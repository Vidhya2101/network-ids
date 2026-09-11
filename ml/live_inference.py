import numpy as np
import tensorflow as tf
import joblib

model = tf.keras.models.load_model("models/ids_cnn_model.h5")
scaler = joblib.load("models/scaler.pkl")
encoder = joblib.load("models/label_encoder.pkl")

print("[*] Live IDS Inference Started")

from feature_alignment import build_feature_vector

sample_flow_features = {
    "Flow Duration": 10.5,
    "Total Fwd Packets": 15,
    "Total Backward Packets": 10,
    "Total Length of Fwd Packets": 3000,
    "Total Length of Bwd Packets": 2000,
    "Packet Length Mean": 200,
    "Packet Length Std": 45.2,
    "Max Packet Length": 500,
    "Min Packet Length": 60,
    "Flow Bytes/s": 476.2,
    "Flow Packets/s": 2.38,
    "Flow IAT Mean": 0.42,
    "Flow IAT Std": 0.11,
    "Flow IAT Max": 0.9,
    "Flow IAT Min": 0.05,
    "SYN Flag Count": 3,
    "ACK Flag Count": 10,
    "FIN Flag Count": 0,
    "RST Flag Count": 0,
    "PSH Flag Count": 5
}

sample_flow = build_feature_vector(sample_flow_features)

sample_flow_scaled = scaler.transform(sample_flow)

sample_flow_scaled = sample_flow_scaled.reshape(
    sample_flow_scaled.shape[0],
    sample_flow_scaled.shape[1],
    1
)

prediction = model.predict(sample_flow_scaled)

predicted_class = np.argmax(prediction)
confidence = np.max(prediction)

label = encoder.inverse_transform([predicted_class])[0]

print("\n[+] Prediction Result")
print(f"Attack Type : {label}")
print(f"Confidence  : {confidence:.4f}")