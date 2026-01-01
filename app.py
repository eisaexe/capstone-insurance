import streamlit as st
import time
import random
import plotly.graph_objects as go # NEW IMPORT FOR GAUGES

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Team 2 - Vehicle Claims Intelligence",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- SESSION STATE INITIALIZATION ---
if 'claim_db' not in st.session_state:
    st.session_state.claim_db = {}
if 'current_processing_claim' not in st.session_state:
    st.session_state.current_processing_claim = None

# --- HELPER: CREATE GAUGE CHART ---
def create_gauge(value, title, color_mode="standard", max_val=100):
    """Creates a speedometer-style gauge"""
    
    # Color Logic
    if color_mode == "risk":
        bar_color = "red" if value > 70 else ("orange" if value > 40 else "green")
    elif color_mode == "urgency":
        # Map Text to Number for Gauge
        map_val = {"Low": 25, "Medium": 50, "High": 90}
        bar_color = "red" if value == "High" else ("orange" if value == "Medium" else "green")
        value = map_val.get(value, 0)
    else: # Confidence
        bar_color = "blue"

    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = value,
        title = {'text': title},
        gauge = {
            'axis': {'range': [None, max_val]},
            'bar': {'color': bar_color},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, max_val], 'color': "#f0f2f6"}
            ],
        }
    ))
    fig.update_layout(height=200, margin=dict(l=20, r=20, t=30, b=20))
    return fig

# --- SIMULATED AI BACKEND ---
def simulate_ai_pipeline(narrative):
    """Simulates the 5-step Business Track Workflow"""
    time.sleep(1) 
    urgency = "High" if "total loss" in narrative.lower() or "fire" in narrative.lower() else "Medium"
    risk_score = random.randint(10, 95)
    fraud_reason = "None"
    
    if risk_score > 80:
        fraud_reason = "High similarity to known 'Staged Rear-End' syndicate."
    elif risk_score > 50:
        fraud_reason = "Anomalous repair cost vs damage description."
    
    missing_docs = []
    if "fir" not in narrative.lower(): missing_docs.append("Police FIR")
    if "photo" not in narrative.lower(): missing_docs.append("Damage Photos")
        
    return {
        "urgency": urgency,
        "type": "Accident - Collision" if "collision" in narrative else "Theft",
        "fraud_risk": "High" if risk_score > 70 else "Low",
        "fraud_score": risk_score,
        "fraud_reason": fraud_reason,
        "policy_issues": missing_docs,
        "confidence": 88
    }

# --- VIEW 1: OFFICER DASHBOARD (BUSINESS TRACK) ---
def officer_dashboard():
    st.title("🛡️ Claims Intelligence Platform (Officer View)")
    
    col1, col2 = st.columns([1, 2])
    
    # LEFT COLUMN: INPUTS
    with col1:
        st.info("📝 **New Claim Entry**")
        claim_id = st.text_input("Claim ID", "CLM-2025-001")
        policy_id = st.text_input("Policy ID", "POL-99822")
        narrative = st.text_area("Claim Narrative", 
            "The car was parked and hit by an unknown truck. Massive damage to bumper. No FIR filed yet.", height=150)
        
        if st.button("🚀 Process Claim Analysis"):
            with st.status("Running AI Agents...", expanded=True) as status:
                st.write("📥 Ingesting & Chunking...")
                time.sleep(0.5)
                st.write("🏷️ Classifying Severity...")
                time.sleep(0.5)
                st.write("🕵️ Checking Fraud Vectors...")
                time.sleep(0.5)
                status.update(label="Analysis Complete", state="complete", expanded=False)
            
            # Run simulation
            results = simulate_ai_pipeline(narrative)
            st.session_state.current_processing_claim = results
            st.rerun()

    # RIGHT COLUMN: RESULTS (WITH NEW TABS)
    with col2:
        if st.session_state.current_processing_claim:
            data = st.session_state.current_processing_claim
            
            # --- NEW TABS STRUCTURE ---
            tab1, tab2, tab3 = st.tabs(["📊 Overview & Meters", "🕵️ Fraud Details", "📜 Policy Check"])
            
            # TAB 1: METERS (GAUGES)
            with tab1:
                st.markdown("### Agent Assessment Summary")
                m1, m2, m3 = st.columns(3)
                
                with m1:
                    # Urgency Meter
                    st.plotly_chart(create_gauge(data['urgency'], "Urgency", "urgency"), use_container_width=True)
                
                with m2:
                    # Fraud Risk Meter
                    st.plotly_chart(create_gauge(data['fraud_score'], "Fraud Risk Score", "risk"), use_container_width=True)
                
                with m3:
                    # Confidence Meter
                    st.plotly_chart(create_gauge(data['confidence'], "AI Confidence", "confidence"), use_container_width=True)
                
                st.caption(f"**Claim Type:** {data['type']}")

            # TAB 2: FRAUD DETAILS
            with tab2:
                st.subheader("Semantic Fraud Analysis")
                if data['fraud_score'] > 50:
                    st.error(f"⚠️ **Flagged:** {data['fraud_reason']}")
                    st.markdown("""
                    **Matched Patterns:**
                    * *Case #992 (Staged Rear-End)* - 89% Similarity
                    * *Case #104 (Duplicate VIN)* - 45% Similarity
                    """)
                else:
                    st.success("✅ No significant fraud patterns detected.")

            # TAB 3: POLICY DETAILS
            with tab3:
                st.subheader("Policy Interpretation")
                if data['policy_issues']:
                    for issue in data['policy_issues']:
                        st.warning(f"⚠️ Missing Document: **{issue}**")
                    st.info("ℹ️ Clause 4.2: 'Police FIR is mandatory for third-party damage.'")
                else:
                    st.success("✅ All required documents present.")

    # --- HUMAN IN THE LOOP SECTION (Always Visible below tabs) ---
    if st.session_state.current_processing_claim:
        st.divider()
        st.markdown("### 👤 Human-in-the-Loop Decision")
        
        with st.container(border=True):
            h_col1, h_col2 = st.columns([2, 1])
            with h_col1:
                officer_notes = st.text_area("Officer Notes", "Reviewed fraud flags. Narrative consistent.")
            with h_col2:
                decision = st.radio("Action:", ["Approve", "Request Info", "Escalate (Fraud)"])
                if st.button("Submit Decision"):
                    st.session_state.claim_db["Active_Claim"] = {
                        "status": decision, 
                        "reason": "Missing FIR" if "Request" in decision else "Standard Review"
                    }
                    st.success(f"Decision Recorded: {decision}")

# --- VIEW 2: CUSTOMER ASSISTANT ---
def customer_chat():
    st.title("💬 Insurance Assistant")
    
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "How can I help with your claim?"}]

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Check status..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Logic
        db_record = st.session_state.claim_db.get("Active_Claim")
        if "status" in prompt.lower() and db_record:
            resp = f"Your claim status is: **{db_record['status']}**."
        else:
            resp = "I can help with claim status. Please provide your ID."
        
        time.sleep(0.5)
        st.session_state.messages.append({"role": "assistant", "content": resp})
        with st.chat_message("assistant"):
            st.markdown(resp)

# --- ROUTING ---
sidebar_nav = st.sidebar.radio("Navigation", ["Officer Dashboard", "Customer Support"])
if sidebar_nav == "Officer Dashboard":
    officer_dashboard()
else:
    customer_chat()