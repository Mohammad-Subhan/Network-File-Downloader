import socket
import threading

FORMAT = "utf-8"
HEADER = 64
CHUNK_SIZE = 1048576  # 1MB
DISCONNECT_MESSAGE = "!DISCONNECT".ljust(HEADER).encode(FORMAT)

SERVER = "localhost"


def handle_client(conn, addr):
    print(f"[NEW CONNECTION] from {addr} for chunk {chunk_id}")
    conn.send(b"ACK".ljust(HEADER))  # Initial ACK

    msg_size = conn.recv(HEADER).decode(FORMAT)
    chunk_id = conn.recv(int(msg_size)).decode(FORMAT)
    conn.send(b"ACK".ljust(HEADER))  # ACK chunk ID
    # Send file chunk data
    try:
        file_name = (
            f"file_chunk_{chunk_id}.txt"  # Assuming chunks are stored separately
        )

        with open(file_name, "rb") as f:
            data = f.read(CHUNK_SIZE)
            while data:
                conn.send(data)
                data = f.read(CHUNK_SIZE)
            print(f"[SENT] chunk {chunk_id} sent")

        conn.send(b"<END>")  # End marker
    except Exception as e:
        print(f"[ERROR] {e}")
    conn.close()


def start(port):
    worker = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ADDR = (SERVER, port)
    worker.bind(ADDR)
    worker.listen()
    print(f"[LISTENING] Worker server listening on {SERVER}: {port}")
    while True:
        conn, addr = worker.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()


# start(5051)
