# Server program

from socket import *
import threading
import sys

PORT = 2222
BUFFER_SIZE = 1024
USE_NEWLINE = False # Set to false if using other client

# Client = socket object, port number
clients = {} # Dictionary holds clients
clients_lock = threading.Lock() # Lock for thread-safe access

# Send message to all chat users except sender
def update_chat(message, sender):
    with clients_lock: # Ensure thread-safe access to clients dictionary
        for conn in list(clients.keys()):
            if conn != sender:
                try:
                    conn.sendall((message + '\n').encode())
                except: # Handle possible disconnection
                    conn.close()
                    del clients[conn]

# Receive message from a client and send to chat
def handle_client(conn, addr):
    port = addr[1]
    print(f"New connection from {addr}")

    with clients_lock: # Ensure thread-safe access to clients dictionary
        clients[conn] = port # Store client connection

    data = b''

    while True:
        chunk = conn.recv(BUFFER_SIZE)
        if not chunk:
            break

        if USE_NEWLINE:  # If using newline to separate messages
            data += chunk
            while b'\n' in data: # Process complete messages
                message, data = data.split(b'\n', 1)
                message = message.decode().strip()
                if message.lower() == 'exit':
                    break
                print(f"{port}: {message}")
                update_chat(f"{port}: {message}", conn)
        else:
            message = chunk.decode().strip()
            if message.lower() == 'exit':
                break
            print(f"{port}: {message}")
            update_chat(f"{port}: {message}", conn)

    with clients_lock:
        if conn in clients:
            del clients[conn]

    conn.close()
    print(f"Connection closed from {addr}")

# Starts server and listens for incoming connections
def start_server():
    server = socket(AF_INET, SOCK_STREAM)
    server.bind(('', PORT))
    server.listen()
    server_ip = gethostbyname(gethostname())
    print(f"Server listening on {server_ip}:{PORT}")

    # Accepts connections and starts a new thread for each client   
    try:
        while True:
            conn, addr = server.accept()
            threading.Thread(target=handle_client, args=(conn, addr)).start()
    except KeyboardInterrupt:
        print("\nServer shutting down...")
        with clients_lock:
            for conn in list(clients.keys()):
                conn.close()
                del clients[conn]
        server.close()
        sys.exit()

# Main function
if __name__ == "__main__":
    start_server()