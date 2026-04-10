# ⚡ Real-Time Anomaly Detection in Energy Consumption
**Final Project Report & Run Guide**

---

## 📊 Project Overview
This project is an enterprise-grade, highly scalable Big Data pipeline designed to monitor industrial and residential energy consumption in real-time. It uses **Machine Learning (River ML)** to dynamically learn the "normal" behavioral patterns of different facilities and automatically detect electrical anomalies, short circuits, or massive energy overloads before they cause catastrophic hardware failure.

### The Technology Stack:
* **Message Broker:** Apache Kafka (Handles thousands of high-velocity telemetry events).
* **AI Processing Engine:** PySpark Structured Streaming (Runs the "Spark Brain").
* **Machine Learning:** River ML (Online unsupervised learning via Half-Space Trees).
* **High-Speed Database:** Apache Cassandra (Saves logs and model checkpoints).
* **Visualization:** Grafana (Beautiful, real-time reactive dashboards).
* **Alerting:** Twilio API (Instant SMS and Voice Call dispatching).

---

## 🏗️ Architecture Flow
1. **Data Generation:** `multi_meters_simulator.py` simulates live smart-meter hardware across 5 completely different facilities (Apartments, Malls, Textile Mills, etc). It shoots voltage, current, frequency, and wattage data directly into Kafka.
2. **AI Stream Processing:** `spark_brain.py` catches the raw data. It feeds the data through a Machine Learning model specifically dedicated to that unique meter. The model dynamically evaluates the data against its memory and assigns an **Anomaly Score (0.0 to 1.0)**.
3. **Storage:** The raw metrics and the AI anomaly score are saved persistently into Cassandra for historical audits.
4. **Dashboarding:** Grafana constantly queries Cassandra to update the UI visuals immediately.
5. **Alerting System:** `alert_system.py` watches the AI stream. If an anomaly crosses `0.70`, it fires an SMS. If it crosses `0.85`, it instantly dials the operator's phone through Twilio.

---

## 🚀 How to Run the Project (Step-by-Step)

If you ever restart your computer or stop the project, follow this exact sequence to bring the entire facility online:

### Step 1: Boot Up the Core Infrastructure
Ensure **Docker Desktop** is open and running on your Windows machine.
1. Open a terminal in your project directory.
2. Run the following command to start Cassandra, Kafka, Zookeeper, and Grafana:
   ```bash
   docker-compose up -d
   ```
3. Wait 15 seconds to ensure Cassandra fully initializes.

### Step 2: Start the Sensors (Data Ingestion)
1. Open a new terminal.
2. Start the telemetry hardware simulator:
   ```bash
   python ingestion/multi_meters_simulator.py
   ```
   *(Leave this window open. You will instantly see green output showing wattage flowing).*

### Step 3: Activate the AI (Spark Brain)
1. Open a new terminal.
2. Fire up the Machine Learning processor:
   ```bash
   python processing/spark_brain.py
   ```
   *(Leave this window open. You will see it switch from "🎓 Learning" mode to actively scoring anomalies).*

### Step 4: Turn on the Alert Sirens
1. Open a new terminal.
2. Start the Twilio alarm system:
   ```bash
   python monitoring/alert_system.py
   ```
   *(Leave this window open. It will print alerts when anomalies happen).*

### Step 5: Open the Dashboards
1. Open your web browser and navigate to: [http://localhost:3000](http://localhost:3000)
2. Log in with `admin` / `admin`.
3. Open any of your custom Dashboards (like the Shopping Mall or Industrial Factory) to watch the live data streams and anomaly gauges react!

---

## ⚠️ Troubleshooting Twilio Calls
If your terminal detects an anomaly but your physical phone does not ring, it is **100% caused by a Twilio Free-Trial restriction**. Here is how to fix it:
1. Since you are on a Twilio trial, you **MUST** verify your cellphone number in their dashboard before they will let you text it to prevent spam.
2. Open your Twilio Browser dashboard.
3. Go to **Phone Numbers ➔ Manage ➔ Verified Caller IDs**.
4. Register your personal cellphone (`+91...`).
5. Ensure the `TWILIO_PHONE` variable in `alert_system.py` matches your active Twilio phone number.
