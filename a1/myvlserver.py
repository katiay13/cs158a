from socket import *

serverPort = 12000 # Matches client port

# Reads message from client socket
def receive_msg(sock):
    length_bytes = sock.recv(2) # Reads length
    if len(length_bytes) < 2:
        return None

    msg_len = int(length_bytes.decode())
    print(f"msg_len: {msg_len}")

    # Receive bytes as they come
    data = b'' # Empty byte string for message
    while len(data) < msg_len:
        chunk = sock.recv(min(64, msg_len - len(data)))
        if not chunk:
            break
        data += chunk
    
    return data.decode()

# Sends message to client
def send_message(sock, message):
    msg_len = len(message)
    response = f"{msg_len:02d}" + message
    sock.send(response.encode())
    print(f"msg_len_sent: {msg_len}")

# Processes input msg and sends back through socket
def process_msg(cnSocket, addr):
    print(f"Connected from {addr}")
    sentence = receive_msg(cnSocket)

    # Check that received full msg
    if sentence is None:
        print("Invalid message received")
        cnSocket.close()
        print("Connection closed\n")
        return
    
    # Show what received from client
    print(f"processed: {sentence}")
    capSentence = sentence.upper()
    send_message(cnSocket, capSentence)

    cnSocket.close()
    print("Connection closed\n")

# Start connection with client
def start_server():
    # Create TCP socket
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind(('', serverPort))
    serverSocket.listen(1) # One client at a time

    print("Server is ready")

    # Keeps connection until user stops it manually
    try:
        while True:
            cnSocket, addr = serverSocket.accept()
            process_msg(cnSocket, addr)
    except KeyboardInterrupt:
        print("\nServer stopped manually")
        serverSocket.close()

if __name__ == "__main__":
    start_server()