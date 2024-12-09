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

    connected = True
    while connected:
        msg = conn.recv(HEADER).decode(FORMAT)
        msg_length = int(msg)
        msg = conn.recv(msg_length).decode(FORMAT)

        # Check if client disconnected
        if msg == DISCONNECT_MESSAGE:
            connected = False
            print(f"[DISCONNECTED] {addr} client disconnected")
            conn.send(b"ACK".ljust(HEADER))  # send ACK
            conn.close()
            break

        elif msg == REQUEST_FILES:
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

            continue

        # Check if file exists
        if msg:
            file_name = msg
            print(f"[RECEIVED] file name recieved: {file_name}")
            conn.send(b"ACK".ljust(HEADER))  # send ACK
            try:
                file = open(f"../data/{file_name}", "rb")
                file_size = os.path.getsize(f"../data/{file_name}")
            except FileNotFoundError:
                print(f"[ERROR] file not found")
                conn.send(str(len("ERROR")).ljust(HEADER).encode(FORMAT))
                conn.send("ERROR".encode(FORMAT))
                continue

            # Send file name and size
            conn.send(str(len(f"{file_name}")).encode(FORMAT).ljust(HEADER))
            conn.send(f"{file_name}".encode(FORMAT))
            conn.recv(HEADER)  # recv ACK
            print(f"[SENT] file name sent: received_{file_name}")

            conn.send(str(len(str(file_size))).ljust(HEADER).encode(FORMAT))
            conn.send(str(file_size).encode(FORMAT))
            conn.recv(HEADER)  # recv ACK
            print(f"[SENT] file size sent: {file_size}")

            # Send file data
            data = file.read(CHUNK_SIZE)
            while data:
                conn.send(data)
                data = file.read(CHUNK_SIZE)
            conn.send(b"<END>")  # END marker
            print(f"[SENT] file sent")
            conn.recv(HEADER)  # recv ACK

            file.close()  # Close file


def start():
    server.listen()
    print(f"[LISTENING] server listening on {SERVER}: {PORT}")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()


start()
