import socket
import threading
import json
from datetime import datetime

HOST = "127.0.0.1"
PORT = 9999
BUFFER_SIZE = 4096

clients = {}
lock = threading.Lock()

# Create a JSON string containing the message type, sender, content, and timestamp.
def create_message(message_type, username, text):
    return json.dumps({
        "type": message_type,
        "username": username,
        "message": text,
        "time": datetime.now().strftime("%H:%M:%S")
    })

# Send the message to all connected clients and remove any failed sockets.
def broadcast(message):
    disconnected = []

    with lock:
        # Attempt send to each client while holding the clients lock.
        for client in clients:
            try:
                client.send(message.encode("utf-8"))
            except:
                # Track clients whose sockets fail during send.
                disconnected.append(client)

        # Remove any clients that disconnected during broadcast.
        for client in disconnected:
            del clients[client]
            client.close()

# Handle a single client connection, relay its messages, and manage disconnects.
def handle_client(client_socket):
    # Receive the username, announce the join, and forward messages from this client.
    try:
        # Read the username sent by the client after connecting.
        username = client_socket.recv(BUFFER_SIZE).decode("utf-8")

        # Register the client socket and associated username.
        with lock:
            clients[client_socket] = username
        
        # Print the new connection to the server console.
        print(f"{username} connected.")

        # Broadcast a system message announcing the new user.
        join_message = create_message(
            "system", 
            "SERVER", 
            f"{username} joined the chat."
        )
        broadcast(join_message)

        while True:
            # Wait for a message from this client.
            data = client_socket.recv(BUFFER_SIZE)

            # If the client closed the connection, exit the loop.
            if not data:
                break

            # Decode the received bytes into a string.
            message = data.decode("utf-8")

            try:
                # Parse the message as JSON for logging.
                json_message = json.loads(message)

                print(
                    f"[{json_message['time']}] "
                    f"{json_message['username']}: "
                    f"{json_message['message']} "
                )

            except Exception as error:
                # Log parse errors but continue broadcasting the raw message.
                print("Error:", error)

            # Broadcast the original message text to all clients.
            broadcast(message)

    except Exception as error:
        # Log any unexpected errors encountered while handling this client.
        print("Error:", error)
        
    finally:
        # Clean up the client regardless of how the loop exited.
        remove_client(client_socket)

# Remove a disconnected client, close its socket, and sent a leave notice.
def remove_client(client_socket):
    with lock:
        if client_socket in clients:
            username = clients[client_socket]
            del clients[client_socket]
        else:
            username = "Unknown"

    # Close the socket to release network resources.
    client_socket.close()

    # Print the disconnect event to the server console.
    print(f"{username} disconnected.")

    # Send a system leave message to remaining connected clients.
    leave_message = create_message(
        "system", 
        "SERVER", 
        f"{username} has left the chat."
    )
    broadcast(leave_message)

# Start the TCP server, accept incoming connections, and spawn handler threads.
def start_server():
    # Open the listening socket, bind it, and start accepting clients.
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))

    # Put the socket into listening mode.
    server.listen()

    # Print server startup information.
    print(f"Server running on {HOST}:{PORT}")

    while True:
        # Accept the next incoming client connection.
        client_socket, address = server.accept()

        # Print the remote client address for logging.
        print(f"Connection from {address}")

        # Spawn a dedicated thread to handle the client interaction.
        thread = threading.Thread(target=handle_client, args=(client_socket,), daemon=True)
        thread.start()

start_server()
