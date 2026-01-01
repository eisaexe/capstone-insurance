# FILE: agents/customer_agent.py
import google.generativeai as genai
import pandas as pd
import re

# ==========================================
# 👇 PASTE YOUR GEMINI API KEY INSIDE QUOTES
KEY = "AIzaSyCTBigtnx1U8uXd2RGcLfhUkz87oLhnsBI"
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
    Handles Login + Chat Response
    """
    if "PASTE_YOUR" in KEY:
        return "⚠️ Error: Please paste your API Key in agents/customer_agent.py"

    try:
        genai.configure(api_key=KEY)
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
        
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
                # 👇 THIS IS THE REPEATED PROMPT IF THEY FAIL TO PROVIDE ID
                return "🔒 **Authentication Required**\nPlease provide your **Customer ID** (e.g., 'CUST-1001') to continue."

        # 3. IF LOGGED IN -> ANSWER QUESTION USING DATA
        if user_id:
            customer_data = lookup_customer(user_id)
        
        # Create Data Context for Gemini
        context = f"""
        USER PROFILE:
        - Name: {customer_data['Name']}
        - Claims History: {customer_data['Total_Claims']} claims (Total: ₹{customer_data['Claim_History_Amount']})
        - Policy Status: {customer_data['Status']}
        - Policy Limit: ₹{customer_data['Policy_Limit']}
        - Renewal Date: {customer_data['Next_Renewal']}
        """

        prompt = f"""
        Act as a friendly insurance agent.
        {context}
        User Query: "{user_query}"
        
        Instructions:
        - Answer concisely based ONLY on the profile data.
        - If they ask about claims, mention the exact number and amount.
        """
        
        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        return f"System Error: {str(e)}"