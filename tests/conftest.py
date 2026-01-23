import pytest


@pytest.fixture(autouse=True)
def set_test_env(monkeypatch):
    """
    Force safe test-only environment variables.
    Prevents accidental real DB / Kafka usage.
    """
    monkeypatch.setenv("POSTGRES_HOST", "test-db")
    monkeypatch.setenv("POSTGRES_DB", "test_db")
    monkeypatch.setenv("POSTGRES_USER", "test_user")
    monkeypatch.setenv("POSTGRES_PASSWORD", "test_password")

    monkeypatch.setenv("KAFKA_BOOTSTRAP_SERVERS", "test-kafka:9092")
    monkeypatch.setenv("RAW_EVENTS_TOPIC", "test-topic")
    monkeypatch.setenv("KAFKA_GROUP_ID", "test-group")

    yield
