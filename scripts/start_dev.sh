#!/bin/bash

# Start Kafka and PostgreSQL
echo "Starting infrastructure..."
docker compose up -d db kafka

# Wait for Kafka to be ready
echo "Waiting for Kafka to be ready..."
sleep 10

# Set up Kafka topic
echo "Setting up Kafka topic..."
poetry run python scripts/setup_kafka.py

# Start consumer in background
echo "Starting consumer..."
poetry run python -m consumer.kafka_consumer &

# Start API
echo "Starting API..."
poetry run uvicorn src.app.api.main:app --reload 