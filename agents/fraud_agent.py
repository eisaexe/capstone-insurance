# FILE: agents/fraud_agent.py
import time
import random

# The function name MUST be 'check_fraud_risk' to match app.py
def check_fraud_risk(narrative):
    """
    Simulates Step 3 & 4: Semantic Fraud Check.
    """
    time.sleep(1)
    
    # Simulated Result
    risk_score = random.randint(10, 95)
    fraud_reason = "None"
    
    if risk_score > 80:
        fraud_reason = "High similarity to known 'Staged Rear-End' syndicate."
    elif risk_score > 50:
        fraud_reason = "Anomalous repair cost vs damage description."
        
    return {
        "score": risk_score,
        "risk_level": "High" if risk_score > 70 else "Low",
        "reason": fraud_reason
    }