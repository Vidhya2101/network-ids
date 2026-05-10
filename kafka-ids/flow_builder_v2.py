import json
import time
import numpy as np

from kafka import KafkaConsumer, KafkaProducer

# =========================================================
# Kafka Consumer
# =========================================================

consumer = KafkaConsumer(
    'network-traffic',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='latest',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

# =========================================================
# Kafka Producer
# =========================================================

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda x: json.dumps(x).encode('utf-8')
)

# =========================================================
# Flow Storage
# =========================================================

flows = {}

FLOW_TIMEOUT = 15

print("[*] Advanced Flow Builder Started")


# =========================================================
# Compute CICIDS-style Features
# =========================================================

def compute_features(flow):

    # -----------------------------------------------------
    # Duration
    # -----------------------------------------------------

    duration = flow["last_seen"] - flow["start_time"]

    if duration <= 0:
        duration = 1e-6

    # -----------------------------------------------------
    # Packet Length Statistics
    # -----------------------------------------------------

    lengths = np.array(flow["packet_lengths"])

    packet_length_mean = np.mean(lengths)
    packet_length_std = np.std(lengths)
    packet_length_max = np.max(lengths)
    packet_length_min = np.min(lengths)

    # -----------------------------------------------------
    # Inter Arrival Time (IAT)
    # -----------------------------------------------------

    timestamps = np.array(flow["timestamps"])

    iat = np.diff(timestamps)

    if len(iat) > 0:

        flow_iat_mean = np.mean(iat)
        flow_iat_std = np.std(iat)
        flow_iat_max = np.max(iat)
        flow_iat_min = np.min(iat)

    else:

        flow_iat_mean = 0
        flow_iat_std = 0
        flow_iat_max = 0
        flow_iat_min = 0

    # -----------------------------------------------------
    # Traffic Rates
    # -----------------------------------------------------

    total_bytes = (
        flow["fwd_bytes"] +
        flow["bwd_bytes"]
    )

    total_packets = (
        flow["fwd_packets"] +
        flow["bwd_packets"]
    )

    flow_bytes_per_sec = total_bytes / duration

    flow_packets_per_sec = total_packets / duration

    # -----------------------------------------------------
    # Final Feature Dictionary
    # -----------------------------------------------------

    features = {

        "Flow Duration":
            duration,

        "Total Fwd Packets":
            flow["fwd_packets"],

        "Total Backward Packets":
            flow["bwd_packets"],

        "Total Length of Fwd Packets":
            flow["fwd_bytes"],

        "Total Length of Bwd Packets":
            flow["bwd_bytes"],

        "Packet Length Mean":
            packet_length_mean,

        "Packet Length Std":
            packet_length_std,

        "Max Packet Length":
        packet_length_max,

        "Min Packet Length":
        packet_length_min,

        "Flow Bytes/s":
            flow_bytes_per_sec,

        "Flow Packets/s":
            flow_packets_per_sec,

        "Flow IAT Mean":
            flow_iat_mean,

        "Flow IAT Std":
            flow_iat_std,

        "Flow IAT Max":
            flow_iat_max,

        "Flow IAT Min":
            flow_iat_min,

        "SYN Flag Count":
            flow["syn_count"],

        "ACK Flag Count":
            flow["ack_count"],

        "FIN Flag Count":
            flow["fin_count"],

        "RST Flag Count":
            flow["rst_count"],

        "PSH Flag Count":
            flow["psh_count"]
    }

    return features


# =========================================================
# Main Consumer Loop
# =========================================================

try:

    for message in consumer:

        packet = message.value

        src_ip = packet["src_ip"]
        dst_ip = packet["dst_ip"]

        src_port = packet["src_port"]
        dst_port = packet["dst_port"]

        protocol = packet["protocol"]

        length = packet["length"]

        flags = packet["flags"]

        timestamp = packet["timestamp"]

        # -------------------------------------------------
        # Create Flow ID
        # -------------------------------------------------

        flow_id = (
            src_ip,
            dst_ip,
            src_port,
            dst_port,
            protocol
        )

        # -------------------------------------------------
        # Create New Flow
        # -------------------------------------------------

        if flow_id not in flows:

            flows[flow_id] = {

                "start_time": timestamp,
                "last_seen": timestamp,

                "fwd_packets": 0,
                "bwd_packets": 0,

                "fwd_bytes": 0,
                "bwd_bytes": 0,

                "packet_lengths": [],
                "timestamps": [],

                "syn_count": 0,
                "ack_count": 0,
                "fin_count": 0,
                "rst_count": 0,
                "psh_count": 0
            }

        flow = flows[flow_id]

        # -------------------------------------------------
        # Update Flow Time
        # -------------------------------------------------

        flow["last_seen"] = timestamp

        # -------------------------------------------------
        # Packet Statistics
        # -------------------------------------------------

        flow["packet_lengths"].append(length)

        flow["timestamps"].append(timestamp)

        # -------------------------------------------------
        # Directional Traffic
        # -------------------------------------------------

        if src_ip == flow_id[0]:

            flow["fwd_packets"] += 1
            flow["fwd_bytes"] += length

        else:

            flow["bwd_packets"] += 1
            flow["bwd_bytes"] += length

        # -------------------------------------------------
        # TCP Flags
        # -------------------------------------------------

        if "S" in flags:
            flow["syn_count"] += 1

        if "A" in flags:
            flow["ack_count"] += 1

        if "F" in flags:
            flow["fin_count"] += 1

        if "R" in flags:
            flow["rst_count"] += 1

        if "P" in flags:
            flow["psh_count"] += 1

        # -------------------------------------------------
        # Expire Old Flows
        # -------------------------------------------------

        expired_flows = []

        current_time = time.time()

        for fid, f in flows.items():

            if current_time - f["last_seen"] > FLOW_TIMEOUT:

                features = compute_features(f)

                print("\n[+] Flow Completed")
                print("Flow:", fid)

                print("\nFeatures:")

                for k, v in features.items():

                    print(f"  {k}: {v}")

                # -----------------------------------------
                # Send to Kafka Topic
                # -----------------------------------------

                producer.send(
                    'flow-features',
                    value=features
                )

                producer.flush()

                expired_flows.append(fid)

        # Remove expired flows
        for fid in expired_flows:

            del flows[fid]

except KeyboardInterrupt:

    print("\n[!] Stopping Flow Builder")

    consumer.close()

    producer.close()

    print("[*] Shutdown Complete")