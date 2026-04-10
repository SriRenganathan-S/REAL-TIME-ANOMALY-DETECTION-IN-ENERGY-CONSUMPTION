from cassandra.cluster import Cluster
c = Cluster(['127.0.0.1'])
s = c.connect('energy_db')
rows = s.execute("SELECT timestamp, voltage_v, fault_type FROM meter_readings WHERE meter_id='auto_factory_001' ORDER BY timestamp DESC LIMIT 5")
print([(str(r.timestamp), r.voltage_v, r.fault_type) for r in rows])
