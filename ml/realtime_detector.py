import json
import numpy as np
import tensorflow as tf
import joblib
from kafka import KafkaConsumer, KafkaProducer

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
# Kafka Consumer
# -----------------------------
consumer = KafkaConsumer(
    'flow-features',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='latest',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

# -----------------------------
# Kafka Producer
# -----------------------------
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda x: json.dumps(x).encode('utf-8')
)

print("[*] Real-Time IDS Detector Started")

# -----------------------------
# Process flows
# -----------------------------
for message in consumer:

    flow_features = message.value

    # Build aligned vector
    feature_vector = build_feature_vector(
        flow_features
    )

    # Scale
    feature_vector = scaler.transform(
        feature_vector
    )

    # Reshape
    feature_vector = feature_vector.reshape(
        feature_vector.shape[0],
        feature_vector.shape[1],
        1
    )

    # Predict
    prediction = model.predict(
        feature_vector,
        verbose=0
    )

    predicted_class = np.argmax(prediction)
    confidence = float(np.max(prediction))

    attack_label = encoder.inverse_transform(
        [predicted_class]
    )[0]

    result = {
        "attack_type": attack_label,
        "confidence": confidence,
        "flow_features": flow_features
    }

    print("\n[+] IDS Alert")
    print(result)

    # Send alert to dashboard topic
    producer.send(
        'ids-alerts',
        value=result
    )

    producer.flush()