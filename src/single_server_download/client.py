import socket
import sys

PORT = 5050
SERVER = "localhost"
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
HEADER = 64
CHUNK_SIZE = 1024 * 1024 * 10  # 10MB
DISCONNECT_MESSAGE = "!DISCONNECT"
REQUEST_FILES = "--rf"

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)
client.recv(HEADER)  # recv ACK
print(f"[CONNECTED] connected to server {SERVER}")


def send(msg):

    if msg == REQUEST_FILES:
        client.send(str(len(msg)).ljust(HEADER).encode(FORMAT))
        client.send(msg.encode(FORMAT))
        print(f"[SENT] files requested")
        client.recv(HEADER)  # recv ACK

        # Receive file names
        msg_length = int(client.recv(HEADER).decode(FORMAT))
        file_names = client.recv(msg_length).decode(FORMAT)
        client.send(b"ACK".ljust(HEADER))

        print("[RECEIVED] files names received")
        print(f"[INFO] files available:\n{file_names}")
        return

    # request file
    client.send(str(len(msg)).ljust(HEADER).encode(FORMAT))
    client.send(msg.encode(FORMAT))
    print(f"[SENT] file requested: {msg}")
    client.recv(HEADER)  # recv ACK
    if msg == DISCONNECT_MESSAGE:
        return
    # Receive file name
    msg_length = int(client.recv(HEADER).decode(FORMAT))
    file_name = client.recv(msg_length).decode(FORMAT)
    if file_name == "ERROR":
        print(f"[ERROR] file not found")
        return
    client.send(b"ACK".ljust(HEADER))  # send ACK
    print(f"[RECEIVED] file name: {file_name}")
    # Receive file size
    msg_length = int(client.recv(HEADER).decode(FORMAT))
    file_size = client.recv(msg_length).decode(FORMAT)
    client.send(b"ACK".ljust(HEADER))  # send ACK
    print(f"[RECEIVED] file size: {file_size}")
    file_bytes = b""
    # Receive file data
    try:
        file = open(f"../data/received/{file_name}", "wb")
        while True:
            data = client.recv(CHUNK_SIZE)
            file_bytes += data
            if b"<END>" in file_bytes:
                file_bytes = file_bytes[:-5]
                break
        file.write(file_bytes)
        print(f"[RECEIVED] file recieved")
        client.send(b"ACK".ljust(HEADER))  # send ACK
        file.close()  # Close file
    except Exception as e:
        print(f"[ERROR] {e}")


args = sys.argv
file_name = args[1]
send(file_name)  # send file name
send(DISCONNECT_MESSAGE)  # send disconnect message
client.close()  # Close connection
