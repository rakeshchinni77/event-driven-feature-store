# Event-Driven Feature Store
# Makefile for Developer Workflow

PROJECT_NAME=event-driven-feature-store
SERVICE=feature-client

.PHONY: help build up down restart logs shell producer consumer test clean

help:
	@echo ""
	@echo "Available commands:"
	@echo "  make build      - Build Docker images"
	@echo "  make up         - Start all services"
	@echo "  make down       - Stop all services"
	@echo "  make restart    - Restart services"
	@echo "  make logs       - View service logs"
	@echo "  make shell      - Shell into feature-client container"
	@echo "  make producer   - Run Kafka producer"
	@echo "  make consumer   - Run Kafka consumer"
	@echo "  make test       - Run pytest inside container"
	@echo "  make clean      - Remove containers & volumes"
	@echo ""

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

restart: down up

logs:
	docker-compose logs -f

shell:
	docker-compose exec $(SERVICE) /bin/sh

producer:
	docker-compose exec $(SERVICE) python producer.py

consumer:
	docker-compose exec $(SERVICE) python -c "from src.consumer import start_consumer; start_consumer()"

test:
	docker-compose exec $(SERVICE) pytest

clean:
	docker-compose down -v
