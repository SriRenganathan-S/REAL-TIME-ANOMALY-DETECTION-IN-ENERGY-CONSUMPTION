FROM python:3.11-slim-bookworm

ENV SPARK_HOME=/opt/spark
ENV PATH=$SPARK_HOME/bin:$PATH
ENV PYSPARK_PYTHON=python
ENV PYSPARK_DRIVER_PYTHON=python

# 1. System Tools & Java (STAY CACHED)
RUN apt-get update && apt-get install -y --no-install-recommends \
    openjdk-17-jre-headless wget tar ca-certificates curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# 2. Python Libraries (STAY CACHED)
RUN pip install --no-cache-dir \
    pyspark==3.5.0 river kafka-python cassandra-driver twilio numpy==1.26.4

# 3. DOWNLOAD APACHE SPARK 3.5.0
WORKDIR /opt
RUN wget -q https://archive.apache.org/dist/spark/spark-3.5.0/spark-3.5.0-bin-hadoop3.tgz && \
    tar -xzf spark-3.5.0-bin-hadoop3.tgz && \
    mv spark-3.5.0-bin-hadoop3 spark && \
    rm spark-3.5.0-bin-hadoop3.tgz && \
    echo "✅ Spark 3.5.0 installed at /opt/spark"

WORKDIR /app
COPY . /app

# Run the Original Spark Engine
CMD ["spark-submit", \
     "--master", "local[*]", \
     "--packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,com.datastax.spark:spark-cassandra-connector_2.12:3.4.0", \
     "processing/spark_brain.py"]