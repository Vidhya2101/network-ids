import streamlit as st
import pandas as pd
import numpy as np
import tensorflow as tf
import joblib
import shap
from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    'ids-alerts',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='latest',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)


from feature_alignment import build_feature_vector

# -----------------------------
# Load model + preprocessing
# -----------------------------
model = tf.keras.models.load_model(
    "models/ids_cnn_model.h5"
)

scaler = joblib.load(
    "models/scaler.pkl"
)

encoder = joblib.load(
    "models/label_encoder.pkl"
)

# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(
    page_title="Real-Time IDS Dashboard",
    layout="wide"
)

st.title("🚨 Real-Time Intrusion Detection System")

st.markdown("---")

# -----------------------------
# Example Live Flow
# -----------------------------
sample_flow_features = {
    "duration": 10.5,
    "packet_count": 25,
    "byte_count": 5000,
    "avg_packet_size": 200,
    "packets_per_sec": 2.3,
    "bytes_per_sec": 450.2,
    "syn_flags": 3,
    "ack_flags": 10,
    "fin_flags": 0
}

# Build feature vector
sample_flow = build_feature_vector(
    sample_flow_features
)

# Scale
sample_flow_scaled = scaler.transform(
    sample_flow
)

# Reshape
sample_flow_scaled = sample_flow_scaled.reshape(
    sample_flow_scaled.shape[0],
    sample_flow_scaled.shape[1],
    1
)

# -----------------------------
# Prediction
# -----------------------------
prediction = model.predict(
    sample_flow_scaled
)

predicted_class = np.argmax(prediction)
confidence = np.max(prediction)

attack_label = encoder.inverse_transform(
    [predicted_class]
)[0]

# -----------------------------
# Display Prediction
# -----------------------------
st.subheader("📌 Prediction Result")

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "Attack Type",
        attack_label
    )

with col2:
    st.metric(
        "Confidence",
        f"{confidence:.4f}"
    )

st.markdown("---")

# -----------------------------
# SHAP Explainability
# -----------------------------
st.subheader("🔍 SHAP Feature Importance")

background = np.zeros((10, 20, 1))

explainer = shap.GradientExplainer(
    model,
    background
)

shap_values = explainer.shap_values(
    sample_flow_scaled
)

values = np.abs(
    shap_values[0]
).reshape(-1)

feature_names = [
    "duration",
    "packet_count",
    "byte_count",
    "avg_packet_size",
    "packets_per_sec",
    "bytes_per_sec",
    "syn_flags",
    "ack_flags",
    "fin_flags"
]

importance_df = pd.DataFrame({
    "Feature": feature_names,
    "Importance": values[:len(feature_names)]
})

st.dataframe(
    importance_df.sort_values(
        by="Importance",
        ascending=False
    )
)

st.markdown("---")

# -----------------------------
# Raw Flow Data
# -----------------------------
st.subheader("📡 Live Flow Statistics")

st.json(sample_flow_features)

st.subheader("🚨 Live IDS Alerts")

alert_placeholder = st.empty()

for message in consumer:

    alert = message.value

    attack_type = alert['attack_type']
    confidence = alert['confidence']

    alert_placeholder.error(
        f"Attack: {attack_type} | Confidence: {confidence:.4f}"
    )