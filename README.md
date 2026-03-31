# Real-Time Anomaly Detection in Energy Consumption

A distributed system for detecting anomalies in smart meter energy consumption using Kafka, Cassandra, and adaptive ML models.

## Architecture

- **Ingestion**: Smart meter data producer (`smart_meter.py`)
- **Processing**: Real-time anomaly detection with River ML (`adaptive_brain.py`, `spark_brain.py`)
- **Storage**: Cassandra time-series database
- **Monitoring**: Grafana dashboard
- **Messaging**: Apache Kafka for streaming

## Quick Start

```bash
docker-compose up -d
pip install -r [requirements.txt](http://_vscodecontentref_/6)
python [smart_meter.py](http://_vscodecontentref_/7) &
python [adaptive_brain.py](http://_vscodecontentref_/8)