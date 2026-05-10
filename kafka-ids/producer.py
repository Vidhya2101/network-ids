import json
import time
from scapy.all import sniff, IP, TCP, UDP
from kafka import KafkaProducer

# ─────────────────────────────────────────────
# STEP 1: Connect to Kafka
# KafkaProducer is your "letter writer + sender"
# value_serializer converts Python dict → JSON bytes automatically
# ─────────────────────────────────────────────
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda msg: json.dumps(msg).encode('utf-8')
)

print("[*] Kafka producer connected. Starting packet capture...")


# ─────────────────────────────────────────────
# STEP 2: Define what to do with each packet
# This function is called by Scapy for every captured packet
# ─────────────────────────────────────────────
def process_packet(packet):
    # Only process packets that have an IP layer
    # (Some low-level frames like ARP don't have IP)
    if not packet.haslayer(IP):
        return

    ip_layer = packet[IP]

    # Extract common fields
    src_ip    = ip_layer.src
    dst_ip    = ip_layer.dst
    length    = len(packet)             # Total packet size in bytes
    timestamp = time.time()             # Unix timestamp (float)

    # Protocol number: 6 = TCP, 17 = UDP, 1 = ICMP, etc.
    protocol  = ip_layer.proto

    # Ports and flags depend on transport layer (TCP/UDP)
    src_port  = 0
    dst_port  = 0
    flags     = ""

    if packet.haslayer(TCP):
        tcp = packet[TCP]
        src_port = tcp.sport
        dst_port = tcp.dport
        # TCP flags as a string e.g. "SA" = SYN+ACK, "F" = FIN
        flags = str(tcp.flags)

    elif packet.haslayer(UDP):
        udp = packet[UDP]
        src_port = udp.sport
        dst_port = udp.dport
        flags = "UDP"   # UDP has no flags; label it for clarity

    # ─────────────────────────────────────────
    # STEP 3: Build the feature dictionary
    # This is the data your CNN will eventually consume
    # ─────────────────────────────────────────
    packet_data = {
        "src_ip":    src_ip,
        "dst_ip":    dst_ip,
        "protocol":  protocol,
        "src_port":  src_port,
        "dst_port":  dst_port,
        "length":    length,
        "flags":     flags,
        "timestamp": timestamp
    }

    # ─────────────────────────────────────────
    # STEP 4: Send to Kafka topic 'network-traffic'
    # .send() is non-blocking — it queues the message
    # .flush() forces it to actually be sent immediately
    # ─────────────────────────────────────────
    producer.send('network-traffic', value=packet_data)
    producer.flush()

    print(f"[+] Sent: {src_ip}:{src_port} → {dst_ip}:{dst_port} | proto={protocol} | len={length}")


# ─────────────────────────────────────────────
# STEP 5: Start sniffing
# count=0 means sniff forever (Ctrl+C to stop)
# store=False means don't keep packets in RAM (important for real-time use)
# ─────────────────────────────────────────────
# sniff(
#     prn=process_packet,   # Call process_packet() for every captured packet
#     store=False,          # Don't accumulate packets in memory
#     count=0               # Capture indefinitely
# )
try:
    sniff(
        prn=process_packet,
        store=False,
        count=0
    )
except KeyboardInterrupt:
    print("\n[!] Stopping capture...")
    producer.flush()
    producer.close()
    print("[*] Producer shut down cleanly.")