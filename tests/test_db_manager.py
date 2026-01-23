import os
import logging
from typing import Dict
from datetime import datetime

import psycopg2
from psycopg2.extras import RealDictCursor
from tenacity import retry, stop_after_attempt, wait_exponential

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

    # Connection Handling (with retry)
    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def connect(self):
        if self._connection is None or self._connection.closed != 0:
            logger.info("Connecting to PostgreSQL")
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

    # Public API expected by TESTS
    def save_feature(
        self,
        entity_id: str,
        feature_name: str,
        feature_value: str,
        timestamp: datetime,
    ) -> None:
        """
        Public write API (required by tests).
        Delegates to idempotent upsert_feature().
        """
        self.upsert_feature(
            entity_id=entity_id,
            feature_name=feature_name,
            feature_value=feature_value,
            timestamp=timestamp,
        )

    # Internal Idempotent Write
    def upsert_feature(
        self,
        entity_id: str,
        feature_name: str,
        feature_value: str,
        timestamp: datetime,
    ) -> None:
        conn = self.connect()

        query = """
        INSERT INTO features (entity_id, feature_name, feature_value, timestamp)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (entity_id, feature_name)
        DO UPDATE SET
            feature_value = EXCLUDED.feature_value,
            timestamp = EXCLUDED.timestamp;
        """

        with conn.cursor() as cursor:
            cursor.execute(
                query,
                (entity_id, feature_name, feature_value, timestamp),
            )

        logger.info(
            "Feature upserted | entity_id=%s feature=%s",
            entity_id,
            feature_name,
        )

    # Read Path
    def get_features(self, entity_id: str) -> Dict[str, str]:
        conn = self.connect()

        query = """
        SELECT feature_name, feature_value
        FROM features
        WHERE entity_id = %s;
        """

        with conn.cursor() as cursor:
            cursor.execute(query, (entity_id,))
            rows = cursor.fetchall()

        return {row["feature_name"]: row["feature_value"] for row in rows}

    # Cleanup
    def close(self):
        if self._connection and self._connection.closed == 0:
            self._connection.close()
            logger.info("PostgreSQL connection closed")
