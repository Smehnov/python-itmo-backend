#!/bin/bash

# Wait for Kafka to be ready
echo "Waiting for Kafka..."
max_retries=30
count=0

while ! nc -z kafka 29092; do
    count=$((count + 1))
    if [ $count -eq $max_retries ]; then
        echo "Failed to connect to Kafka after $max_retries attempts."
        exit 1
    fi
    echo "Waiting for Kafka... ($count/$max_retries)"
    sleep 2
done

echo "Kafka is ready!"

# Wait for the API to be ready (it creates the database schema)
echo "Waiting for API..."
count=0
while ! curl -s http://api:8000 > /dev/null; do
    count=$((count + 1))
    if [ $count -eq $max_retries ]; then
        echo "Failed to connect to API after $max_retries attempts."
        exit 1
    fi
    echo "Waiting for API... ($count/$max_retries)"
    sleep 2
done

echo "API is ready!"

# Set up Kafka topic
echo "Setting up Kafka topic..."
python scripts/setup_kafka.py

# Start the consumer
echo "Starting consumer..."
exec python -m consumer.kafka_consumer 