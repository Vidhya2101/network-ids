import json
from kafka import KafkaConsumer

# ─────────────────────────────────────────────
# Connect to Kafka and subscribe to the topic
#
# auto_offset_reset='earliest' means:
#   "If I'm new here, start reading from the very first message"
#   (vs 'latest' which means "only show me new messages going forward")
#
# value_deserializer does the reverse of the producer:
#   bytes → JSON string → Python dict
# ─────────────────────────────────────────────
consumer = KafkaConsumer(
    'network-traffic',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',
    group_id='ids-consumer-group',        # Identifies this consumer group
    value_deserializer=lambda msg: json.loads(msg.decode('utf-8'))
)

print("[*] Consumer connected. Waiting for messages...\n")

# Loop forever, reading one message at a time
# for message in consumer:
#     data = message.value   # This is already a Python dict (deserialised)

#     print("─" * 55)
#     print(f"  src_ip    : {data['src_ip']}")
#     print(f"  dst_ip    : {data['dst_ip']}")
#     print(f"  protocol  : {data['protocol']}")
#     print(f"  src_port  : {data['src_port']}")
#     print(f"  dst_port  : {data['dst_port']}")
#     print(f"  length    : {data['length']} bytes")
#     print(f"  flags     : {data['flags']}")
#     print(f"  timestamp : {data['timestamp']}")
try:
    for message in consumer:
        data = message.value

        print("─" * 55)
        print(f"  src_ip    : {data['src_ip']}")
        print(f"  dst_ip    : {data['dst_ip']}")
        print(f"  protocol  : {data['protocol']}")
        print(f"  src_port  : {data['src_port']}")
        print(f"  dst_port  : {data['dst_port']}")
        print(f"  length    : {data['length']} bytes")
        print(f"  flags     : {data['flags']}")
        print(f"  timestamp : {data['timestamp']}")

except KeyboardInterrupt:
    print("\n[!] Stopping consumer...")
    consumer.close()
    print("[*] Consumer shut down cleanly.")