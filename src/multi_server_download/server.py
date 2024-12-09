import os
import socket
import threading

PORT = 5050
SERVER = "localhost"
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
HEADER = 64
CHUNK_SIZE = 1024 * 1024 * 10  # 10MB
DISCONNECT_MESSAGE = "!DISCONNECT"
REQUEST_FILES = "--rf"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)


def handle_client(conn, addr):
    conn.send(b"ACK".ljust(HEADER))  # send ACK
    print(f"[NEW CONNECTION] connection accepted from {addr}")

    msg = conn.recv(HEADER).decode(FORMAT)
    msg_length = int(msg)
    msg = conn.recv(msg_length).decode(FORMAT)

    if msg == REQUEST_FILES:
        print(f"[RECEIVED] file names requested")
        conn.send(b"ACK".ljust(HEADER))  # send ACK
        # Get only files
        directory = "../data"
        files = [
            f
            for f in os.listdir(directory)
            if os.path.isfile(os.path.join(directory, f))
        ]
        # Send file names
        file_names = f"\n".join(files)
        conn.send(str(len(file_names)).ljust(HEADER).encode(FORMAT))
        conn.send(file_names.encode(FORMAT))
        conn.recv(HEADER)  # recv ACK
        print("[SENT] file names sent")
    else:
        print(f"[RECEIVED] file size request for {msg}")
        conn.send(b"ACK".ljust(HEADER))  # send ACK
        file_path = f"../data/{msg}"
        file_size = os.path.getsize(file_path)
        conn.send(str(len(str(file_size))).ljust(HEADER).encode(FORMAT))
        conn.send(str(file_size).encode(FORMAT))
        conn.recv(HEADER)  # recv ACK
        print(f"[SENT] file size sent: {file_size}")
    conn.close()


def start():
    server.listen()
    print(f"[LISTENING] server listening on {SERVER}: {PORT}")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()


start()
