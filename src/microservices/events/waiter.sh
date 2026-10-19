#!/bin/sh

while ! nc -z -v $KAFKA_HOST $KAFKA_PORT;
do
  echo "Cannot connect to Kafka."
  sleep $KAFKA_WAIT_TIMEOUT;
done