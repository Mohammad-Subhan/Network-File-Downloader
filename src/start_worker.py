from worker_server import start
import threading

WORKER_SERVERS = [
    {"id": "1", "address": "localhost", "port": 5051},
    {"id": "2", "address": "localhost", "port": 5052},
    {"id": "3", "address": "localhost", "port": 5053},
]

for worker in WORKER_SERVERS:
    worker_id = worker["id"]
    worker_address = worker["address"]
    worker_port = worker["port"]
    print(f"Starting worker server {worker_id} on {worker_address}:{worker_port}")
    thread = threading.Thread(target=start, args=(worker_port,))
    thread.start()
