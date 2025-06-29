# Server program

from socket import *
import threading
import sys

PORT = 2222
BUFFER_SIZE = 1024

# Client = socket object, port number
# Dictionary holds clients
clients = {}

# Send message to all chat users except sender
def update_chat(message, sender):
    for conn in list(clients):
        if conn != sender: # Don't send to sender
            try:
                conn.sendall(message.encode())
            except: # Handle possible disconnection
                conn.close()
                del clients[conn]

# Receive message from a client and send to chat
def handle_client(conn, addr):
    port = addr[1]
    print(f"New connection from {addr}")
    clients[conn] = port # Store client connection

    while True:
        data = conn.recv(BUFFER_SIZE)
        if not data:
            break
        message = data.decode().strip()
        if message.lower() == "exit": # End chat
            break
        update_chat(f"{port}: {message}", conn)

    conn.close()
    del clients[conn] # Remove client from dictionary
    print(f"Connection closed from {addr}")

# Starts server and listens for incoming connections
def start_server():
    server = socket(AF_INET, SOCK_STREAM)
    server.bind(('', PORT))
    server.listen()
    server_ip = socket.gethostbyname(socket.gethostname())
    print(f"Server listening on {server_ip}:{PORT}")

    # Accepts connections and starts a new thread for each client   
    try:
        while True:
            conn, addr = server.accept()
            threading.Thread(target=handle_client, args=(conn, addr)).start()
    except KeyboardInterrupt:
        print("\nServer shutting down...")
        server.close()
        sys.exit()

# Main function
if __name__ == "__main__":
    start_server()