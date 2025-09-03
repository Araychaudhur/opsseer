CREATE TABLE timeline (
    id SERIAL PRIMARY KEY,
    incident_id VARCHAR(255) NOT NULL,
    event_ts TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    type VARCHAR(50) NOT NULL,
    payload JSONB
);