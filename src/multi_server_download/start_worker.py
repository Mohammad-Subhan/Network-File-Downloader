from worker_server import start
import threading
import signal
import sys
import time

WORKER_SERVERS = [
    {"id": "1", "address": "localhost", "port": 5051},
    {"id": "2", "address": "localhost", "port": 5052},
    {"id": "3", "address": "localhost", "port": 5053},
    {"id": "4", "address": "localhost", "port": 5054},
]

threads = []
stop_event = threading.Event()


def shutdown_server(signal_num, frame):
    print("\n[SHUTTING DOWN] Stopping all worker servers...")
    stop_event.set()
    for thread in threads:
        thread.join()
    print("[STOPPED] All worker servers stopped.")
    sys.exit(0)


# Register the signal handler
signal.signal(signal.SIGINT, shutdown_server)

for worker in WORKER_SERVERS:
    worker_id = worker["id"]
    worker_address = worker["address"]
    worker_port = worker["port"]
    print(f"Starting worker server {worker_id} on {worker_address}:{worker_port}")
    thread = threading.Thread(target=start, args=(worker_port, stop_event))
    threads.append(thread)
    thread.start()

print("[MAIN THREAD] Press Ctrl+C to stop the servers.")
try:
    while not stop_event.is_set():
        time.sleep(1)
except KeyboardInterrupt:
    shutdown_server(None, None)
