# agent_developmental.py
import json
import google.generativeai as genai

# CONFIG
API_KEY = "YOUR_GEMINI_API_KEY"
LOG_FILE = "monitor_history.json"

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def analyze_development():
    # 1. Load the History
    try:
        with open(LOG_FILE, 'r') as f:
            history_data = f.read()
    except FileNotFoundError:
        print("No logs found.")
        return

    # 2. The Pediatrician Prompt
    prompt = f"""
    SYSTEM ROLE: 
    You are a Developmental Tracking Assistant.
    
    OBJECTIVE:
    Analyze the progress of specific skills (e.g., 'tummy_time', 'sleep_duration') over time.
    
    INSTRUCTIONS:
    1. Ignore environmental data. Focus on 'data' payload and timestamps.
    2. Plot the trajectory: Is the duration/frequency Increasing, Decreasing, or Stagnant?
    3. REGRESSION CHECK: Flag any significant drop in performance compared to previous weeks.
    4. If the data is insufficient to form a trend, state "Insufficient data."
    
    LOG DATA:
    {history_data}
    """

    print("📈 Gemini is calculating developmental trends...")
    response = model.generate_content(prompt)
    print("\n--- DEVELOPMENT REPORT ---")
    print(response.text)

if __name__ == "__main__":
    analyze_development()