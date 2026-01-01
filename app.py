import streamlit as st

# Sidebar for navigation between the two project tracks
page = st.sidebar.radio("Select View", ["Customer Support (Chat)", "Officer Dashboard (Internal)"])

if page == "Officer Dashboard (Internal)":
    st.title("🛡️ Claims Intelligence Platform")
    
    # 1. Upload Section [cite: 52]
    uploaded_file = st.file_uploader("Upload Claim Document", type=["pdf", "docx", "txt"])
    
    # 2. Analysis Section (Business Track)
    col1, col2, col3 = st.columns(3)
    col1.metric("Fraud Risk Score", "High", "85%")  # [cite: 71]
    col2.metric("Policy Match", "Review Needed", "-15%") # [cite: 72]
    col3.metric("Urgency", "Immediate", "High") # [cite: 47]

    st.subheader("⚠️ Detected Anomalies")
    st.warning("Claimant location matches 3 previous fraud cases. [cite: 21]")
    
    # 3. Human-in-the-loop [cite: 68]
    st.divider()
    decision = st.radio("Officer Decision:", ["Approve", "Reject", "Request More Info"])
    if st.button("Submit Decision"):
        st.success(f"Claim processed as: {decision}")

elif page == "Customer Support (Chat)":
    st.title("💬 Insurance Assistant")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input [cite: 78]
    if prompt := st.chat_input("Check my claim status..."):
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        # Add to history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # (Connect your OpenAI 'Customer Track' agent here)
        response = "Your claim #123 is currently under review. We need a document verification."
        
        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})