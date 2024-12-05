import os
import socket
import threading

PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
HEADER = 64
CHUNK_SIZE = 1024
DISCONNECT_MESSAGE = "!DISCONNECT".ljust(HEADER).encode(FORMAT)

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
        if msg == DISCONNECT_MESSAGE.decode(FORMAT):
            connected = False
            print(f"[DISCONNECTED] {addr} client disconnected")
            conn.close()
            break

        # Check if file exists
        if msg:
            file_name = msg
            print(f"[RECEIVED] file name recieved: {file_name}")
            conn.send(b"ACK".ljust(HEADER))  # send ACK
            try:
                file = open(file_name, "rb")
                file_size = os.path.getsize(file_name)
            except FileNotFoundError:
                print(f"[ERROR] file not found")
                conn.send(str(len("ERROR")).ljust(HEADER).encode(FORMAT))
                conn.send("ERROR".encode(FORMAT))
                continue

            # Send file name and size
            conn.send(str(len(f"received_{file_name}")).encode(FORMAT).ljust(HEADER))
            conn.send(f"received_{file_name}".encode(FORMAT))
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
