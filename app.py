import streamlit as st
import time
import plotly.graph_objects as go
from datetime import datetime

# --- LINKING THE TEAM FILES ---
from agents.data_pipeline import process_and_classify
from agents.fraud_agent import check_fraud_risk
from agents.policy_agent import verify_policy
from agents.customer_agent import generate_chat_response

# --- PAGE CONFIG ---
st.set_page_config(page_title="Team 2 - Vehicle Claims", page_icon="🚗", layout="wide")

# --- SHARED SESSION STATE ---
if 'claim_db' not in st.session_state:
    st.session_state.claim_db = {} 
if 'current_processing_claim' not in st.session_state:
    st.session_state.current_processing_claim = None

# --- HELPER FOR GAUGES ---
def create_gauge(value, title, color_mode="standard"):
    # (Same gauge code as provided before)
    max_val = 100
    if color_mode == "risk":
        bar_color = "red" if value > 70 else "green"
    elif color_mode == "urgency":
        map_val = {"Low": 25, "Medium": 50, "High": 90}
        value = map_val.get(value, 0)
        bar_color = "red" if value > 60 else "green"
    else:
        bar_color = "blue"

    fig = go.Figure(go.Indicator(
        mode = "gauge+number", value = value, title = {'text': title},
        gauge = {'axis': {'range': [None, 100]}, 'bar': {'color': bar_color}}
    ))
    fig.update_layout(height=150, margin=dict(l=20, r=20, t=10, b=10))
    return fig

# --- VIEW 1: OFFICER DASHBOARD ---
def officer_dashboard():
    st.title("🛡️ Officer Dashboard")
    col1, col2 = st.columns([1, 2])

    with col1:
        st.info("📝 **New Claim Entry**")
        narrative = st.text_area("Narrative", "Car hit by truck. No FIR.", height=150)
        
        if st.button("🚀 Process Claim"):
            with st.spinner("AI Agents Working..."):
                # --- CALLING TEAM FUNCTIONS ---
                res_data = process_and_classify(narrative)
                res_fraud = check_fraud_risk(narrative)
                res_policy = verify_policy(narrative)
                
                # Combine results
                st.session_state.current_processing_claim = {
                    **res_data, **res_fraud, **res_policy,
                    "confidence": 88 
                }
            st.rerun()

    with col2:
        if st.session_state.current_processing_claim:
            data = st.session_state.current_processing_claim
            
            # METER TABS
            tab1, tab2, tab3 = st.tabs(["📊 Overview", "🕵️ Fraud", "📜 Policy"])
            
            with tab1:
                c1, c2, c3 = st.columns(3)
                c1.plotly_chart(create_gauge(data['urgency'], "Urgency", "urgency"), use_container_width=True)
                c2.plotly_chart(create_gauge(data['score'], "Fraud Risk", "risk"), use_container_width=True)
                c3.plotly_chart(create_gauge(data['confidence'], "Confidence", "conf"), use_container_width=True)
            
            with tab2:
                if data['score'] > 50:
                    st.error(f"Reason: {data['reason']}")
                else:
                    st.success("No fraud detected.")
            
            with tab3:
                for doc in data['missing_documents']:
                    st.warning(f"Missing: {doc}")

    # HUMAN IN THE LOOP
    if st.session_state.current_processing_claim:
        st.divider()
        decision = st.radio("Officer Decision:", ["Approve", "Request Info", "Escalate"])
        if st.button("Submit Decision"):
            st.session_state.claim_db["Active_Claim"] = {
                "status": decision,
                "public_reason": "Missing Documents" if decision == "Request Info" else ""
            }
            st.success("Saved!")

# --- VIEW 2: CUSTOMER CHAT ---
def customer_chat():
    st.title("💬 Customer Support")
    user_input = st.chat_input("Ask about your claim...")
    
    if user_input:
        # Display User Message
        with st.chat_message("user"):
            st.write(user_input)
            
        # Get Response from Agent File
        active_claim = st.session_state.claim_db.get("Active_Claim")
        response = generate_chat_response(user_input, active_claim)
        
        # Display AI Message
        with st.chat_message("assistant"):
            st.write(response)

# --- ROUTING ---
page = st.sidebar.radio("Go to", ["Officer Dashboard", "Customer Chat"])
if page == "Officer Dashboard":
    officer_dashboard()
else:
    customer_chat()