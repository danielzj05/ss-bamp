# logger.py
import json
import os
from datetime import datetime

LOG_FILE = "monitor_history.json"

class MonitorLogger:
    def __init__(self, filename=LOG_FILE):
        self.filename = filename
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        if not os.path.exists(self.filename):
            with open(self.filename, 'w') as f:
                json.dump([], f)

    def log_event(self, event_type, data_payload, environment_context):
        """
        Args:
            event_type (str): e.g., "distress", "sleep", "tummy_time"
            data_payload (dict): Specifics (e.g., {"duration": 10, "intensity": "high"})
            environment_context (dict): Sensor data (e.g., {"temp": 22, "noise": "loud"})
        """
        new_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_id": f"evt_{int(datetime.now().timestamp())}",
            "type": event_type,
            "data": data_payload,
            "environment": environment_context
        }

        # Read, Append, Write (in production, use a proper DB like SQLite)
        with open(self.filename, 'r+') as f:
            try:
                logs = json.load(f)
            except json.JSONDecodeError:
                logs = []
            
            logs.append(new_entry)
            f.seek(0)
            json.dump(logs, f, indent=2)
            
        print(f"✅ Logged event: {event_type}")

# --- OPTIONAL: TEST DATA GENERATOR ---
# Run this ONLY if you need to populate the file for testing the agents below.
if __name__ == "__main__":
    print("Populating with test data for demonstration...")
    logger = MonitorLogger()
    
    # Simulating 3 real logs
    logger.log_event("sleep", {"duration_min": 45}, {"temp": 22})
    logger.log_event("distress", {"visual": "crying"}, {"temp": 28}) # Heat spike
    logger.log_event("tummy_time", {"duration_min": 2}, {"temp": 22}) # Regression