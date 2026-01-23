from datetime import datetime, timezone
from src.consumer import compute_feature
from src.models import RawEvent


def test_compute_feature_basic():
    event = RawEvent(
        entity_id="user_123",
        action="click",
        timestamp=datetime.now(timezone.utc),
    )

    feature = compute_feature(event)

    assert feature.entity_id == "user_123"
    assert feature.feature_name == "last_action"
    assert feature.feature_value == "click"
    assert feature.timestamp == event.timestamp
