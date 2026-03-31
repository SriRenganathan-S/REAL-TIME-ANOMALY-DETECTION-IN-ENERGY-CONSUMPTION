-- CASSANDRA SCHEMA - ENERGY ANOMALY DETECTION (Phase 3 - Multi-Meter + Latency)

CREATE KEYSPACE IF NOT EXISTS energy_db 
WITH REPLICATION = { 'class' : 'SimpleStrategy', 'replication_factor' : 1 };

USE energy_db;

-- Main meter readings table with latency tracking
CREATE TABLE IF NOT EXISTS meter_readings (
    meter_id text,
    timestamp timestamp,
    power_w float,
    anomaly_score float,
    status text,
    voltage_v float,
    current_a float,
    frequency_hz float,
    kafka_ingest_time timestamp,
    spark_process_time timestamp,
    cassandra_write_time timestamp,
    latency_ms int,
    risk_level text,
    fault_type text,
    PRIMARY KEY (meter_id, timestamp)
) WITH CLUSTERING ORDER BY (timestamp DESC);

-- Model persistence table (per-meter)
CREATE TABLE IF NOT EXISTS model_states (
    meter_id text PRIMARY KEY,
    model_checkpoint blob,
    baseline_power float,
    learning_count int,
    last_updated timestamp
);

-- System heartbeat for monitoring
CREATE TABLE IF NOT EXISTS system_heartbeat (
    processor_id text PRIMARY KEY,
    timestamp timestamp,
    status text,
    last_update timestamp
);

-- Add missing columns if upgrading from older schema
ALTER TABLE meter_readings ADD IF NOT EXISTS kafka_ingest_time timestamp;
ALTER TABLE meter_readings ADD IF NOT EXISTS spark_process_time timestamp;
ALTER TABLE meter_readings ADD IF NOT EXISTS cassandra_write_time timestamp;
ALTER TABLE meter_readings ADD IF NOT EXISTS latency_ms int;
ALTER TABLE meter_readings ADD IF NOT EXISTS risk_level text;
ALTER TABLE meter_readings ADD IF NOT EXISTS fault_type text;
