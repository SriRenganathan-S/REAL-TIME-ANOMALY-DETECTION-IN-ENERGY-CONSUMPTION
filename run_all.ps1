# =======================================================
# MASTER LAUNCH SCRIPT - REAL-TIME ENERGY ANOMALY PROJECT
# =======================================================

Write-Host "🚀 Booting up Core Backend (Kafka, Cassandra, Grafana)..." -ForegroundColor Cyan
docker-compose up -d

Write-Host "⏳ Waiting 15 seconds for Cassandra DB to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

Write-Host "📡 Launching Hardware Simulator (Meter Data)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit -Command `"cd '$PWD'; set PYTHONIOENCODING=utf-8; python ingestion/multi_meters_simulator.py`""

Write-Host "🧠 Launching Spark AI Brain (Anomaly Detection)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit -Command `"cd '$PWD'; set PYTHONIOENCODING=utf-8; python processing/spark_brain.py`""

Write-Host "🚨 Launching Twilio Alert System..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit -Command `"cd '$PWD'; set PYTHONIOENCODING=utf-8; python monitoring/alert_system.py`""

Write-Host "=======================================================" -ForegroundColor Green
Write-Host "✅ PROJECT FULLY ONLINE AND OPERATIONAL!" -ForegroundColor Green
Write-Host "📊 Dashboards: http://localhost:3000 (admin/admin)" -ForegroundColor Green
Write-Host "=======================================================" -ForegroundColor Green
