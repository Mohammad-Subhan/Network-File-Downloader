import socket

PORT = 5050
SERVER = "192.168.3.106"
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
HEADER = 64
CHUNK_SIZE = 1024
DISCONNECT_MESSAGE = "!DISCONNECT".ljust(HEADER)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)
client.recv(HEADER)  # recv ACK
print(f"[CONNECTED] connected to server {SERVER}")


def send(msg):

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
        file = open(file_name, "wb")
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


send("test.cpp")  # send file name
send(DISCONNECT_MESSAGE)  # send disconnect message
client.close()  # Close connection
