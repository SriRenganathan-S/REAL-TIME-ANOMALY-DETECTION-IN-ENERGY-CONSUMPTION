CREATE KEYSPACE IF NOT EXISTS energy_db 
WITH REPLICATION = { 'class' : 'SimpleStrategy', 'replication_factor' : 1 };

USE energy_db;

CREATE TABLE IF NOT EXISTS meter_readings (
    meter_id text,
    timestamp timestamp,
    power_w float,
    anomaly_score float,
    status text,
    voltage_v float,
    current_a float,
    frequency_hz float,
    PRIMARY KEY (meter_id, timestamp)
) WITH CLUSTERING ORDER BY (timestamp DESC);

CREATE TABLE IF NOT EXISTS model_states (
    meter_id text PRIMARY KEY,
    model_checkpoint blob,
    baseline_power float,
    learning_count int,
    last_updated timestamp
);

CREATE TABLE IF NOT EXISTS system_heartbeat (
    processor_id text PRIMARY KEY,
    timestamp timestamp,
    status text,
    last_update timestamp
);