import socket
import threading
import json
import os

# List of Worker Servers (Simulated) and Main Server Configuration
WORKER_SERVERS = [
    {"id": "1", "address": "localhost", "port": 5051},
    {"id": "2", "address": "localhost", "port": 5052},
    {"id": "3", "address": "localhost", "port": 5053},
]
SERVER_PORT = 5050
SERVER_HOST = "localhost"
ADDR = (SERVER_HOST, SERVER_PORT)
FORMAT = "utf-8"
HEADER = 64
CHUNK_SIZE = 1048576  # 1MB
DISCONNECT_MESSAGE = "!DISCONNECT".ljust(HEADER).encode(FORMAT)

# Main Server Socket Configuration
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)


def handle_client(conn, addr):
    print(f"[NEW CONNECTION] from {addr}")
    conn.send(b"ACK".ljust(HEADER))  # Initial ACK

    connected = True
    while connected:
        msg = conn.recv(HEADER).decode(FORMAT)
        msg_length = int(msg)
        msg = conn.recv(msg_length).decode(FORMAT)

        # Disconnect request
        if msg == DISCONNECT_MESSAGE.decode(FORMAT):
            connected = False
            print(f"[DISCONNECTED] {addr} disconnected")
            conn.close()
            break

        # Provide file chunk information to client
        if msg:
            file_name = msg
            print(f"[RECEIVED] file request for {file_name}")
            conn.send(b"ACK".ljust(HEADER))  # Acknowledge file request

            # Assign chunks to worker servers
            chunk_info = assign_chunks_to_workers(file_name)
            conn.send(str(len(json.dumps(chunk_info))).ljust(HEADER).encode(FORMAT))
            conn.send(json.dumps(chunk_info).encode(FORMAT))
            print(f"[SENT] chunk info: {chunk_info}")
            conn.recv(HEADER)  # ACK chunk info

    conn.close()


def assign_chunks_to_workers(file_name):
    # Get the size of the file
    file_size = os.path.getsize(file_name)
    num_chunks = 3  # Number of chunks to split the file into
    chunk_size = file_size // num_chunks  # Base chunk size
    remainder = file_size % num_chunks  # Extra bytes to distribute

    # Generate chunk assignments
    chunk_info = []
    for i in range(num_chunks):
        # Assign base chunk size to all but the last chunk
        if i == num_chunks - 1:
            chunk_info.append(
                {
                    "chunk_id": i + 1,
                    "size": chunk_size + remainder,  # Last chunk gets the remainder
                    "worker": WORKER_SERVERS[i % len(WORKER_SERVERS)],
                }
            )
        else:
            chunk_info.append(
                {
                    "chunk_id": i + 1,
                    "size": chunk_size,  # All other chunks get the base size
                    "worker": WORKER_SERVERS[i % len(WORKER_SERVERS)],
                }
            )

    return chunk_info


def start():
    server.listen()
    print(f"[LISTENING] Main server listening on {SERVER_HOST}: {SERVER_PORT}")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()


start()
