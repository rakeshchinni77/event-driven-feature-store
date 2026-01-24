#!/bin/sh
set -e

echo "Waiting for PostgreSQL to be ready..."
while ! nc -z "$POSTGRES_HOST" 5432; do
  sleep 1
done
echo "PostgreSQL is ready"

echo "Waiting for Kafka to be ready..."
while ! nc -z kafka 29092; do
  sleep 1
done
echo "Kafka is ready"

echo "Starting Feature Store Service..."
exec python -m src
