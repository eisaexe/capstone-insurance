# FILE: agents/policy_agent.py
import time

def verify_policy(narrative):
    """
    Simulates Step 5: Policy Interpretation.
    """
    time.sleep(1)
    
    missing_docs = []
    # Simple rule-based check for the prototype
    if "fir" not in narrative.lower():
        missing_docs.append("Police FIR")
    if "photo" not in narrative.lower():
        missing_docs.append("Damage Photos")
        
    return {
        "missing_documents": missing_docs,
        "policy_clause": "Clause 4.2: FIR mandatory for third-party damages."
    }