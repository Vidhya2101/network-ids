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

    "Flow Duration": 10.5,

    "Total Fwd Packets": 25,

    "Total Backward Packets": 10,

    "Total Length of Fwd Packets": 5000,

    "Total Length of Bwd Packets": 2000,

    "Packet Length Mean": 200,

    "Packet Length Std": 45,

    "Max Packet Length": 512,

    "Min Packet Length": 40,

    "Flow Bytes/s": 450.2,

    "Flow Packets/s": 2.3,

    "Flow IAT Mean": 0.12,

    "Flow IAT Std": 0.05,

    "Flow IAT Max": 0.20,

    "Flow IAT Min": 0.01,

    "SYN Flag Count": 3,

    "ACK Flag Count": 10,

    "FIN Flag Count": 0,

    "RST Flag Count": 0,

    "PSH Flag Count": 1
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
#background = np.zeros((10, 78, 1))
background = np.zeros((10, 20, 1))

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
from cicids_feature_map import FEATURE_COLUMNS

feature_names = FEATURE_COLUMNS

print("\n[+] Top Contributing Features")

# Print top implemented features
num_features = min(len(feature_names), len(values))

for i in range(num_features):

    print(
        f"{feature_names[i]} : "
        f"{values[i]:.6f}"
    )