import os
from flask import Flask, render_template, session, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_qrcode import QRcode

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'

bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class OrderAmount(FlaskForm):
    burger = StringField('Burger Quantity', validators=[DataRequired()])
    fries = StringField('Fries Quantity', validators=[DataRequired()])
    submit = SubmitField('Add to Cart')


class Cart():
    # TODO: init menu items from a database query instead of hard coded values
    def __init__(self):
        self.burger_total = round(int(session.get('burger_quantity', 0)) * 9.99, 2)
        self.fries_total = round(int(session.get('fries_quantity', 0)) * 5.99, 2)
        self.tax = round((self.burger_total + self.fries_total) * .06, 2)
        self.check = round((self.burger_total + self.fries_total), 2)

    def reset(self):
        self.burger_total = self.fries_total = self.tax = self.check = 0


class CheckOut(FlaskForm):
    submit = SubmitField('Checkout')


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
    else:
        # TODO: find a better way to handle empty cart, perhaps flash warning
        session['burger_quantity'] = session['fries_quantity'] = 0

    if checkout.is_submitted():
        # TODO: insert record into DB
        print('button pressed')
        # TODO: the argument for qrcode() could maybe be the sql insert statement
        qrcode = QRcode.qrcode("put order details here")

    return render_template('cart.html', check=_cart, form=checkout, qrcode=qrcode)


if __name__ == '__main__':
    app.run(debug=True)
