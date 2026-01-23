import logging
import threading
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException

from src.logging_config import setup_logging
from src.consumer import start_consumer
from src.db_manager import PostgreSQLManager
from src.models import FeatureResponse

setup_logging()
logger = logging.getLogger("api")

app = FastAPI(title="Event-Driven Feature Store")

db = PostgreSQLManager()


@app.on_event("startup")
def startup_event():
    logger.info("Starting Feature Store API")

    consumer_thread = threading.Thread(
        target=start_consumer,
        daemon=True,
    )
    consumer_thread.start()

    logger.info("Kafka consumer started in background thread")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/features/{entity_id}", response_model=FeatureResponse)
def get_features(entity_id: str):
    try:
        features = db.get_features(entity_id)

        if not features:
            raise HTTPException(
                status_code=404,
                detail=f"No features found for entity_id={entity_id}",
            )

        return FeatureResponse(
            entity_id=entity_id,
            features=features,
            last_updated=datetime.now(timezone.utc),
        )

    except HTTPException:
        raise
    except Exception:
        logger.exception("Failed to fetch features")
        raise HTTPException(status_code=500, detail="Internal server error")
