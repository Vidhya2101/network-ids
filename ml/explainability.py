import shap
import numpy as np
import tensorflow as tf
import joblib

from feature_alignment import build_feature_vector

# Load trained model
model = tf.keras.models.load_model("models/ids_cnn_model.h5")

# Load scaler
scaler = joblib.load("models/scaler.pkl")

print("[*] SHAP Explainability Started")

# Example live flow
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

# Build aligned vector
sample_flow = build_feature_vector(sample_flow_features)

# Scale
sample_flow_scaled = scaler.transform(sample_flow)

# Reshape for CNN
sample_flow_scaled = sample_flow_scaled.reshape(
    sample_flow_scaled.shape[0],
    sample_flow_scaled.shape[1],
    1
)

# Background data for SHAP
background = np.zeros((10, 78, 1))

# Create explainer
explainer = shap.GradientExplainer(
    model,
    background
)

# Compute SHAP values
shap_values = explainer.shap_values(sample_flow_scaled)

# Extract SHAP values safely
values = np.abs(shap_values[0])

# Flatten if needed
values = values.reshape(-1)

print(f"\n[*] SHAP values shape: {values.shape}")

# Feature names
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

print("\n[+] Top Contributing Features")

# Print top implemented features
num_features = min(len(feature_names), len(values))

for i in range(num_features):

    print(
        f"{feature_names[i]} : "
        f"{values[i]:.6f}"
    )