# Client / Server Process

# Classes:
    # Message (uuid & flag)

# Functions:
#   1. Read config.txt
#   2. Log messages
#   3. Serialize and send messages
#   4. Process received messages
#       - Deserialize message
#       - Compare uuid & act
#       - Log action (2)
#   5. Connect to neighbor node
#       - Send initial uuid
#   6. Start server socket
#       - Create thread for receiving messages
#   7. Receive messages
#   8. Main