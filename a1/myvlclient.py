from socket import *

serverPort = 12000 # Port

# Sends encoded message over socket
def send_msg(sock, message):
    sock.send(message.encode())
    return True

# Reads message from socket
def receive_msg(sock):
    length_bytes = sock.recv(2) # Read first 2 char
    if len(length_bytes) < 2:
        return None

    msg_len = int(length_bytes.decode())

    # Receive bytes as they come
    data = b'' # Empty byte string for message
    while len(data) < msg_len:
        chunk = sock.recv(min(64, msg_len - len(data)))
        if not chunk:
            break
        data += chunk

    return data.decode()

def run_client():
    serverName = input("Enter server IP address: ") # IP
    clientSocket = socket(AF_INET, SOCK_STREAM) # Create TCP socket
    clientSocket.connect((serverName, serverPort)) # Connect to server

    # Ask user for input
    sentence = input('Input lowercase sentence: ')
    if not send_msg(clientSocket, sentence): # Send user input as message
        clientSocket.close() # Close socket if sending fails
        return

    capSentence = receive_msg(clientSocket)
    if capSentence:
        print('From Server:', capSentence)

    clientSocket.close()

if __name__ == "__main__":
    run_client()