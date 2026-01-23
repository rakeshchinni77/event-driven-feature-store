import json
import logging
import os
import time

from confluent_kafka import Consumer, KafkaException, KafkaError

from src.models import RawEvent, Feature
from src.db_manager import PostgreSQLManager

# Logger (uses centralized logging_config)
logger = logging.getLogger("consumer")

# Configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:29092")
RAW_EVENTS_TOPIC = os.getenv("RAW_EVENTS_TOPIC", "raw-events")
KAFKA_GROUP_ID = os.getenv("KAFKA_GROUP_ID", "feature-store-consumer")


# Feature Engineering Logic
def compute_feature(event: RawEvent) -> Feature:
    """
    Deterministic feature computation.
    Safe for reprocessing (idempotent).
    """
    return Feature(
        entity_id=event.entity_id,
        feature_name="last_action",
        feature_value=event.action,
        timestamp=event.timestamp,
    )


# Kafka Consumer Factory
def create_consumer() -> Consumer:
    """
    Create Kafka consumer with retry.
    Prevents API crash if topic is not ready yet.
    """
    consumer_conf = {
        "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
        "group.id": KAFKA_GROUP_ID,
        "auto.offset.reset": "earliest",
        "enable.auto.commit": False,  # offset safety
    }

    while True:
        try:
            logger.info("Attempting to connect to Kafka...")
            consumer = Consumer(consumer_conf)
            consumer.subscribe([RAW_EVENTS_TOPIC])
            logger.info("Kafka consumer connected successfully")
            return consumer
        except KafkaException as e:
            logger.warning(f"Kafka not ready yet: {e}")
            time.sleep(5)


# Kafka Consumer Loop
def start_consumer() -> None:
    logger.info("Starting Kafka consumer")
    logger.info(f"Bootstrap servers: {KAFKA_BOOTSTRAP_SERVERS}")
    logger.info(f"Topic: {RAW_EVENTS_TOPIC}")
    logger.info(f"Group ID: {KAFKA_GROUP_ID}")

    consumer = create_consumer()
    db = PostgreSQLManager()

    try:
        while True:
            msg = consumer.poll(timeout=1.0)

            if msg is None:
                continue

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                logger.error(f"Kafka error: {msg.error()}")
                continue

            try:
                payload = json.loads(msg.value().decode("utf-8"))
                logger.info(
                    f"Consumed message | partition={msg.partition()} "
                    f"offset={msg.offset()}"
                )

                # 1. Validate raw event
                raw_event = RawEvent(**payload)

                # 2. Compute feature
                feature = compute_feature(raw_event)

                # 3. Persist feature (idempotent UPSERT)
                db.upsert_feature(feature)

                # 4. Commit offset ONLY after success
                consumer.commit(message=msg)
                logger.info("Offset committed successfully")

            except Exception:
                logger.exception(
                    "Error while processing message. Offset NOT committed."
                )
                time.sleep(1)

    except KeyboardInterrupt:
        logger.info("Kafka consumer interrupted (shutdown requested)")

    finally:
        logger.info("Closing Kafka consumer")
        consumer.close()
        db.close()


# Optional standalone run (debug / local)
if __name__ == "__main__":
    start_consumer()
