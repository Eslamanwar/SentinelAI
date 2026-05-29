import json
import logging
from datetime import datetime, timezone
from typing import Any, Optional

from confluent_kafka import Consumer, KafkaError, Producer

from config import settings

logger = logging.getLogger(__name__)

TOPICS = [
    "threat.discovered",
    "threat.correlated",
    "risk.scored",
    "remediation.generated",
    "alert.dispatched",
]


class EventBus:
    def __init__(self):
        self._producer: Optional[Producer] = None
        self._consumer: Optional[Consumer] = None

    async def start(self):
        try:
            self._producer = Producer(
                {"bootstrap.servers": settings.kafka_bootstrap_servers}
            )
            logger.info("Kafka producer connected")
        except Exception as e:
            logger.warning(f"Kafka not available, running without event bus: {e}")
            self._producer = None

    async def stop(self):
        if self._producer:
            self._producer.flush(timeout=5)

    def publish(self, topic: str, event: dict[str, Any]):
        if not self._producer:
            logger.debug(f"Event bus offline, skipping publish to {topic}")
            return

        event["timestamp"] = datetime.now(timezone.utc).isoformat()
        event["topic"] = topic

        try:
            self._producer.produce(
                topic,
                key=event.get("investigation_id", ""),
                value=json.dumps(event, default=str),
                callback=self._delivery_callback,
            )
            self._producer.poll(0)
        except Exception as e:
            logger.error(f"Failed to publish to {topic}: {e}")

    @staticmethod
    def _delivery_callback(err, msg):
        if err:
            logger.error(f"Kafka delivery failed: {err}")

    def publish_threat_discovered(self, investigation_id: str, threat: dict):
        self.publish("threat.discovered", {
            "investigation_id": investigation_id,
            "threat": threat,
        })

    def publish_threat_correlated(self, investigation_id: str, correlation: dict):
        self.publish("threat.correlated", {
            "investigation_id": investigation_id,
            "correlation": correlation,
        })

    def publish_risk_scored(self, investigation_id: str, risk: dict):
        self.publish("risk.scored", {
            "investigation_id": investigation_id,
            "risk": risk,
        })

    def publish_remediation_generated(self, investigation_id: str, plan: dict):
        self.publish("remediation.generated", {
            "investigation_id": investigation_id,
            "plan": plan,
        })

    def publish_alert_dispatched(self, investigation_id: str, alert: dict):
        self.publish("alert.dispatched", {
            "investigation_id": investigation_id,
            "alert": alert,
        })
