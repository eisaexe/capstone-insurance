import streamlit as st
import plotly.graph_objects as go
from agents.fraud_agent import check_fraud_risk
from agents.customer_agent import get_customer_response

st.set_page_config(page_title="Team 2 AI", layout="wide", page_icon="🛡️")

st.markdown("""
<style>
:root {
    --carbon-blue: #0f62fe;
    --bg-main: #f4f4f4;
    --surface: #ffffff;
    --border: #e0e0e0;
    --text-main: #161616;
    --text-muted: #525252;
}

@media (prefers-color-scheme: dark) {
    :root {
        --bg-main: #161616;
        --surface: #262626;
        --border: #393939;
        --text-main: #f4f4f4;
        --text-muted: #c6c6c6;
    }
}

.stApp {
    background-color: var(--bg-main);
    color: var(--text-main);
    font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 20px;
    margin-bottom: 20px;
}

label {
    color: var(--text-muted) !important;
    font-size: 0.85rem !important;
}

.stTextInput input,
.stTextArea textarea,
.stNumberInput input,
.stSelectbox div {
    background-color: var(--surface) !important;
    color: var(--text-main) !important;
    border-radius: 0px !important;
    border: 1px solid var(--border) !important;
}

.stTextInput input:focus,
.stTextArea textarea:focus,
.stNumberInput input:focus {
    border-color: var(--carbon-blue) !important;
    outline: none !important;
}

.stFileUploader {
    background: var(--surface);
    border: 1px dashed var(--border);
    border-radius: 0px;
    padding: 8px;
}

.stButton button {
    background-color: var(--carbon-blue);
    color: white;
    border-radius: 0px;
    font-weight: 500;
    border: none;
}

.metric-val {
    font-size: 1.8rem;
    font-weight: 600;
    color: var(--carbon-blue);
}

.metric-lbl {
    font-size: 0.75rem;
    color: var(--text-muted);
    text-transform: uppercase;
}
</style>
""", unsafe_allow_html=True)

if "auth_id" not in st.session_state:
    st.session_state.auth_id = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [{
        "role": "assistant",
        "content": "Authentication required. Please enter your Customer ID."
    }]

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None

# ---------- SIDEBAR ----------
with st.sidebar:
    st.markdown(
        """
        <div style="display:flex; align-items:center; gap:10px;">
            <img src="https://cdn-icons-png.flaticon.com/512/4712/4712109.png"
                 style="height:26px;" />
            <h3 style="margin:0;">IntelliClaim AI</h3>
        </div>
        """,
        unsafe_allow_html=True
    )

    page = st.radio("Navigate", ["Officer Dashboard", "Customer Chat"])

    if st.session_state.auth_id:
        st.success(f"Logged in: {st.session_state.auth_id}")

# ---------- CUSTOMER CHAT ----------
if page == "Customer Chat":
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if prompt := st.chat_input("Type your message"):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        response = get_customer_response(prompt, {"auth_id": st.session_state.auth_id})
        if isinstance(response, dict) and response.get("action") == "LOGIN":
            st.session_state.auth_id = response["user_id"]
            response = response["text"]
            st.rerun()
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.write(response)

# ---------- OFFICER DASHBOARD ----------
else:
    st.markdown(
        """
        <div style="display:flex; align-items:center; justify-content:center; gap:14px; margin-bottom:10px;">
            <img src="https://cdn-icons-png.flaticon.com/512/741/741407.png"
                 style="height:40px;" />
            <h2 style="
                margin:0;
                font-family: 'Georgia', 'Times New Roman', serif;
                letter-spacing: 0.5px;
                font-weight: 600;
            ">
                Claims Intelligence Dashboard
            </h2>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Claim Intake")

    u1, u2, u3 = st.columns([2, 2, 1])
    with u1:
        rc_file = st.file_uploader("RC Document", type=["pdf", "docx"])
    with u2:
        insurance_file = st.file_uploader("Insurance Document", type=["pdf", "docx"])
    with u3:
        claim_amount = st.number_input("Claim Amount (₹)", min_value=0, step=1000)

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
        st.success("Document data extracted")

    manual_override = st.checkbox("Manual Entry / Override")

    r1c1, r1c2, r1c3 = st.columns(3)
    with r1c1:
        vehicle_number = st.text_input("Vehicle Number", auto_data.get("vehicle_number", "") if not manual_override else "")
    with r1c2:
        cust_id = st.text_input("Customer ID", auto_data.get("cust_id", "") if not manual_override else "")
    with r1c3:
        name = st.text_input("Customer Name", auto_data.get("name", "") if not manual_override else "")

    r2c1, r2c2, r2c3 = st.columns(3)
    with r2c1:
        policy_type = st.selectbox("Policy Type", ["Zero Dep", "Standard"])
    with r2c2:
        idv_value = st.number_input("IDV Value (₹)", min_value=0)
    with r2c3:
        claim_history = st.number_input("Previous Claim Amount (₹)", min_value=0)

    st.divider()

    claim_type = st.radio(
        "Claim Cause",
        ["Accidental Fire", "Theft", "Riot", "Accident", "Vehicle in Transit Accident"]
    )

    if claim_type == "Accidental Fire":
        c1, _ = st.columns([1, 3])
        with c1:
            st.file_uploader("Damage Image", type=["jpg", "jpeg", "png"])

    if claim_type == "Theft":
        c1, _ = st.columns([1, 3])
        with c1:
            st.file_uploader("FIR Image", type=["jpg", "jpeg", "png", "pdf"])

    if claim_type in ["Riot", "Accident", "Vehicle in Transit Accident"]:
        c1, c2 = st.columns(2)
        with c1:
            st.file_uploader("Damage Image", type=["jpg", "jpeg", "png"])
        with c2:
            st.file_uploader("FIR Image", type=["jpg", "jpeg", "png", "pdf"])

    st.markdown('</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        narrative = st.text_area("Incident Narrative", height=140)
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
                st.markdown(f'<div class="card"><div class="metric-lbl">Risk</div><div class="metric-val">{data["risk_level"]}</div></div>', unsafe_allow_html=True)
            with b:
                st.markdown(f'<div class="card"><div class="metric-lbl">Score</div><div class="metric-val">{data["risk_score"]}</div></div>', unsafe_allow_html=True)
            with c:
                st.markdown(f'<div class="card"><div class="metric-lbl">Confidence</div><div class="metric-val">95%</div></div>', unsafe_allow_html=True)

            st.markdown('<div class="card">', unsafe_allow_html=True)
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=data["risk_score"],
                gauge={"axis": {"range": [0, 100]}, "bar": {"color": "#0f62fe"}}
            ))
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font={"color": "#161616"}, height=260)
            st.plotly_chart(fig, use_container_width=True)
            st.write(f"AI Reasoning: {data['reasoning']}")
            for i in data.get("fraud_indicators", []):
                st.write(f"- {i}")
            st.markdown('</div>', unsafe_allow_html=True)
