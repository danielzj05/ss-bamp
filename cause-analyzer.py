# agent_root_cause.py
import json
import google.generativeai as genai

# CONFIG
API_KEY = "YOUR_GEMINI_API_KEY"
LOG_FILE = "monitor_history.json"

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def analyze_root_cause():
    # 1. Load the History
    try:
        with open(LOG_FILE, 'r') as f:
            history_data = f.read()
    except FileNotFoundError:
        print("No logs found. Run logger.py first.")
        return

    # 2. The Detective Prompt
    prompt = f"""
    SYSTEM ROLE: 
    You are an expert Pattern Recognition Analyst for a biometric monitoring system.
    
    OBJECTIVE:
    Analyze the provided logs to find the Root Cause of 'distress' or 'anxiety' events.
    
    INSTRUCTIONS:
    1. Filter for all events tagged 'distress' or 'crying'.
    2. Cross-reference these events with the 'environment' data (temperature, noise, time of day).
    3. Identify patterns. (e.g., "Distress always happens when Temp > 26C").
    4. You MUST cite the specific 'event_id' for every claim.
    
    LOG DATA:
    {history_data}
    """

    print("🕵️‍♀️ Gemini is analyzing environment correlations...")
    response = model.generate_content(prompt)
    print("\n--- ANALYSIS RESULT ---")
    print(response.text)

if __name__ == "__main__":
    analyze_root_cause()