"""
Analyze baby tracking data using Gemini API.
Detects abnormal sleep patterns, emotions, and other health indicators.
"""
import json
import os
from datetime import datetime
import config

try:
    import google.generativeai as genai
except ImportError:
    print("Error: google-generativeai not installed.")
    print("Install it with: pip install google-generativeai")
    exit(1)

def load_baby_data(json_file_path):
    """Load baby tracking data from JSON file."""
    try:
        with open(json_file_path, 'r') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print(f"Error: File '{json_file_path}' not found.")
        exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in '{json_file_path}': {e}")
        exit(1)

def format_data_for_analysis(data):
    """Format the baby tracking data into a readable format for Gemini."""
    formatted = f"""BABY TRACKING DATA ANALYSIS REQUEST

Baby Information:
- Name: {data['baby_info']['name']}
- Age: {data['baby_info']['age_months']} months
- Tracking Period: {data['baby_info']['tracking_period_hours']} hours

Summary Statistics:
- Total Sleep: {data['summary']['total_sleep_hours']} hours
- Total Feedings: {data['summary']['total_feedings']}
- Total Milk Consumed: {data['summary']['total_ml_consumed']} ml
- Average Feeding Amount: {data['summary']['average_feeding_amount_ml']} ml
- Diaper Changes: {data['summary']['diaper_changes']}
- Longest Sleep: {data['summary']['sleep_sessions']['longest_sleep_minutes']} minutes
- Shortest Sleep: {data['summary']['sleep_sessions']['shortest_sleep_minutes']} minutes

Emotion Distribution:
{json.dumps(data['summary']['emotion_distribution'], indent=2)}

DETAILED TIMELINE (Last 48 hours):
"""
    
    for entry in data['entries']:
        formatted += f"\n--- {entry['timestamp']} ({entry['event_type']}) ---\n"
        
        if 'sleep' in entry:
            sleep = entry['sleep']
            formatted += f"Sleep: Status={sleep.get('status', 'N/A')}, "
            if 'duration_minutes' in sleep:
                formatted += f"Duration={sleep['duration_minutes']} min, "
            formatted += f"Quality={sleep.get('sleep_quality', 'N/A')}\n"
        
        if 'emotion' in entry:
            emotion = entry['emotion']
            formatted += f"Emotion: Mood={emotion.get('mood', 'N/A')}, "
            formatted += f"Energy={emotion.get('energy_level', 'N/A')}, "
            formatted += f"Fussiness={emotion.get('fussiness', 'N/A')}\n"
        
        if 'feeding' in entry:
            feeding = entry['feeding']
            formatted += f"Feeding: Type={feeding.get('type', 'N/A')}, "
            formatted += f"Amount={feeding.get('amount_ml', 0)} ml, "
            formatted += f"Duration={feeding.get('duration_minutes', 0)} min\n"
        
        if 'diaper' in entry:
            diaper = entry['diaper']
            formatted += f"Diaper: Type={diaper.get('type', 'N/A')}, Changed={diaper.get('changed', False)}\n"
    
    return formatted

def analyze_with_gemini(formatted_data, api_key, baby_age_months):
    """Send data to Gemini API for analysis."""
    if not api_key or api_key == "":
        print("Error: Gemini API key not found. Please set GEMINI_API_KEY in .env file.")
        exit(1)
    
    # Configure Gemini API
    genai.configure(api_key=api_key)
    
    # Create the model - using gemini-2.5-flash (latest, faster and cost-effective)
    # Alternative: 'gemini-2.5-pro' for more complex analysis
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # Create the analysis prompt
    prompt = f"""{formatted_data}

ANALYSIS REQUEST:
Please analyze this baby tracking data and provide a comprehensive report covering:

1. SLEEP PATTERN ANALYSIS:
   - Identify any abnormal sleep patterns (too much/little sleep, irregular schedules)
   - Evaluate sleep quality and consistency
   - Note any concerning sleep duration patterns (very short naps, insufficient night sleep, etc.)
   - Check if sleep schedule aligns with age-appropriate expectations for a {baby_age_months}-month-old

2. EMOTION & BEHAVIOR ANALYSIS:
   - Identify abnormal emotional patterns (excessive fussiness, prolonged crying, lack of happy/content moods)
   - Note any sudden mood changes or concerning behavioral patterns
   - Evaluate overall emotional well-being

3. FEEDING ANALYSIS:
   - Check if feeding amounts and frequency are appropriate
   - Identify any feeding pattern abnormalities (overfeeding, underfeeding, irregular intervals)
   - Note any correlation between feeding and sleep/emotion patterns

4. OVERALL HEALTH INDICATORS:
   - Identify any patterns that might indicate health concerns
   - Note any red flags or areas requiring attention
   - Provide recommendations if abnormalities are detected

5. SUMMARY:
   - Overall assessment (healthy patterns vs concerns)
   - Key findings and actionable insights
   - Recommendations for improvement if needed

Please format your response in a clear, structured manner suitable for parents/caregivers.
"""
    
    print("Sending data to Gemini API for analysis...")
    print("This may take a moment...\n")
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        exit(1)

def save_analysis_to_file(analysis_text, output_file):
    """Save the analysis to a text file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    formatted_output = f"""BABY TRACKING DATA ANALYSIS REPORT
Generated: {timestamp}
{'='*60}

{analysis_text}

{'='*60}
End of Report
"""
    
    try:
        with open(output_file, 'w') as f:
            f.write(formatted_output)
        print(f"Analysis saved to: {output_file}")
    except Exception as e:
        print(f"Error saving file: {e}")
        exit(1)

def main():
    # File paths
    json_file = 'baby_tracking_data.json'
    output_file = 'baby_analysis_report.txt'
    
    # Load baby tracking data
    print(f"Loading baby tracking data from '{json_file}'...")
    data = load_baby_data(json_file)
    print("Data loaded successfully.\n")
    
    # Format data for analysis
    print("Formatting data for analysis...")
    formatted_data = format_data_for_analysis(data)
    
    # Get API key from config
    api_key = config.GEMINI_API_KEY
    
    # Analyze with Gemini
    analysis = analyze_with_gemini(formatted_data, api_key, data['baby_info']['age_months'])
    
    # Save analysis to file
    print(f"\nSaving analysis to '{output_file}'...")
    save_analysis_to_file(analysis, output_file)
    
    # Also print to console
    print("\n" + "="*60)
    print("ANALYSIS COMPLETE")
    print("="*60)
    print(analysis)
    print("\n" + "="*60)

if __name__ == "__main__":
    main()

