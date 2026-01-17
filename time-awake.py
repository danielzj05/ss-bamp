from datetime import datetime, timedelta

# 1. INPUT DATA (Last 48h Wake Windows in minutes)
# Example: [120, 130, 110, 125, 115]
wake_windows = [120, 135, 125, 110, 115] 

# 2. SETTINGS
current_wake_time = "07:00"  # Format HH:MM
wind_down_buffer = 20        # Minutes needed to calm down

# 3. CALCULATE TREND
# Weighted average: Give more weight to the most recent 2 windows
recent_weight = 0.7
historic_weight = 0.3

recent_avg = sum(wake_windows[-2:]) / 2
historic_avg = sum(wake_windows[:-2]) / len(wake_windows[:-2])
predicted_window = (recent_avg * recent_weight) + (historic_avg * historic_weight)

# 4. PREDICT CRASH
wake_dt = datetime.strptime(current_wake_time, "%H:%M")
crash_dt = wake_dt + timedelta(minutes=predicted_window)
wind_down_dt = crash_dt - timedelta(minutes=wind_down_buffer)

print(f"--- PREDICTION ---")
print(f"Current Trend (Window): {int(predicted_window)} minutes")
print(f"Predicted Crash Zone:   {crash_dt.strftime('%H:%M')}")
print(f"START WIND DOWN AT:     {wind_down_dt.strftime('%H:%M')}")