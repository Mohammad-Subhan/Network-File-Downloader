import json
import socket
import os
import threading

FORMAT = "utf-8"
HEADER = 64
CHUNK_SIZE = 1048576  # 1MB
DISCONNECT_MESSAGE = "!DISCONNECT".ljust(HEADER).encode(FORMAT)
SERVER = "localhost"


def handle_client(conn, addr):
    print(f"[NEW CONNECTION] from {addr}")
    conn.send(b"ACK".ljust(HEADER))  # Initial ACK

    # Send file chunk data
    try:
        msg_size = conn.recv(HEADER).decode(FORMAT)
        chunk_info = conn.recv(int(msg_size)).decode(FORMAT)
        conn.send(b"ACK".ljust(HEADER))  # ACK chunk ID

        chunk_info = json.loads(chunk_info)

        file_name = chunk_info["file_name"]
        file_size = os.path.getsize(file_name)
        chunk_size = chunk_info["size"]
        chunk_id = chunk_info["chunk_id"]
        total_chunks = chunk_info["total_chunks"]

        file = open(file_name, "rb")
        for i in range(chunk_id):
            if i == total_chunks - 1:
                data = file.read(chunk_size + file_size % total_chunks)
            else:
                data = file.read(chunk_size)

        for i in range(0, len(data), CHUNK_SIZE):
            conn.send(data[i : i + CHUNK_SIZE])  # Send chunk data
        conn.send(b"<END>")  # End marker
        print(f"[SENT] chunk {chunk_id} sent")
        conn.recv(HEADER)  # ACK

    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        conn.close()


def start(port, stop_event):
    worker = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ADDR = (SERVER, port)
    worker.bind(ADDR)
    worker.listen()
    print(f"[LISTENING] Worker server listening on {SERVER}: {port}")

    try:
        while not stop_event.is_set():
            worker.settimeout(1)
            try:
                conn, addr = worker.accept()
                thread = threading.Thread(target=handle_client, args=(conn, addr))
                thread.start()
            except socket.timeout:
                continue
    except Exception as e:
        print(f"[ERROR] Worker server on port {port} encountered an error: {e}")
    finally:
        worker.close()
        print(f"[STOPPED] Worker server on port {port} has stopped.")
