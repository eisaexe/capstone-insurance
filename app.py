# FILE: app.py
import streamlit as st
import plotly.graph_objects as go
from agents.fraud_agent import check_fraud_with_gemini
from agents.customer_agent import get_customer_response

# --- CONFIGURATION ---
st.set_page_config(page_title="Team 2 AI", layout="wide", page_icon="🛡️")

# --- GLASSMORPHISM CSS ---
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); color: white; }
    .glass-card { background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(10px); border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.18); padding: 20px; margin-bottom: 20px; }
    h1, h2, h3, p { color: white !important; }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if 'auth_id' not in st.session_state: st.session_state.auth_id = None

# 👇 THIS IS WHERE WE SET THE "PRE-RESPONSE"
if 'chat_history' not in st.session_state: 
    st.session_state.chat_history = [{
        "role": "assistant", 
        "content": "🔒 **Authentication Required**\nPlease provide your **Customer ID** (e.g., 'CUST-1001') to continue."
    }]

if 'analysis_result' not in st.session_state: st.session_state.analysis_result = None

# --- SIDEBAR ---
with st.sidebar:
    st.header("🛡️ IntelliClaim")
    page = st.radio("Navigate", ["Officer Dashboard", "Customer Chat"])
    st.divider()
    if st.session_state.auth_id:
        st.success(f"👤 User: {st.session_state.auth_id}")
        if st.button("Logout"):
            st.session_state.auth_id = None
            # Reset chat to ask for ID again
            st.session_state.chat_history = [{
                "role": "assistant", 
                "content": "🔒 **Authentication Required**\nPlease provide your **Customer ID** to continue."
            }]
            st.rerun()

# --- PAGE: CUSTOMER CHAT ---
if page == "Customer Chat":
    st.markdown("<h1 style='text-align: center;'>💬 Insurance Assistant</h1>", unsafe_allow_html=True)
    
    # Chat History
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            
    if prompt := st.chat_input("Type your Customer ID..."):
        # User Message
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
            
        # AI Response
        with st.spinner("Verifying Identity..."):
            context = {'auth_id': st.session_state.auth_id}
            response = get_customer_response(prompt, context)
            
            final_text = response
            # Login Action Logic
            if isinstance(response, dict) and response.get("action") == "LOGIN":
                st.session_state.auth_id = response["user_id"]
                final_text = response["text"]
                st.rerun()
            
        # Bot Message
        st.session_state.chat_history.append({"role": "assistant", "content": final_text})
        with st.chat_message("assistant"):
            st.write(final_text)

# --- PAGE: OFFICER DASHBOARD ---
elif page == "Officer Dashboard":
    st.markdown("<h1 style='text-align: center;'>👮 Claims Command Center</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("📥 New Claim")
        narrative = st.text_area("Narrative", "Car hit a tree...", height=150)
        if st.button("⚡ Analyze"):
            res = check_fraud_with_gemini(narrative)
            st.session_state.analysis_result = res
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        if st.session_state.analysis_result:
            data = st.session_state.analysis_result
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.metric("Risk Score", f"{data.get('risk_score')}/100")
            st.metric("Reasoning", data.get('reasoning'))
            st.markdown('</div>', unsafe_allow_html=True)