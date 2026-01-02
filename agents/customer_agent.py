# FILE: agents/customer_agent.py

import requests
import pandas as pd
import re
import time
import sys

# ==========================================
# PERPLEXITY API KEY
PPLX_API_KEY = "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"
# ==========================================

PPLX_URL = "https://api.perplexity.ai/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {PPLX_API_KEY}",
    "Content-Type": "application/json"
}

# ------------------------------------------
# Load Customer CSV
# ------------------------------------------
try:
    CUSTOMER_DB = pd.read_csv("customers.csv")
    CUSTOMER_DB["Customer_ID"] = CUSTOMER_DB["Customer_ID"].astype(str).str.upper()
except Exception:
    CUSTOMER_DB = pd.DataFrame()

# ------------------------------------------
# Load Motor Policy Text (CAR POLICY)
# ------------------------------------------
try:
    with open("policy.txt", "r", encoding="utf-8") as f:
        POLICY_TEXT = f.read().strip()
except Exception:
    POLICY_TEXT = ""

# ------------------------------------------
# Helpers
# ------------------------------------------
def lookup_customer(cust_id):
    if CUSTOMER_DB.empty:
        return None
    record = CUSTOMER_DB[CUSTOMER_DB["Customer_ID"] == cust_id]
    if not record.empty:
        return record.iloc[0].to_dict()
    return None


def typing_animation(label="Assistant is typing"):
    for _ in range(2):
        for dots in [".", "..", "..."]:
            sys.stdout.write(f"\r{label}{dots}")
            sys.stdout.flush()
            time.sleep(0.4)
    print("\r", end="")


def is_policy_query(text):
    keywords = [
        "policy", "coverage", "covered", "not covered", "exclusion",
        "idv", "deductible", "claim", "accident", "theft", "fire"
    ]
    return any(k in text.lower() for k in keywords)


# ------------------------------------------
# MAIN FUNCTION
# ------------------------------------------
def get_customer_response(user_query, session_context):
    """
    Customer Agent for Motor Insurance
    """

    user_id = session_context.get("auth_id")

    # --------------------------------------
    # AUTHENTICATION
    # --------------------------------------
    if not user_id:
        match = re.search(r"(CUST-\d{4})", user_query, re.IGNORECASE)

        if not match:
            return "🔒 Please enter your **Customer ID** (e.g., CUST-1001)."

        found_id = match.group(1).upper()
        customer = lookup_customer(found_id)

        if not customer:
            return f"❌ Customer ID `{found_id}` not found."

        # ✅ IMMEDIATE GREETING
        return {
            "action": "LOGIN",
            "user_id": found_id,
            "text": f"👋 Hi {customer['Name']}!"
        }

    # --------------------------------------
    # POST LOGIN
    # --------------------------------------
    customer = lookup_customer(user_id)
    if not customer:
        return "⚠️ Session error. Please login again."

    typing_animation()

    # --------------------------------------
    # STRICT CONTEXT BUILDING
    # --------------------------------------
    customer_context = f"""
CUSTOMER RECORD (USE ONLY THIS):
Name: {customer['Name']}
Policy Status: {customer['Status']}
Policy Limit: ₹{customer['Policy_Limit']}
Total Claims: {customer['Total_Claims']}
Claim Amount: ₹{customer['Claim_History_Amount']}
Renewal Date: {customer['Next_Renewal']}
""".strip()

    policy_context = f"""
MOTOR INSURANCE POLICY (USE ONLY THIS):
{POLICY_TEXT if POLICY_TEXT else "Policy text not available."}
""".strip()

    system_prompt = (
        "You are a MOTOR INSURANCE customer assistant.\n"
        "RULES:\n"
        "- Answer ONLY from the provided CUSTOMER RECORD and MOTOR POLICY.\n"
        "- If information is not present, clearly say it is not available.\n"
        "- Do NOT guess, assume, or provide legal conclusions.\n"
        "- No fraud accusations.\n"
        "- Be clear, polite, and concise."
    )

    user_prompt = f"""
{customer_context}

{policy_context}

User Question:
{user_query}
"""

    payload = {
        "model": "sonar-pro",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    }

    # --------------------------------------
    # API CALL
    # --------------------------------------
    try:
        response = requests.post(PPLX_URL, headers=HEADERS, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    except requests.exceptions.HTTPError:
        if "429" in response.text:
            return "⚠️ System temporarily unavailable. Please try again later."
        return "⚠️ Unable to process your request right now."

    except Exception as e:
        return f"⚠️ System Error: {str(e)}"
