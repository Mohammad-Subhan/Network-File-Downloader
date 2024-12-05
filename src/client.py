import socket
import json

SERVER_PORT = 5050
SERVER_HOST = "localhost"  # Main server IP
ADDR = (SERVER_HOST, SERVER_PORT)
FORMAT = "utf-8"
HEADER = 64
CHUNK_SIZE = 1048576  # 1MB
DISCONNECT_MESSAGE = "!DISCONNECT".ljust(HEADER)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)
client.recv(HEADER)  # Initial ACK


def send_request(file_name):

    # Request file metadata from main server
    client.send(str(len(file_name)).ljust(HEADER).encode(FORMAT))
    client.send(file_name.encode(FORMAT))

    if file_name == DISCONNECT_MESSAGE:
        client.send(DISCONNECT_MESSAGE.encode(FORMAT))
        client.close()
        return

    client.recv(HEADER)  # ACK from main server

    # Receive chunk info from main server
    chunk_info_size = client.recv(HEADER).decode(FORMAT)
    chunk_info = client.recv(int(chunk_info_size)).decode(FORMAT)
    chunk_info = json.loads(chunk_info)
    print(f"[RECEIVED] chunk info: {chunk_info}")
    client.send(b"ACK".ljust(HEADER))  # ACK chunk info

    # Download chunks from worker servers
    for chunk in chunk_info:
        worker_info = chunk["worker"]
        chunk_size = chunk["size"]
        print(
            f"[INFO] Downloading from {worker_info["id"]} for chunk {chunk["chunk_id"]}"
        )
        download_chunk(worker_info, chunk["chunk_id"], chunk_size)

    # client.send(DISCONNECT_MESSAGE.encode(FORMAT))  # Send disconnect message


def download_chunk(worker_info, chunk_id, chunk_size):
    worker_server = worker_info["address"]  # IP for worker
    worker_port = worker_info["port"]  # port for worker
    worker_addr = (worker_server, worker_port)

    worker = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    worker.connect(worker_addr)
    worker.recv(HEADER)  # Initial ACK

    worker.send(str(len(str(chunk_id))).ljust(HEADER).encode(FORMAT))  # Request chunk
    worker.send(str(chunk_id).encode(FORMAT))  # Request chunk
    worker.recv(HEADER)  # ACK chunk ID

    # Receive the chunk from the worker server
    chunk_data = worker.recv(CHUNK_SIZE)
    with open(f"received_chunk_{chunk_id}.txt", "wb") as f:
        while True:
            data = worker.recv(CHUNK_SIZE)
            chunk_data += data
            if b"<END>" in chunk_data:
                chunk_data = chunk_data[:-5]
                break

    print(f"[RECEIVED] Chunk {chunk_id} downloaded from {worker_server}:{worker_port}")
    worker.close()


send_request("test.txt")
send_request(DISCONNECT_MESSAGE)
