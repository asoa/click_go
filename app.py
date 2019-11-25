import os
import boto3
import json
import decimal
from flask import Flask, render_template, session, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_qrcode import QRcode

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000")
bootstrap = Bootstrap(app)


class OrderAmount(FlaskForm):
    burger = IntegerField('Burger Quantity', validators=[DataRequired()])
    fries = IntegerField('Fries Quantity', validators=[DataRequired()])
    submit = SubmitField('Add to Cart')


class Cart:
    """ inits the cart with session values """
    # TODO: init menu items from a database query instead of hard coded values
    def __init__(self):
        self.burger_total = round(session.get('burger_quantity', 0) * 9.99, 2)
        self.fries_total = round(session.get('fries_quantity', 0) * 5.99, 2)
        self.tax = round((self.burger_total + self.fries_total) * .06, 2)
        self.check = round((self.burger_total + self.fries_total + self.tax), 2)

    def reset(self):
        self.burger_total = self.fries_total = self.tax = self.check = 0


class CheckOut(FlaskForm):
    """ Checkout button in cart """
    submit = SubmitField('Checkout')


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if abs(o) % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)


class DB:
    def __init__(self, **kwargs):
        self.kwargs = {k: v for k, v in kwargs.items()}
        # dynamodb = boto3.resource('dynamodb', region_name='us-east-2', endpoint_url="http://localhost:8000")
        self.check = self.kwargs.get('check')
        self.table = dynamodb.Table('clickgo')


    def write(self):
        response = self.table.put_item(
            Item={
                'uid': session.get('csrf_token'),
                'burger_quantity': session.get('burger_quantity'),
                'fries_quantity': session.get('fries_quantity'),
                'amount_due': decimal.Decimal(str(self.check))
            }
        )

        print("PutItem succeeded:")
        print(json.dumps(response, indent=4, cls=DecimalEncoder))


@app.route('/', methods=['GET', 'POST'])
def index():
    form = OrderAmount()
    if form.validate_on_submit():
        session['burger_quantity'] = form.burger.data
        session['fries_quantity'] = form.fries.data
        form.burger.data = form.fries.data = 0

    return render_template('menu.html', form=form)


@app.route('/cart', methods=['GET', 'POST'])
def cart():
    qrcode = None
    _cart = None
    checkout = CheckOut()
    # check to see if the cart has items in it
    if session.get('burger_quantity', None) or session.get('fries_quantity', None) is not None:
        _cart = Cart()  # init the cart with items from the session

        if checkout.is_submitted():
            # TODO: insert record into DB
            db = DB(check=_cart.check).write()
            print(session)
            # TODO: the argument for qrcode() could maybe be the sql insert statement
            qrcode = QRcode.qrcode(session.get('csrf_token'))

    else:
        # TODO: find a better way to handle empty cart, perhaps flash warning
        session['burger_quantity'] = session['fries_quantity'] = 0

    return render_template('cart.html', check=_cart, form=checkout, qrcode=qrcode)


if __name__ == '__main__':
    app.run(debug=True)
