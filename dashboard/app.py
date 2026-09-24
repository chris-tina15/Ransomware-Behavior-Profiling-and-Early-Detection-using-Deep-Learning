import sys
import os
import json
import time
import torch
import joblib
import streamlit as st
import numpy as np
import plotly.graph_objects as go
from pathlib import Path

# ================= FIX MODULE PATH =================
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(ROOT_DIR)

from src.model.transformer import BehavioralTransformer
from src.encoding.event_vocab import EventVocab

# ================= CONFIG =================
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
MAX_LEN = 256
PREFIXES = [64, 128, 256]
THRESHOLD = 0.5

SELECTED_FEATURES = [
    "pslist.nproc","pslist.avg_threads","handles.nhandles","handles.nfile",
    "handles.nkey","dlllist.ndlls","ldrmodules.not_in_load",
    "psxview.not_in_pslist","psxview.not_in_session",
    "malfind.ninjections","malfind.uniqueInjections","svcscan.nservices",
]

st.set_page_config(page_title="Ransomware Early Detection", layout="wide")

# ================= LOAD MODEL + SCALER =================
@st.cache_resource
def load_resources():
    vocab = EventVocab()

    model = BehavioralTransformer(
        vocab_size=len(vocab.token2id),
        num_features=len(SELECTED_FEATURES),
        max_len=MAX_LEN
    ).to(DEVICE)

    model.load_state_dict(
        torch.load("models/transformer.pt", map_location=DEVICE)
    )
    model.eval()

    scaler = joblib.load("models/scaler.pkl")

    return model, vocab, scaler

model, vocab, scaler = load_resources()

# ================= TITLE =================
st.title("🛡️ Transformer-Based Ransomware Early Detection")
st.caption("Hybrid Behavioral & Memory-Forensic Analysis")

# ================= SIDEBAR =================
st.sidebar.header("Input Selection")

mode = st.sidebar.radio(
    "Choose Input Mode",
    ["Use Dataset Sample", "Upload JSON File"]
)

scenario = st.sidebar.selectbox(
    "Select Sample Type",
    ["ransomware", "benign"]
)

uploaded_file = st.sidebar.file_uploader(
    "Upload JSON File",
    type=["json"]
)

run_btn = st.sidebar.button("▶ Run Detection")

# ================= SAMPLE LOADER =================
def load_dataset_sample(sample_type):
    files = list(Path(f"data/processed/sequences/{sample_type}").glob("*.json"))
    return json.load(open(files[0]))

# ================= GAUGE FUNCTION =================
def render_gauge(value):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value * 100,
        title={'text': "Ransomware Risk (%)"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "red" if value > THRESHOLD else "green"},
            'steps': [
                {'range': [0, 50], 'color': "#d4edda"},
                {'range': [50, 100], 'color': "#f8d7da"}
            ],
        }
    ))
    fig.update_layout(height=280)
    return fig

# ================= MAIN =================
if run_btn:

    # -------- Load Input --------
    if mode == "Use Dataset Sample":
        sample = load_dataset_sample(scenario)

    elif mode == "Upload JSON File" and uploaded_file:
        sample = json.load(uploaded_file)

    else:
        st.warning("Please select or upload a valid JSON file.")
        st.stop()

    sequence = sample["sequence"]
    features = sample["features"]

    st.subheader("📜 Behavioral Event Stream")
    event_box = st.empty()

    st.subheader("🔄 Live Detection Engine")

    progress_bar = st.progress(0)
    status_text = st.empty()
    prefix_counter = st.empty()

    col1, col2 = st.columns(2)
    gauge_placeholder = col1.empty()
    chart_placeholder = col2.empty()

    risk_scores = []
    prefix_labels = []

    total_steps = len(PREFIXES)

    for i, prefix in enumerate(PREFIXES):

        status_text.info("Analyzing behavioral evidence...")
        prefix_counter.write(f"Current Prefix Length: {prefix} events")

        partial_seq = sequence[:prefix]
        encoded = vocab.encode(partial_seq)

        if len(encoded) < MAX_LEN:
            encoded += [0] * (MAX_LEN - len(encoded))
        encoded = encoded[:MAX_LEN]

        x_seq = torch.tensor([encoded], dtype=torch.long).to(DEVICE)

        feature_vector = [features.get(k, 0.0) for k in SELECTED_FEATURES]
        scaled = scaler.transform([feature_vector])
        x_feat = torch.tensor(scaled, dtype=torch.float).to(DEVICE)

        with torch.no_grad():
            logits = model(x_seq, x_feat)
            probs = torch.softmax(logits, dim=1)
            ransomware_prob = probs[0, 1].item()

        risk_scores.append(ransomware_prob)
        prefix_labels.append(prefix)

        # Update event stream
        event_box.code("\n".join(partial_seq[:15]))

        # Update progress bar
        progress_bar.progress((i + 1) / total_steps)

        # Update gauge
        gauge_placeholder.plotly_chart(
            render_gauge(ransomware_prob),
            use_container_width=True
        )

        # === PREFIX PROGRESSION GRAPH ===
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=prefix_labels,
            y=risk_scores,
            mode="lines+markers",
            line=dict(
                color="red" if ransomware_prob > THRESHOLD else "green",
                width=3
            ),
            name="Ransomware Probability"
        ))

        fig.add_trace(go.Scatter(
            x=PREFIXES,
            y=[THRESHOLD]*len(PREFIXES),
            mode="lines",
            line=dict(dash="dash", color="orange"),
            name="Detection Threshold"
        ))

        fig.update_layout(
            xaxis_title="Prefix Length",
            yaxis_title="Probability",
            yaxis=dict(range=[0, 1]),
            transition=dict(duration=500),
            template="plotly_white"
        )

        chart_placeholder.plotly_chart(fig, use_container_width=True)

        time.sleep(1)

    status_text.success("Analysis Complete")

    # ================= FINAL RESULT =================
    final_score = risk_scores[-1]

    st.divider()
    st.subheader("🔍 Final Classification")
    
    colA, colB = st.columns(2)

    colA.metric("Ransomware Probability", f"{final_score:.3f}")
    colB.metric("Benign Probability", f"{1 - final_score:.3f}")

    if final_score > THRESHOLD:
        st.error("⚠️ Ransomware Behavior Detected")
    else:
        st.success("✅ Benign Behavior Detected")

    st.caption(
        "Detection performed using progressive prefix-based behavioral and forensic feature fusion."
    )
