# Client program

from socket import *
import threading
import sys

HOST = 'localhost' # Change to server IP if needed
PORT = 2222 # Default port for chat server
BUFFER_SIZE = 1024

# Receives messages from server and prints to user
def receive_msgs(sock):
    # Continuously receive messages from the server
    while True:
        try:
            data = sock.recv(BUFFER_SIZE)
            if not data:
                break
            print(data.decode())
        except:
            break

# Processes user input and sends to server
def send_msgs(sock):
    # Continuously read user input and send to server
    while True:
        message = input()
        if message.strip().lower() == "exit":
            sock.sendall(b"exit") # Send exit command to server
            break
        sock.sendall(message.encode())
    sock.close()
    print("Disconnected from server")
    sys.exit()

# Create client socket and thread for receiving messages
def start_client():
    # Create a TCP socket
    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect((HOST, PORT))
    print("Connected to chat server. Type 'exit' to leave.")

    # Start a thread to receive messages from the server
    threading.Thread(target=receive_msgs, args=(sock,)).start()
    send_msgs(sock)

# Main function
if __name__ == "__main__":
    start_client()