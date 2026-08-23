from typing import Any

from backend.utils.kafka import KafkaProducerService


class KafkaBookingEventPublisher:
    """
    Publishes booking-related events to Kafka.
    """

    def __init__(
        self,
        kafka_producer: KafkaProducerService,
    ):
        self.kafka_producer = kafka_producer

    def publish_booking_created(
        self,
        booking: Any,
    ) -> None:
        message = {
            "event": "booking_created",
            "booking_id": str(booking.id),
            "flight_order_id": booking.flight_order_id,
            "status": booking.status,
        }

        self.kafka_producer.publish(
            topic="flight-bookings",
            key=str(booking.id),
            message=message,
        )
