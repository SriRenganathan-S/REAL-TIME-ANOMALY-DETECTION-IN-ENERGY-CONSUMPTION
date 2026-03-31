CREATE KEYSPACE IF NOT EXISTS energy_db WITH REPLICATION = { 'class' : 'SimpleStrategy', 'replication_factor' : 1 };

USE energy_db;

ALTER TABLE meter_readings ADD voltage_v float;
ALTER TABLE meter_readings ADD current_a float;
ALTER TABLE meter_readings ADD frequency_hz float;

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
