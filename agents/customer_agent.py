# FILE: agents/customer_agent.py
from openai import OpenAI
import pandas as pd
import re

# ==========================================
# 👇 PASTE YOUR OPENAI API KEY INSIDE QUOTES
OPENAI_KEY = "sk-aQpnfpf9xb4_QVPHSYGc1wSjwABJs-NgFMmUZsTGQ2T3BlbkFJ8Z7K4NnjeAnYQx7rtQNe861Hjp0Uai5ovXQfko5lYA"
# ==========================================

# Load the CSV Data
try:
    CUSTOMER_DB = pd.read_csv("customers.csv")
    CUSTOMER_DB['Customer_ID'] = CUSTOMER_DB['Customer_ID'].astype(str).str.strip().str.upper()
except Exception as e:
    CUSTOMER_DB = pd.DataFrame()

def lookup_customer(cust_id):
    """Searches the CSV for the Customer ID."""
    if CUSTOMER_DB.empty: return None
    cust_id = cust_id.strip().upper()
    record = CUSTOMER_DB[CUSTOMER_DB['Customer_ID'] == cust_id]
    if not record.empty: return record.iloc[0].to_dict()
    return None

def get_customer_response(user_query, session_context):
    """
    Handles Login + Chat Response using OpenAI
    """
    if "sk-proj" in OPENAI_KEY or "xxxx" in OPENAI_KEY:
        return "⚠️ Error: Please paste your OpenAI API Key in agents/customer_agent.py"

    try:
        client = OpenAI(api_key=OPENAI_KEY)
        
        # 1. CHECK IF USER IS LOGGED IN
        user_id = session_context.get('auth_id')
        customer_data = None
        
        # 2. IF NOT LOGGED IN -> LOOK FOR ID IN TEXT
        if not user_id:
            # Regex: Finds 'CUST-' followed by 4 digits (case insensitive)
            match = re.search(r'(CUST-\d{4})', user_query, re.IGNORECASE)
            
            if match:
                found_id = match.group(1).upper()
                customer_data = lookup_customer(found_id)
                
                if customer_data:
                    # SUCCESS: Return "LOGIN" action dictionary
                    return {
                        "action": "LOGIN",
                        "user_id": found_id,
                        "text": f"✅ Identity Verified! Welcome back, {customer_data['Name']}."
                    }
                else:
                    return f"❌ I found ID '{found_id}', but it's not in our database. Please check customers.csv."
            else:
                # REPEATED PROMPT IF THEY FAIL TO PROVIDE ID
                return "🔒 **Authentication Required**\nPlease provide your **Customer ID** (e.g., 'CUST-1001') to continue."

        # 3. IF LOGGED IN -> ANSWER QUESTION USING DATA
        if user_id:
            customer_data = lookup_customer(user_id)
        
        # Create Data Context for OpenAI
        context = f"""
        USER PROFILE:
        - Name: {customer_data['Name']}
        - Claims History: {customer_data['Total_Claims']} claims (Total: ₹{customer_data['Claim_History_Amount']})
        - Policy Status: {customer_data['Status']}
        - Policy Limit: ₹{customer_data['Policy_Limit']}
        - Renewal Date: {customer_data['Next_Renewal']}
        """

        prompt = f"""
        Act as a friendly, empathetic insurance assistant.
        User Data: {context}
        User Query: "{user_query}"
        
        Instructions:
        - Answer based ONLY on the User Data provided.
        - Be concise and polite.
        """
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", # Fast model for chat
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        return response.choices[0].message.content

    except Exception as e:
        return f"System Error: {str(e)}"