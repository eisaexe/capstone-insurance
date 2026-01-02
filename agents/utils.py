# FILE: agents/utils.py

import streamlit as st
import plotly.graph_objects as go

# -------------------------------------------------
# UI / STYLING UTILITIES (UNCHANGED)
# -------------------------------------------------

def inject_custom_css():
    st.markdown("""
    <style>
        /* 1. Main Background with Gradient */
        .stApp {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
        }

        /* 2. Glassmorphism Card Style */
        .glass-card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.18);
            padding: 20px;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
            margin-bottom: 20px;
        }

        /* 3. Metric Styling */
        .metric-value {
            font-size: 32px;
            font-weight: 800;
            -webkit-text-fill-color: white;
        }

        .metric-label {
            font-size: 14px;
            color: #d1d5db;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        /* 4. Chat Input Styling */
        .stChatInputContainer {
            background-color: rgba(255, 255, 255, 0.1) !important;
            border-radius: 15px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }

        /* 5. Sidebar Styling */
        section[data-testid="stSidebar"] {
            background-color: rgba(0, 0, 0, 0.2);
        }
    </style>
    """, unsafe_allow_html=True)


def render_metric_card(label, value, delta=None):
    delta_html = (
        f"<span style='color: #4ade80; font-size: 0.8rem;'>{delta}</span>"
        if delta else ""
    )

    st.markdown(f"""
    <div class="glass-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def create_gauge_chart(value, title):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': title, 'font': {'color': 'white'}},
        number={'font': {'color': 'white'}},
        gauge={
            'axis': {'range': [None, 100], 'tickcolor': "white"},
            'bar': {'color': "#00d2ff"},
            'bgcolor': "rgba(255,255,255,0.1)",
            'borderwidth': 0,
            'steps': [{'range': [0, 100], 'color': "rgba(0,0,0,0)"}],
        }
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': "white"}
    )
    return fig


# -------------------------------------------------
# TEXT FILE UTILITIES (NEW – REQUIRED FOR CLEAN ARCH)
# -------------------------------------------------

def load_text_file(path: str) -> str:
    """
    Generic utility to load a TXT document safely.
    Used for insurance policy text or future documents.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        return ""
