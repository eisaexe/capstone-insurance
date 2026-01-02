# FILE: agents/fraud_agent.py
from openai import OpenAI
import json

# ==========================================
# 👇 PASTE YOUR OPENAI API KEY INSIDE QUOTES
OPENAI_KEY = "sk-aQpnfpf9xb4_QVPHSYGc1wSjwABJs-NgFMmUZsTGQ2T3BlbkFJ8Z7K4NnjeAnYQx7rtQNe861Hjp0Uai5ovXQfko5lYA"
# ==========================================

def check_fraud_risk(narrative):
    """
    Uses OpenAI GPT-4o to analyze fraud risk.
    """
    if "sk-proj" in OPENAI_KEY or "xxxx" in OPENAI_KEY:
        return {
            "risk_score": 0, 
            "risk_level": "Setup Error", 
            "reasoning": "Please paste your real OpenAI API Key in agents/fraud_agent.py", 
            "fraud_indicators": []
        }

    try:
        client = OpenAI(api_key=OPENAI_KEY)
        
        prompt = f"""
        Act as an Insurance Fraud Expert. Analyze this claim narrative for potential fraud.
        Narrative: "{narrative}"
        
        Return a strictly valid JSON object with these keys:
        - risk_score (integer 0-100)
        - risk_level (Low/Medium/High)
        - reasoning (1 short sentence explaining the score)
        - fraud_indicators (List of 2-3 short bullet points)
        """
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Using the smart model for fraud
            response_format={"type": "json_object"}, # Enforce JSON
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        
        # Parse JSON output
        content = response.choices[0].message.content
        data = json.loads(content)
        return data

    except Exception as e:
        return {
            "risk_score": 0,
            "risk_level": "API Error",
            "reasoning": f"Connection failed: {str(e)}",
            "fraud_indicators": ["Check Internet", "Check API Key"]
        }