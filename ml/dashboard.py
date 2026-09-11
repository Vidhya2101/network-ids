import streamlit as st
import pandas as pd
import numpy as np
import tensorflow as tf
import joblib
import shap
from kafka import KafkaConsumer
import json

from feature_alignment import build_feature_vector
from cicids_feature_map import FEATURE_COLUMNS

# -----------------------------
# Load model + preprocessing
# -----------------------------
model = tf.keras.models.load_model("models/ids_cnn_model.h5")
scaler = joblib.load("models/scaler.pkl")
encoder = joblib.load("models/label_encoder.pkl")

# -----------------------------
# Kafka Consumer
# -----------------------------
consumer = KafkaConsumer(
    'ids-alerts',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='latest',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

# -----------------------------
# Streamlit UI setup
# -----------------------------
st.set_page_config(page_title="Real-Time IDS Dashboard", layout="wide")
st.title("🚨 Real-Time Intrusion Detection System")
st.markdown("---")

if "alert_log" not in st.session_state:
    st.session_state.alert_log = []

prediction_placeholder = st.empty()
shap_placeholder = st.empty()
flow_placeholder = st.empty()
alerts_placeholder = st.empty()

# SHAP background reference (zeros, matching real feature count)
background = np.zeros((10, len(FEATURE_COLUMNS), 1))
explainer = shap.GradientExplainer(model, background)

# -----------------------------
# Live loop — runs on every real alert
# -----------------------------
for message in consumer:

    alert = message.value
    attack_type = alert["attack_type"]
    confidence = alert["confidence"]
    flow_features = alert["flow_features"]

    # ---- Prediction Result ----
    with prediction_placeholder.container():
        st.subheader("📌 Prediction Result")
        col1, col2 = st.columns(2)
        col1.metric("Attack Type", attack_type)
        col2.metric("Confidence", f"{confidence:.4f}")

    # ---- Rebuild vector for SHAP explanation ----
    vector = build_feature_vector(flow_features)
    vector_scaled = scaler.transform(vector)
    vector_scaled = vector_scaled.reshape(
        vector_scaled.shape[0], vector_scaled.shape[1], 1
    )

    shap_values = explainer.shap_values(vector_scaled)
    values = np.abs(shap_values[0]).reshape(-1)

    importance_df = pd.DataFrame({
        "Feature": FEATURE_COLUMNS,
        "Importance": values[:len(FEATURE_COLUMNS)]
    }).sort_values(by="Importance", ascending=False)

    with shap_placeholder.container():
        st.subheader("🔍 SHAP Feature Importance")
        st.dataframe(importance_df)

    # ---- Live Flow Statistics ----
    with flow_placeholder.container():
        st.subheader("📡 Live Flow Statistics")
        st.json(flow_features)

    # ---- Track malicious flows only ----
    if attack_type != "BENIGN":
        st.session_state.alert_log.insert(0, {
            "Attack Type": attack_type,
            "Confidence": f"{confidence:.4f}",
            **flow_features
        })

    with alerts_placeholder.container():
        st.subheader("🚨 Live IDS Alerts (Malicious Only)")
        if st.session_state.alert_log:
            st.dataframe(pd.DataFrame(st.session_state.alert_log))
        else:
            st.info("No malicious flows detected yet.")