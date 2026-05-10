import json
import time
from collections import defaultdict
from kafka import KafkaConsumer

# Kafka Consumer
consumer = KafkaConsumer(
    'network-traffic',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='latest',
    group_id='flow-builder-group',
    value_deserializer=lambda msg: json.loads(msg.decode('utf-8'))
)

print("[*] Flow Builder Started...")

# Store active flows
flows = {}

FLOW_TIMEOUT = 60  # seconds


def get_flow_key(data):
    return (
        data['src_ip'],
        data['dst_ip'],
        data['src_port'],
        data['dst_port'],
        data['protocol']
    )


def initialize_flow(data):
    return {
        'start_time': data['timestamp'],
        'last_seen': data['timestamp'],
        'packet_count': 0,
        'byte_count': 0,
        'packet_sizes': [],
        'flags': defaultdict(int)
    }


def update_flow(flow, data):
    flow['packet_count'] += 1
    flow['byte_count'] += data['length']
    flow['packet_sizes'].append(data['length'])
    flow['last_seen'] = data['timestamp']

    flag = data['flags']
    flow['flags'][flag] += 1


def compute_features(flow):
    duration = flow['last_seen'] - flow['start_time']

    avg_packet_size = (
        sum(flow['packet_sizes']) / len(flow['packet_sizes'])
        if flow['packet_sizes']
        else 0
    )

    packets_per_sec = (
        flow['packet_count'] / duration
        if duration > 0
        else 0
    )

    bytes_per_sec = (
        flow['byte_count'] / duration
        if duration > 0
        else 0
    )

    features = {
        'duration': duration,
        'packet_count': flow['packet_count'],
        'byte_count': flow['byte_count'],
        'avg_packet_size': avg_packet_size,
        'packets_per_sec': packets_per_sec,
        'bytes_per_sec': bytes_per_sec,
        'syn_flags': flow['flags'].get('S', 0),
        'ack_flags': flow['flags'].get('A', 0),
        'fin_flags': flow['flags'].get('F', 0)
    }

    return features


try:
    for message in consumer:

        data = message.value

        flow_key = get_flow_key(data)

        if flow_key not in flows:
            flows[flow_key] = initialize_flow(data)

        update_flow(flows[flow_key], data)

        current_time = time.time()

        expired_flows = []

        for key, flow in flows.items():

            if current_time - flow['last_seen'] > FLOW_TIMEOUT:

                features = compute_features(flow)

                print("\n[+] Flow Completed")
                print(f"Flow: {key}")
                print("Features:")

                for k, v in features.items():
                    print(f"  {k}: {v}")

                expired_flows.append(key)

        for key in expired_flows:
            del flows[key]

except KeyboardInterrupt:
    print("\n[!] Stopping Flow Builder...")