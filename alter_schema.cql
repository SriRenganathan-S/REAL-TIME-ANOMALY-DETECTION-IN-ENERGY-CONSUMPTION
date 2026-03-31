ALTER TABLE energy_db.meter_readings ADD IF NOT EXISTS risk_level text;
ALTER TABLE energy_db.meter_readings ADD IF NOT EXISTS fault_type text;
ALTER TABLE energy_db.meter_readings ADD IF NOT EXISTS kafka_ingest_time timestamp;
ALTER TABLE energy_db.meter_readings ADD IF NOT EXISTS spark_process_time timestamp;
ALTER TABLE energy_db.meter_readings ADD IF NOT EXISTS cassandra_write_time timestamp;
ALTER TABLE energy_db.meter_readings ADD IF NOT EXISTS latency_ms int;
