# FILE: app.py
import streamlit as st
import plotly.graph_objects as go

# IMPORT THE OPENAI AGENTS
from agents.fraud_agent import check_fraud_risk
from agents.customer_agent import get_customer_response

# --- CONFIGURATION ---
st.set_page_config(page_title="Team 2 AI", layout="wide", page_icon="🛡️")

# --- GLASSMORPHISM CSS ---
st.markdown("""
<style>
    /* Background Gradient */
    .stApp {
        background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
        color: white;
    }
    /* Glass Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
    }
    /* Text Overrides */
    h1, h2, h3, p, label { color: white !important; }
    .stTextInput > div > div > input { color: white; background-color: rgba(255,255,255,0.1); }
    .stTextArea > div > div > textarea { color: white; background-color: rgba(255,255,255,0.1); }
    /* Metric Styling */
    .metric-val { font-size: 2rem; font-weight: bold; }
    .metric-lbl { font-size: 0.9rem; color: #ccc; text-transform: uppercase; }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION ---
if 'auth_id' not in st.session_state: 
    st.session_state.auth_id = None

# 👇 PRE-RESPONSE: BOT ASKS FIRST
if 'chat_history' not in st.session_state: 
    st.session_state.chat_history = [{
        "role": "assistant", 
        "content": "🔒 **Authentication Required**\nHello! Please provide your **Customer ID** (e.g., 'CUST-1001') to access your policy details."
    }]

if 'analysis_result' not in st.session_state: 
    st.session_state.analysis_result = None

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2503/2503509.png", width=50)
    st.header("IntelliClaim AI")
    page = st.radio("Navigate", ["Officer Dashboard", "Customer Chat"])
    st.divider()
    
    if st.session_state.auth_id:
        st.success(f"👤 Logged in: {st.session_state.auth_id}")
        if st.button("Logout"):
            st.session_state.auth_id = None
            # Reset chat to ask for ID again
            st.session_state.chat_history = [{
                "role": "assistant", 
                "content": "🔒 **Authentication Required**\nPlease provide your **Customer ID** to continue."
            }]
            st.rerun()

# --- PAGE 1: CUSTOMER CHAT ---
if page == "Customer Chat":
    st.markdown("<h2 style='text-align: center;'>💬 Customer Support</h2>", unsafe_allow_html=True)
    
    # Display Chat History
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            
    # Chat Input
    if prompt := st.chat_input("Type your message..."):
        # User Message
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
            
        # AI Response
        with st.spinner("Processing..."):
            context = {'auth_id': st.session_state.auth_id}
            response = get_customer_response(prompt, context)
            
            final_text = response
            # Handle Login Action
            if isinstance(response, dict) and response.get("action") == "LOGIN":
                st.session_state.auth_id = response["user_id"]
                final_text = response["text"]
                st.rerun()
            
        # Bot Message
        st.session_state.chat_history.append({"role": "assistant", "content": final_text})
        with st.chat_message("assistant"):
            st.write(final_text)

# --- PAGE 2: OFFICER DASHBOARD ---
elif page == "Officer Dashboard":
    st.markdown("<h2 style='text-align: center;'>👮 Claims Intelligence</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    # Input Column
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("📥 Process New Claim")
        narrative = st.text_area("Incident Narrative", "Driver claims car hit a tree at 2AM. No witnesses...", height=150)
        
        if st.button("⚡ Analyze Fraud Risk", use_container_width=True):
            with st.spinner("Consulting GPT-4o..."):
                res = check_fraud_risk(narrative)
                st.session_state.analysis_result = res
        st.markdown('</div>', unsafe_allow_html=True)

    # Results Column
    with col2:
        if st.session_state.analysis_result:
            data = st.session_state.analysis_result
            
            # Metric Cards
            c1, c2, c3 = st.columns(3)
            with c1: 
                st.markdown(f'<div class="glass-card"><div class="metric-lbl">RISK LEVEL</div><div class="metric-val" style="color: {"#ff4b4b" if data["risk_score"] > 50 else "#4ade80"};">{data["risk_level"]}</div></div>', unsafe_allow_html=True)
            with c2: 
                st.markdown(f'<div class="glass-card"><div class="metric-lbl">FRAUD SCORE</div><div class="metric-val">{data["risk_score"]}</div></div>', unsafe_allow_html=True)
            with c3: 
                st.markdown(f'<div class="glass-card"><div class="metric-lbl">CONFIDENCE</div><div class="metric-val">95%</div></div>', unsafe_allow_html=True)
            
            # Gauge Chart
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = data.get('risk_score', 0),
                title = {'text': "Fraud Probability", 'font': {'color': 'white'}},
                gauge = {'axis': {'range': [None, 100]}, 'bar': {'color': "#00d2ff"}, 'bgcolor': "rgba(255,255,255,0.1)"}
            ))
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"}, height=250, margin=dict(l=20, r=20, t=50, b=20))
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Reasoning
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.write(f"**AI Reasoning:** {data.get('reasoning')}")
            st.write("**Key Indicators:**")
            for ind in data.get('fraud_indicators', []):
                st.write(f"- {ind}")
            st.markdown('</div>', unsafe_allow_html=True)