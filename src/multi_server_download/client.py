import os
import socket
import json
import threading

FORMAT = "utf-8"
HEADER = 64
CHUNK_SIZE = 1048576  # 1MB
DISCONNECT_MESSAGE = "!DISCONNECT".ljust(HEADER)
WORKER_SERVERS = [
    {"id": "1", "address": "localhost", "port": 5051},
    {"id": "2", "address": "localhost", "port": 5052},
    {"id": "3", "address": "localhost", "port": 5053},
]
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def send_file_request(file_name):
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
        data_chunk_1 = open(f"../data/chunks/chunk_1_{file_name}", "rb").read()
        data_chunk_2 = open(f"../data/chunks/chunk_2_{file_name}", "rb").read()
        data_chunk_3 = open(f"../data/chunks/chunk_3_{file_name}", "rb").read()

        with open(f"../data/received_{file_name}", "wb") as f:
            f.write(data_chunk_1)
            f.write(data_chunk_2)
            f.write(data_chunk_3)
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
            worker.settimeout(5)
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
    file_size = os.path.getsize(f"../data/{file_name}")
    num_chunks = len(WORKER_SERVERS)  # Number of chunks to split the file into
    chunk_size = file_size // num_chunks  # Base chunk size
    remainder = file_size % num_chunks  # Extra bytes to distribute

    # Generate chunk assignments
    chunk_info = []
    for i in range(num_chunks):
        # Assign base chunk size to all but the last chunk
        if i == num_chunks - 1:
            chunk_info.append(
                {
                    "file_name": file_name,
                    "total_chunks": len(WORKER_SERVERS),
                    "chunk_id": i + 1,
                    "size": chunk_size + remainder,  # Last chunk gets the remainder
                    # "worker": WORKER_SERVERS[i % len(WORKER_SERVERS)],
                }
            )
        else:
            chunk_info.append(
                {
                    "file_name": file_name,
                    "total_chunks": len(WORKER_SERVERS),
                    "chunk_id": i + 1,
                    "size": chunk_size,  # All other chunks get the base size
                    # "worker": WORKER_SERVERS[i % len(WORKER_SERVERS)],
                }
            )

    return chunk_info


send_file_request("test.cpp") # Request the file
