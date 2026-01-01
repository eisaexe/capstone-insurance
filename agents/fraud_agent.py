# FILE: agents/fraud_agent.py
import google.generativeai as genai
import json

# ==========================================
# 👇 PASTE YOUR GEMINI API KEY INSIDE QUOTES
KEY = "AIzaSyCTBigtnx1U8uXd2RGcLfhUkz87oLhnsBI" 
# ==========================================

def check_fraud_with_gemini(narrative):
    """
    Uses Gemini 2.5 Flash to analyze fraud risk.
    """
    # Safety Check
    if "PASTE_YOUR" in KEY:
        return {
            "risk_score": 0, 
            "risk_level": "Setup Error", 
            "reasoning": "Please paste your real API Key in agents/fraud_agent.py", 
            "fraud_indicators": []
        }

    try:
        genai.configure(api_key=KEY)
        model = genai.GenerativeModel('gemini-2.5-flash-lite') 
        
        prompt = f"""
        Act as an Insurance Fraud Expert. Analyze this claim:
        "{narrative}"
        
        Output strictly valid JSON with these keys:
        - risk_score (integer 0-100)
        - risk_level (Low/Medium/High)
        - reasoning (Short, punchy 1-sentence reason)
        - fraud_indicators (List of 2-3 suspicious points)
        """
        
        response = model.generate_content(prompt)
        
        # Clean response to ensure it's JSON
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        data = json.loads(clean_text)
        return data

    except Exception as e:
        return {
            "risk_score": 50,
            "risk_level": "API Error",
            "reasoning": f"Connection failed: {str(e)}",
            "fraud_indicators": ["Check internet", "Check API Key"]
        }