-- =====================================================
-- Feature Store Schema
-- =====================================================

CREATE TABLE IF NOT EXISTS features (
    entity_id VARCHAR(255) NOT NULL,
    feature_name VARCHAR(255) NOT NULL,
    feature_value TEXT NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (entity_id, feature_name)
);

-- Index for fast feature retrieval by entity
CREATE INDEX IF NOT EXISTS idx_entity_id
ON features (entity_id);
