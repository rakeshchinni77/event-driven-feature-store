import json
import time
import uuid
from datetime import datetime, timezone
from confluent_kafka import Producer
import os


KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:29092")
RAW_EVENTS_TOPIC = os.getenv("RAW_EVENTS_TOPIC", "raw-events")


def delivery_report(err, msg):
    if err is not None:
        print(f"Delivery failed: {err}")
    else:
        print(
            f"Delivered to {msg.topic()} "
            f"[partition {msg.partition()}] "
            f"offset {msg.offset()}"
        )


def generate_event():
    return {
        "entity_id": f"user_{uuid.uuid4().hex[:6]}",
        "action": "click",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


def main():
    producer = Producer(
        {
            "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
            "linger.ms": 10,
            "acks": "all",
        }
    )

    print("Kafka Producer Started")
    print(f"Topic: {RAW_EVENTS_TOPIC}")

    try:
        for i in range(5):
            event = generate_event()
            print(f"Producing event {i+1}: {event}")

            producer.produce(
                RAW_EVENTS_TOPIC,
                key=event["entity_id"],
                value=json.dumps(event),
                callback=delivery_report,
            )

            producer.poll(1)
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("Producer interrupted")

    finally:
        print("Flushing producer...")
        producer.flush()
        print("Producer finished cleanly")


if __name__ == "__main__":
    main()
