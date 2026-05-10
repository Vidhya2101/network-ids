from scapy.all import sniff, IP

def packet_handler(packet):
    if IP in packet:
        print(f"Source: {packet[IP].src}  -->  Destination: {packet[IP].dst}")

print("Starting capture... (10 packets)")
sniff(iface="Intel(R) Wi-Fi 6 AX101", count=10, prn=packet_handler)
print("Done.") 