import numpy as np
import tensorflow as tf
import joblib

# Load model
model = tf.keras.models.load_model("models/ids_cnn_model.h5")

# Load scaler + encoder
scaler = joblib.load("models/scaler.pkl")
encoder = joblib.load("models/label_encoder.pkl")

print("[*] Live IDS Inference Started")

sample_flow = np.zeros((1, 78))

sample_flow[0][0] = 10.5
sample_flow[0][1] = 25
sample_flow[0][2] = 5000
sample_flow[0][3] = 200
sample_flow[0][4] = 2.3
sample_flow[0][5] = 450.2
sample_flow[0][6] = 3
sample_flow[0][7] = 10
sample_flow[0][8] = 0

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