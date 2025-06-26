# Chat Server with Multiple Clients

A chat program using TCP connections between a single server and client(s). 

# Server:
    - Accepts n clients and creates separate thread for each. 
    - Maintains list of active clients
    - Sends messages to client with
        i. client port number
        ii. text message
    - Removes client when receives "exit" message

# Client:
    - Connects to server
    - Creates threads for sending and receiving messages
    - Sends user input to server
    - Prints messages from other chat users
