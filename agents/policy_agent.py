# FILE: Capstone_insurance/agents/policy_agent.py

import time

POLICY_TXT_PATH = "insurance_policy.txt"

# ----------------------------
# Load policy text ONCE
# ----------------------------
try:
    with open(POLICY_TXT_PATH, "r", encoding="utf-8") as f:
        POLICY_TEXT = f.read().lower()
except FileNotFoundError:
    POLICY_TEXT = ""

def verify_policy(narrative: str):
    """
    Step 5: Policy Interpretation using TXT policy document.
    """
    time.sleep(1)

    missing_docs = []

    # FIR requirement
    if "fir" not in narrative.lower():
        missing_docs.append("Police FIR")

    # Photo requirement
    if "photo" not in narrative.lower():
        missing_docs.append("Damage Photos")

    # Simple clause grounding (demo-safe)
    clause = "Clause 4.2: FIR mandatory for third-party damages."

    # Evidence-backed policy check
    policy_hit = "fir" in POLICY_TEXT

    return {
        "missing_documents": missing_docs,
        "policy_clause": clause if policy_hit else "Relevant clause under review"
    }
