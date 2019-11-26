#!/usr/bin/env zsh

aws dynamodb create-table \
  --table-name clickgo \
  --attribute-definitions \
      AttributeName=uid,AttributeType=S \
  --key-schema AttributeName=uid,KeyType=HASH \
  --provisioned-throughput ReadCapacityUnits=1,WriteCapacityUnits=1 \
#  --endpoint-url http://localhost:8000