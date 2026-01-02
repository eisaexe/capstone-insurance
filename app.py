import streamlit as st
import plotly.graph_objects as go
from agents.fraud_agent import check_fraud_risk
from agents.customer_agent import get_customer_response

st.set_page_config(page_title="Team 2 AI", layout="wide", page_icon="🛡️")

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
    color: white;
}
.glass-card {
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(10px);
    border-radius: 15px;
    border: 1px solid rgba(255,255,255,0.1);
    padding: 20px;
    margin-bottom: 20px;
}
h1, h2, h3, p, label { color: white !important; }
.stTextInput input, .stTextArea textarea {
    color: white;
    background-color: rgba(255,255,255,0.1);
}
.metric-val { font-size: 2rem; font-weight: bold; }
.metric-lbl { font-size: 0.9rem; color: #ccc; }
</style>
""", unsafe_allow_html=True)

if "auth_id" not in st.session_state:
    st.session_state.auth_id = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [{
        "role": "assistant",
        "content": "🔒 Authentication Required. Please enter your Customer ID."
    }]

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None

with st.sidebar:
    st.header("IntelliClaim AI")
    page = st.radio("Navigate", ["Officer Dashboard", "Customer Chat"])
    if st.session_state.auth_id:
        st.success(f"Logged in: {st.session_state.auth_id}")
        if st.button("Logout"):
            st.session_state.auth_id = None
            st.session_state.chat_history = [{
                "role": "assistant",
                "content": "🔒 Authentication Required. Please enter your Customer ID."
            }]
            st.rerun()

if page == "Customer Chat":
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if prompt := st.chat_input("Type your message"):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        response = get_customer_response(prompt, {"auth_id": st.session_state.auth_id})
        if isinstance(response, dict) and response.get("action") == "LOGIN":
            st.session_state.auth_id = response["user_id"]
            response = response["text"]
            st.rerun()

        st.session_state.chat_history.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.write(response)

else:
    st.markdown("<h2 style='text-align:center;'>👮 Claims Intelligence Dashboard</h2>", unsafe_allow_html=True)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("📄 Claim Intake")

    u1, u2, u3 = st.columns([2, 2, 1])

    with u1:
        rc_file = st.file_uploader("Upload RC Document", type=["pdf", "docx"])

    with u2:
        insurance_file = st.file_uploader("Upload Insurance Document", type=["pdf", "docx"])

    with u3:
        claim_amount = st.number_input("Claim Amount (₹)", min_value=0, step=1000, value=0)

    auto_data = {}
    if rc_file or insurance_file:
        auto_data = {
            "vehicle_number": "MH12AB1234",
            "cust_id": "CUST-2045",
            "name": "Rahul Sharma",
            "policy_type": "Zero Dep",
            "idv_value": 620000,
            "claim_history": 45000
        }
        st.success("Documents processed. Details auto-filled.")

    manual_override = st.checkbox("Manual Entry / Override")
    st.divider()

    r1c1, r1c2, r1c3 = st.columns(3)
    with r1c1:
        vehicle_number = st.text_input("Vehicle Number", auto_data.get("vehicle_number", "") if not manual_override else "")
    with r1c2:
        cust_id = st.text_input("Customer ID", auto_data.get("cust_id", "") if not manual_override else "")
    with r1c3:
        name = st.text_input("Customer Name", auto_data.get("name", "") if not manual_override else "")

    r2c1, r2c2, r2c3 = st.columns(3)
    with r2c1:
        policy_type = st.selectbox(
            "Policy Type",
            ["Zero Dep", "Standard"],
            index=["Zero Dep", "Standard"].index(auto_data.get("policy_type", "Zero Dep")) if auto_data and not manual_override else 0
        )
    with r2c2:
        idv_value = st.number_input("IDV Value (₹)", min_value=0, value=int(auto_data.get("idv_value", 0)) if not manual_override else 0)
    with r2c3:
        claim_history = st.number_input("Previous Claim Amount (₹)", min_value=0, value=int(auto_data.get("claim_history", 0)) if not manual_override else 0)

    if idv_value > 0 and claim_amount > idv_value:
        st.warning("⚠️ Claim amount exceeds IDV value")

    st.divider()

    claim_type = st.radio(
        "Claim Cause",
        ["Accidental Fire", "Theft", "Riot", "Accident", "Vehicle in Transit Accident"]
    )

    if claim_type == "Accidental Fire":
        st.file_uploader("Upload Fire Damage Image", type=["jpg", "jpeg", "png"])

    if claim_type == "Theft":
        st.file_uploader("Upload FIR Image", type=["jpg", "jpeg", "png", "pdf"])

    if claim_type == "Riot":
        st.file_uploader("Upload Riot Damage Image", type=["jpg", "jpeg", "png"])
        st.file_uploader("Upload FIR Image", type=["jpg", "jpeg", "png", "pdf"])

    if claim_type == "Accident":
        st.file_uploader("Upload Accident Image", type=["jpg", "jpeg", "png"])
        st.file_uploader("Upload FIR Image", type=["jpg", "jpeg", "png", "pdf"])

    if claim_type == "Vehicle in Transit Accident":
        st.file_uploader("Upload Transit Damage Image", type=["jpg", "jpeg", "png"])
        st.file_uploader("Upload FIR Image", type=["jpg", "jpeg", "png", "pdf"])

    st.markdown('</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        narrative = st.text_area("Incident Narrative", height=150)
        if st.button("Analyze Fraud Risk", use_container_width=True):
            st.session_state.analysis_result = check_fraud_risk(
                narrative=narrative,
                claim_amount=claim_amount,
                idv=idv_value,
                claim_history=claim_history
            )
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        if st.session_state.analysis_result:
            data = st.session_state.analysis_result
            a, b, c = st.columns(3)

            with a:
                st.markdown(f'<div class="glass-card"><div class="metric-lbl">RISK LEVEL</div><div class="metric-val">{data["risk_level"]}</div></div>', unsafe_allow_html=True)
            with b:
                st.markdown(f'<div class="glass-card"><div class="metric-lbl">FRAUD SCORE</div><div class="metric-val">{data["risk_score"]}</div></div>', unsafe_allow_html=True)
            with c:
                st.markdown(f'<div class="glass-card"><div class="metric-lbl">CONFIDENCE</div><div class="metric-val">95%</div></div>', unsafe_allow_html=True)

            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=data["risk_score"],
                gauge={"axis": {"range": [0, 100]}, "bar": {"color": "#00d2ff"}}
            ))
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font={"color": "white"}, height=250)
            st.plotly_chart(fig, use_container_width=True)
            st.write(f"**AI Reasoning:** {data['reasoning']}")
            for i in data.get("fraud_indicators", []):
                st.write(f"- {i}")
            st.markdown('</div>', unsafe_allow_html=True)
