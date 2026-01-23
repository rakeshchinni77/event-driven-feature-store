import os
import logging
from typing import Dict
from datetime import datetime

import psycopg2
from psycopg2.extras import RealDictCursor
from tenacity import retry, stop_after_attempt, wait_exponential

from src.models import Feature

# Logger (uses centralized logging_config)
logger = logging.getLogger("db")


class PostgreSQLManager:
    """
    Handles all PostgreSQL interactions for the feature store.
    Provides idempotent writes and safe reads.
    """

    def __init__(self):
        self.host = os.getenv("POSTGRES_HOST")
        self.db = os.getenv("POSTGRES_DB")
        self.user = os.getenv("POSTGRES_USER")
        self.password = os.getenv("POSTGRES_PASSWORD")

        self._connection = None

    # Connection Handling
    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def connect(self):
        """
        Establish a PostgreSQL connection with retries.
        """
        if self._connection is None or self._connection.closed != 0:
            logger.info("Connecting to PostgreSQL feature store")

            self._connection = psycopg2.connect(
                host=self.host,
                dbname=self.db,
                user=self.user,
                password=self.password,
                cursor_factory=RealDictCursor,
            )

            self._connection.autocommit = True
            logger.info("PostgreSQL connection established")

        return self._connection

    # Idempotent Write (UPSERT)
    def upsert_feature(self, feature: Feature) -> None:
        """
        Insert or update a feature in an idempotent way.
        Safe against duplicate Kafka messages.
        """
        conn = self.connect()

        query = """
        INSERT INTO features (entity_id, feature_name, feature_value, timestamp)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (entity_id, feature_name)
        DO UPDATE SET
            feature_value = EXCLUDED.feature_value,
            timestamp = EXCLUDED.timestamp;
        """

        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    query,
                    (
                        feature.entity_id,
                        feature.feature_name,
                        feature.feature_value,
                        feature.timestamp,
                    ),
                )

            logger.info(
                "Feature upserted | entity_id=%s feature=%s",
                feature.entity_id,
                feature.feature_name,
            )

        except Exception:
            logger.exception("Failed to upsert feature into PostgreSQL")
            raise

    # Read Path (API)
    def get_features(self, entity_id: str) -> Dict[str, str]:
        """
        Retrieve all features for a given entity_id.
        Used by FastAPI read endpoint.
        """
        conn = self.connect()

        query = """
        SELECT feature_name, feature_value
        FROM features
        WHERE entity_id = %s;
        """

        try:
            with conn.cursor() as cursor:
                cursor.execute(query, (entity_id,))
                rows = cursor.fetchall()

            logger.info("Features fetched | entity_id=%s", entity_id)

            return {row["feature_name"]: row["feature_value"] for row in rows}

        except Exception:
            logger.exception("Failed to fetch features from PostgreSQL")
            raise

    # Cleanup
    def close(self):
        if self._connection and self._connection.closed == 0:
            logger.info("Closing PostgreSQL connection")
            self._connection.close()
