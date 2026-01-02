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
# Load Insurance Policy TXT
# (UNCHANGED – as requested)
# ------------------------------------------
try:
    with open("insurance_policy.txt", "r", encoding="utf-8") as f:
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


def classify_query(text: str) -> str:
    """
    Robust intent classification:
    1. CUSTOMER intent has priority
    2. POLICY intent only if no customer signals
    """

    text_l = text.lower()

    customer_keywords = [
        "my name", "my email", "my phone", "my number", "my address",
        "my policy number", "my dob", "my date of birth",
        "customer id", "account", "profile", "personal details",
        "registered", "contact details"
    ]

    policy_keywords = [
        "policy coverage", "coverage", "covered", "not covered",
        "exclusion", "idv", "deductible", "claim process",
        "accident", "theft", "fire", "policy limit", "eligibility"
    ]

    if any(k in text_l for k in customer_keywords):
        return "CUSTOMER"

    if any(k in text_l for k in policy_keywords):
        return "POLICY"

    # Default fallback: customer context
    return "CUSTOMER"


def call_llm(system_prompt: str, user_prompt: str) -> str:
    payload = {
        "model": "sonar-pro",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    }

    response = requests.post(PPLX_URL, headers=HEADERS, json=payload)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


# ------------------------------------------
# MAIN FUNCTION
# ------------------------------------------
def get_customer_response(user_query, session_context):
    """
    Insurance Customer Support Assistant
    with strict data-source isolation
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

        return {
            "action": "LOGIN",
            "user_id": found_id,
            "text": f"👋 Hi {customer['Name']}! How can I help you today?"
        }

    # --------------------------------------
    # POST LOGIN
    # --------------------------------------
    customer = lookup_customer(user_id)
    if not customer:
        return "⚠️ Session error. Please login again."

    typing_animation()

    query_type = classify_query(user_query)

    # =====================================================
    # A. CUSTOMER DETAIL QUERY (CSV ONLY)
    # =====================================================
    if query_type == "CUSTOMER":

        customer_context = f"""
CUSTOMER RECORD (AUTHORITATIVE SOURCE):
{customer}
"""

        system_prompt = (
            "You are an Insurance Customer Support Assistant.\n"
            "Answer using ONLY the provided customer record.\n"
            "Do NOT use policy information.\n"
            "If information is missing, say:\n"
            "'This information is not available in the customer records.'"
        )

        user_prompt = f"""
{customer_context}

User Question:
{user_query}
"""

        try:
            return call_llm(system_prompt, user_prompt)
        except Exception:
            return "⚠️ Unable to retrieve customer information at this time."

    # =====================================================
    # B. INSURANCE POLICY QUERY (UNCHANGED)
    # =====================================================
    if query_type == "POLICY":

        policy_context = f"""
INSURANCE POLICY DOCUMENT:
{POLICY_TEXT if POLICY_TEXT else "Policy text not available."}
"""

        system_prompt = (
            "You are an Insurance Policy Support Assistant.\n"
            "Answer using ONLY the provided policy document.\n"
            "Do NOT add interpretation or assumptions.\n"
            "If information is missing, say:\n"
            "'This information is not specified in the insurance policy document.'"
        )

        user_prompt = f"""
{policy_context}

User Question:
{user_query}
"""

        try:
            return call_llm(system_prompt, user_prompt)
        except Exception:
            return "⚠️ Unable to retrieve policy information at this time."
