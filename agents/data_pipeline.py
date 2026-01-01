# FILE: agents/data_pipeline.py
import time

def process_and_classify(narrative):
    """
    Simulates Step 1 & 2: Ingestion and Triage.
    """
    time.sleep(1) 
    
    # Simple keyword-based logic for now
    urgency = "Medium"
    if "total loss" in narrative.lower() or "fire" in narrative.lower():
        urgency = "High"
    elif "scratch" in narrative.lower():
        urgency = "Low"
        
    claim_type = "Theft" if "stolen" in narrative.lower() else "Accident - Collision"
    
    return {
        "urgency": urgency,
        "type": claim_type
    }