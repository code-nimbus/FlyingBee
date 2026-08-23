from kafka import KafkaProducer
import json
import os
from typing import Any

from dotenv import load_dotenv

load_dotenv()


class KafkaProducerService:
    def __init__(self):
        bootstrap_servers = os.getenv(
            "KAFKA_BOOTSTRAP_SERVERS",
            "localhost:9092",
        )

        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers.split(","),
            value_serializer=lambda value: json.dumps(value).encode("utf-8"),
            key_serializer=lambda key: (key.encode("utf-8") if key else None),
            acks="all",
            retries=5,
            enable_idempotence=True,
        )

    def publish(
        self,
        topic: str,
        message: dict[str, Any],
        key: str | None = None,
    ) -> None:
        """
        Publish an event to Kafka.
        """

        future = self.producer.send(
            topic,
            key=key,
            value=message,
        )

        # Wait for Kafka acknowledgement.
        future.get(timeout=10)

    def close(self) -> None:
        self.producer.flush()
        self.producer.close()


# kafka_producer = KafkaProducerService()
