# FILE: agents/customer_agent.py
import time

def generate_chat_response(user_query, claim_status_data):
    """
    Simulates Step 2 & 4 of Customer Track: RAG + Safety Layer.
    """
    time.sleep(0.5)
    
    # If we have a claim decision in the database (passed from app.py)
    if claim_status_data:
        status = claim_status_data.get('status', 'Under Review')
        reason = claim_status_data.get('public_reason', '')
        
        # Simple logic to check what the user is asking
        if "status" in user_query.lower():
            if status == "Approve":
                return "Good news! Your claim has been approved."
            elif status == "Request Info":
                return f"Your claim is on hold. We are missing: {reason}. Please upload it."
            else:
                return "Your claim is currently under standard quality review."
    
    return "I can help you with your claim status. Please provide your Claim ID."