from socket import *
import threading
import uuid
import json
import time
import sys

BUFFER_SIZE = 1024

class Message:
    def __init__(self, uuid_str, flag=0):
        self.uuid = uuid_str
        self.flag = flag

    def to_json(self):
        return json.dumps({
            "uuid": self.uuid,
            "flag": self.flag
        })

    @staticmethod
    def from_json(data):
        obj = json.loads(data)
        return Message(obj["uuid"], obj["flag"])

class Node:
    def __init__(self, config_file, log_file):
        self.uuid = str(uuid.uuid4())
        self.state = 0
        self.leader_id = None
        self.log_file = log_file

        # Read configuration file
        with open(config_file, 'r') as f:
            lines = f.readlines()
            self.server_ip, self.server_port = lines[0].strip().split(',')
            self.client_ip, self.client_port = lines[1].strip().split(',')

        self.server_port = int(self.server_port)
        self.client_port = int(self.client_port)

        self.server_conn = None
        self.client_socket = None

        self.leader_announced = False # Help drop msg forwarding when election finished

    # Log messages to file and console
    def log(self, msg):
        with open(self.log_file, 'a') as f:
            f.write(msg + '\n')
            print(msg)

    # Send message to neighbor
    def send_message(self, msg):
        try:
            self.client_socket.sendall((msg.to_json() + '\n').encode())
            self.log(f"Sent: uuid={msg.uuid}, flag={msg.flag}")
        except Exception as e:
            print(f"Error sending message: {e}")

    # Handle incoming messages
    def handle_message(self, msg):

        # Compare uuid strings
        if msg.uuid > self.uuid:
            comparison = "greater"
        elif msg.uuid < self.uuid:
            comparison = "lesser"
        else:
            comparison = "same"
        
        # Log the received message
        log_msg = f"Received: uuid={msg.uuid}, flag={msg.flag}, {comparison}, {self.state}"
        if self.state == 1:
            log_msg += f", leader_id={self.leader_id}"
        self.log(log_msg)

        # Handle message based on flag and uuid
        if msg.flag == 1:
            if not self.leader_announced:
                self.state = 1
                self.leader_id = msg.uuid
                self.leader_announced = True
                self.log(f"Leader is decided to {self.leader_id}")
                # Forward leader announcement if not leader
                if msg.uuid != self.uuid:
                    self.send_message(msg)
            else:
                # Ignore further leader announcements
                self.log("Leader announcement ignored, already announced.")
        
        elif msg.uuid == self.uuid:
            # Node's unique uuid came back, it is now leader
            self.state = 1
            self.leader_id = msg.uuid
            self.leader_announced = True
            self.log(f"Leader is decided to {self.leader_id}")
            # Forward leader announcement to neighbors
            leader_msg = Message(self.uuid, 1)
            self.send_message(leader_msg)

        elif msg.uuid > self.uuid:
            # Forward message, election still in process
            self.send_message(msg)

        else:
            # Ignore messages with lesser uuid
            self.log("Ignored message.")

    # Connect to neighbor as client
    def connect_to_neighbor(self):
        self.client_socket = socket(AF_INET, SOCK_STREAM)
        while True:
            try:
                self.client_socket.connect((self.client_ip, self.client_port))
                print(f"Connected to neighbor at {self.client_ip}:{self.client_port}")
                print(f"Node UUID: {self.uuid}\n")
                break
            except Exception:
                time.sleep(10) # Retry every 10 seconds if connection fails

    # Start server to listen for incoming messages
    def start_server(self):
        server_socket = socket(AF_INET, SOCK_STREAM)
        server_socket.bind((self.server_ip, self.server_port))
        server_socket.listen(1)
        self.server_conn, addr = server_socket.accept()

        # Receive messages in a loop
        buffer = ""
        try:
            while True:
                chunk = self.server_conn.recv(BUFFER_SIZE).decode()
                if not chunk:
                    print("No data received, closing connection.")
                    break

                buffer += chunk
                while '\n' in buffer: # Split buffer by newlines
                    line, buffer = buffer.split('\n', 1)
                    if line.strip():
                        try:
                            msg = Message.from_json(line.strip())
                            self.handle_message(msg)
                        except:
                            print("JSON error.")
        except Exception as e:
            print(f"Server error: {e}")
        finally:
            if self.server_conn:
                self.server_conn.close()
                print("Server connection closed.")
            server_socket.close()
            print("Server socket closed.")

    def run(self):
        # Start server in a separate thread
        threading.Thread(target=self.start_server, daemon=True).start()
        
        # Wait for everyone to start servers
        time.sleep(15)

        # Connect to neighbor as client
        self.connect_to_neighbor()

        # Wait for connection to be established
        time.sleep(5)

        # Start election process
        initial_message = Message(self.uuid, 0)
        self.send_message(initial_message)

        # Wait for election to finish
        while self.state == 0:
            time.sleep(1)

        self.log(f"\nLeader is {self.leader_id}")

        # Clean up
        if self.client_socket:
            try:
                self.client_socket.close()
                print("Client socket closed.")
            except Exception:
                print("Error closing client socket.")

        if self.server_conn:
            try:
                self.server_conn.close()
                print("Server connection closed.")
            except Exception:
                print("Error closing server connection.")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python myleprocess.py <config_file> <log_file>")
        sys.exit(1)

    node = Node(sys.argv[1], sys.argv[2])
    node.run()