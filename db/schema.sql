-- Schema bootstrap for housing project

CREATE SCHEMA IF NOT EXISTS ingest;
CREATE SCHEMA IF NOT EXISTS curated;

CREATE TABLE IF NOT EXISTS ingest.raw_files (
    id              BIGSERIAL PRIMARY KEY,
    locality        TEXT        NOT NULL,
    source_name     TEXT        NOT NULL,
    source_path     TEXT,
    file_hash       TEXT,
    row_count       INTEGER,
    loaded_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    notes           TEXT
);

CREATE TABLE IF NOT EXISTS ingest.raw_properties (
    locality        TEXT        NOT NULL,
    property_id     TEXT        NOT NULL,
    payload         JSONB       NOT NULL,
    source_file_id  BIGINT      REFERENCES ingest.raw_files(id) ON DELETE SET NULL,
    ingested_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY(locality, property_id)
);

CREATE TABLE IF NOT EXISTS curated.properties (
    locality        TEXT        NOT NULL,
    property_id     TEXT        NOT NULL,
    address         JSONB       NOT NULL,
    property_type   TEXT,
    bedrooms        INTEGER,
    bathrooms       NUMERIC,
    square_feet     NUMERIC,
    lot_size        NUMERIC,
    year_built      INTEGER,
    assessor_id     TEXT,
    zoning          TEXT,
    owner_payload   JSONB,
    taxes_payload   JSONB,
    derived         JSONB,
    source_file_id  BIGINT      REFERENCES ingest.raw_files(id) ON DELETE SET NULL,
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY(locality, property_id)
);

CREATE INDEX IF NOT EXISTS idx_curated_properties_type ON curated.properties(property_type);
CREATE INDEX IF NOT EXISTS idx_curated_properties_year ON curated.properties(year_built);
