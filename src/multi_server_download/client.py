import os
import socket
import json
import threading
import sys

FORMAT = "utf-8"
HEADER = 64
CHUNK_SIZE = 1024 * 1024 * 10  # 10MB
DISCONNECT_MESSAGE = "!DISCONNECT".ljust(HEADER)
WORKER_SERVERS = [
    {"id": "1", "address": "localhost", "port": 5051},
    {"id": "2", "address": "localhost", "port": 5052},
    {"id": "3", "address": "localhost", "port": 5053},
    {"id": "4", "address": "localhost", "port": 5054},
]
MAIN_SERVER = "localhost"
MAIN_PORT = 5050
MAIN_ADDR = (MAIN_SERVER, MAIN_PORT)
REQUEST_FILES = "--rf"


def send_file_request(file_name):

    if file_name == REQUEST_FILES:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(MAIN_ADDR)
        client.recv(HEADER)  # Initial ACK

        client.send(str(len(file_name)).ljust(HEADER).encode(FORMAT))
        client.send(file_name.encode(FORMAT))
        print(f"[SENT] files requested")
        client.recv(HEADER)  # recv ACK

        # Receive file names
        msg_length = int(client.recv(HEADER).decode(FORMAT))
        file_names = client.recv(msg_length).decode(FORMAT)
        client.send(b"ACK".ljust(HEADER))

        print("[RECEIVED] files names received")
        print(f"[INFO] files available:\n{file_names}")
        client.close()
        return

    chunk_info = get_chunk_info(file_name)
    print(f"[INFO] Sending file request for {file_name}")
    threads = []
    for chunk in chunk_info:
        thread = threading.Thread(target=download_chunk, args=(chunk,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    try:
        data = b""
        for i in range(1, len(WORKER_SERVERS) + 1):
            data += open(f"../data/chunks/chunk_{i}_{file_name}", "rb").read()
            os.remove(f"../data/chunks/chunk_{i}_{file_name}")

        with open(f"../data/received/{file_name}", "wb") as f:
            f.write(data)
    except Exception as e:
        print(f"[ERROR] {e}")


def download_chunk(chunk):

    tries = len(WORKER_SERVERS)
    for attempt in range(tries):
        try:
            # worker server info
            worker_server = WORKER_SERVERS[
                ((chunk["chunk_id"] - 1) + attempt) % len(WORKER_SERVERS)
            ][
                "address"
            ]  # Round-robin
            worker_port = WORKER_SERVERS[
                ((chunk["chunk_id"] - 1) + attempt) % len(WORKER_SERVERS)
            ][
                "port"
            ]  # Round-robin
            worker_addr = (worker_server, worker_port)

            worker = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            worker.settimeout(60)
            worker.connect(worker_addr)
            worker.recv(HEADER)  # Initial ACK

            string_chunk_info = json.dumps(chunk)
            worker.send(
                str(len(string_chunk_info)).ljust(HEADER).encode(FORMAT)
            )  # Send chunk info size
            worker.send(string_chunk_info.encode(FORMAT))  # Send chunk info
            worker.recv(HEADER)  # ACK chunk_info

            # Receive the chunk from the worker server
            chunk_data = b""
            with open(
                f"../data/chunks/chunk_{chunk["chunk_id"]}_{chunk["file_name"]}", "wb"
            ) as f:
                while True:
                    data = worker.recv(CHUNK_SIZE)
                    chunk_data += data
                    if b"<END>" in chunk_data:
                        chunk_data = chunk_data[:-5]
                        break

                f.write(chunk_data)

            worker.send(b"ACK".ljust(HEADER))  # ACK chunk data
            print(
                f'[RECEIVED] Chunk {chunk["chunk_id"]} downloaded from {worker_server}:{worker_port}'
            )
            worker.close()
            return  # Exit if successful

        except (socket.error, socket.timeout) as e:
            print(
                f"[ERROR] Failed to download chunk {chunk['chunk_id']} from {worker_server}:{worker_port}. Retrying..."
            )
            continue  # Retry with the next worker


def get_chunk_info(file_name):

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(MAIN_ADDR)
    client.recv(HEADER)  # Initial ACK

    client.send(str(len(file_name)).ljust(HEADER).encode(FORMAT))
    client.send(file_name.encode(FORMAT))
    client.recv(HEADER)  # recv ACK

    # Receive file size
    msg_length = int(client.recv(HEADER).decode(FORMAT))
    file_size = client.recv(msg_length).decode(FORMAT)
    client.send(b"ACK".ljust(HEADER))
    client.close()

    file_size = int(file_size)
    num_chunks = len(WORKER_SERVERS)  # Number of chunks to split the file into
    chunk_size = file_size // num_chunks  # Base chunk size

    # Generate chunk 
    chunk_info = []
    for i in range(num_chunks):
        # Assign base chunk size to all but the last chunk
        chunk_info.append(
            {
                "file_name": file_name,
                "total_chunks": len(WORKER_SERVERS),
                "chunk_id": i + 1,
                "size": chunk_size,
            }
        )

    print(chunk_info)
    return chunk_info


args = sys.argv
file_name = args[1]
send_file_request(file_name)
