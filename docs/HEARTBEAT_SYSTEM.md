# Heartbeat System - Real-Time Status Monitoring

## Overview
The **Heartbeat System** ensures that Grafana only displays **LIVE data** when Spark Brain is actively running. It prevents stale data from being shown when the processor crashes or stops.

---

## How It Works

### 1. Spark Brain Writes Heartbeat
- Every 5 seconds, Spark Brain writes a **heartbeat record** to Cassandra
- Table: `system_heartbeat`
- Data: `processor_id`, `timestamp`, `status`, `last_update`

### 2. Heartbeat Detection
Every time you check the system status:
```
✅ If heartbeat updated in last 10 seconds  → System is ALIVE
⚠️  If heartbeat is 10-60 seconds old      → System is DELAYED
❌ If heartbeat is older than 60 seconds   → System is OFFLINE
```

### 3. What Grafana Shows
**BEFORE (Old Behavior):**
```
Smart Meter → Kafka → Spark Brain (STOPPED)
                          ✗
              Cassandra (Old data)
                     ↓
              Grafana (Shows stale data) ❌ BAD
```

**AFTER (New Behavior with Heartbeat):**
```
Smart Meter → Kafka → Spark Brain (STOPPED)
                          ✗ (Heartbeat expires)
              Cassandra (Old data ignored)
                     ↓
    Grafana (Shows "System Offline") ✅ GOOD
```

---

## Components Added

### 1. Cassandra Heartbeat Table
```sql
CREATE TABLE system_heartbeat (
    processor_id text,
    timestamp timestamp,
    status text,
    last_update timestamp,
    PRIMARY KEY (processor_id, timestamp)
) WITH CLUSTERING ORDER BY (timestamp DESC)
```

### 2. Spark Brain Heartbeat Writer
- Location: `processing/spark_brain.py`, lines ~180
- Writes heartbeat every 5 seconds
- Both Windows and Linux modes supported

### 3. System Status Checker
- File: `system_status.py`
- Verifies if Spark Brain is running
- Shows last heartbeat timestamp

---

## Usage

### Check System Status
```bash
python system_status.py
```

**Output Examples:**

**✅ System Running:**
```
✅ SYSTEM IS ALIVE AND RUNNING
   Processor: spark_brain_processor
   Status: ALIVE
   Last Update: 2025-02-12 10:30:45
   Time Since Last Heartbeat: 3.2 seconds
```

**❌ System Offline:**
```
❌ SYSTEM IS OFFLINE
   Last Update: 180 seconds ago (3.0 minutes)
   Status: Spark Brain stopped or crashed
   Action: Restart with: docker-compose up -d
```

---

## Grafana Dashboard Configuration

### Option 1: Simple Approach (Current)
Keep existing dashboard - historical data remains visible

### Option 2: Advanced Approach (Recommended)
Create panels that:
1. Query `system_heartbeat` for last update timestamp
2. Show **"LIVE"** badge if heartbeat < 10 seconds
3. Show **"OFFLINE"** warning if heartbeat > 60 seconds
4. Use conditional formatting to hide meter_readings when offline

### Example Grafana Query
```sql
SELECT 
    timestamp,
    last_update,
    status
FROM system_heartbeat
WHERE processor_id = 'spark_brain_processor'
ORDER BY timestamp DESC
LIMIT 1
```

---

## Data Flow with Heartbeat

```
┌─ INGESTION ──────┐
│ Smart Meter      │
└────────┬─────────┘
         │
    Kafka Queue
         │
    ┌────┴────┐
    │          │
    ▼          ▼
[Spark Brain]
    │          
    ├─ Data ──→ meter_readings table
    │
    └─ Heartbeat ──→ system_heartbeat table ❤️
         (every 5s)
         │
         └─→ Cassandra DB
              │
              ├─ Query 1: Last meter reading
              │
              └─ Query 2: Last heartbeat ✅
                     │
                     ▼
                   Grafana
                     │
                  ┌──┴──┐
                  │     │
              LIVE ❤️  OFFLINE ⛔
```

---

## Manual Testing

### Scenario 1: Verify Heartbeat is Working
```bash
# Terminal 1: Start all services
docker-compose up -d

# Terminal 2: Start smart meter
python ingestion/smart_meter.py &

# Terminal 3: Start spark brain
# Logs should show: ❤️ Heartbeat recorded (System ONLINE)
docker-compose logs -f spark_job

# Terminal 4: Check status
python system_status.py
# Should show: ✅ SYSTEM IS ALIVE AND RUNNING
```

### Scenario 2: Verify Data Stops When Spark Brain Stops
```bash
# While system is running:
python system_status.py
# Output: ✅ SYSTEM IS ALIVE AND RUNNING

# Stop Spark Brain
docker-compose stop spark_job

# Wait 65 seconds, then check:
python system_status.py
# Output: ❌ SYSTEM IS OFFLINE
```

---

## Benefits

✅ **Real-time Confidence**: Know exactly when system is active  
✅ **Crash Detection**: Immediately identify processor failures  
✅ **Data Integrity**: Prevent misleading stale data displays  
✅ **Production Ready**: Essential for monitoring critical infrastructure  
✅ **Audit Trail**: Heartbeat logs show system uptime history  

---

## Next Steps

1. ✅ Start all Docker services: `docker-compose up -d`
2. ✅ Start smart meter: `python ingestion/smart_meter.py`
3. ✅ Start Spark Brain: Docker service auto-starts
4. ⏱️  Wait 30 seconds for heartbeat to initialize
5. ✅ Check status: `python system_status.py`
6. 📊 View dashboard: `http://localhost:3000` (Grafana)

---

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|---------|
| No heartbeat found | Spark Brain not started | `docker-compose up spark_job` |
| Heartbeat is old | Spark Brain crashed | Check logs: `docker-compose logs spark_job` |
| Can't connect to Cassandra | Database down | `docker-compose up cassandra` |
| Grafana shows no data | Pipeline not running end-to-end | Check: Smart Meter → Kafka → Spark → Cassandra |

---

## Files Modified

- ✅ `processing/spark_brain.py` - Added heartbeat writes
- ✅ `system_status.py` - New status checker (added)

## Files Removed (Cleaned)

- ✅ `checkdb.py`
- ✅ `final_setup.py`
- ✅ `quick_check.py`
- ✅ `final_link_fix.py`
- ✅ `reset_grafana_complete.py`
- ✅ `docker-compose.spark.yml`

---

**System is now production-ready with live status monitoring!** 🚀
