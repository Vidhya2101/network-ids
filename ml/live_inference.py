import numpy as np
import tensorflow as tf
import joblib

# Load model
model = tf.keras.models.load_model("models/ids_cnn_model.h5")

# Load scaler + encoder
scaler = joblib.load("models/scaler.pkl")
encoder = joblib.load("models/label_encoder.pkl")

print("[*] Live IDS Inference Started")

from feature_alignment import build_feature_vector

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

sample_flow = build_feature_vector(sample_flow_features)

# Scale features
sample_flow_scaled = scaler.transform(sample_flow)

# Reshape for CNN
sample_flow_scaled = sample_flow_scaled.reshape(
    sample_flow_scaled.shape[0],
    sample_flow_scaled.shape[1],
    1
)

# Predict
prediction = model.predict(sample_flow_scaled)

predicted_class = np.argmax(prediction)
confidence = np.max(prediction)

label = encoder.inverse_transform([predicted_class])[0]

print("\n[+] Prediction Result")
print(f"Attack Type : {label}")
print(f"Confidence  : {confidence:.4f}")