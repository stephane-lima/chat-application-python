import socket
import threading
import json
import customtkinter as ctk
from datetime import datetime
import queue

HOST = "127.0.0.1"
PORT = 9999
BUFFER_SIZE = 4096

# Show login UI, validate username, and open the main chat window.
def login():
    # Set the appearance mode for the login window.
    ctk.set_appearance_mode("dark")

    # Create the login window.
    login_window = ctk.CTk()
    login_window.title("Login")
    login_window.geometry("300x150")
    login_window.resizable(False, False)

    # Create the username entry field inside the login window.
    username_entry = ctk.CTkEntry(
        login_window, 
        placeholder_text="Username", 
        font=("Segoe UI", 14)
    )
    username_entry.pack(pady=30)
    
    # Bind the Enter key to the connect callback.
    username_entry.bind("<Return>", lambda event: connect())

    # Validate username input and transition from login to chat.
    def connect():
        # Read the typed username and remove surrounding whitespace.
        username = username_entry.get().strip()

        # Do not proceed with an empty username.
        if not username:
            return
        
        # Close the login window before opening the chat.
        login_window.destroy()

        # Launch the main chat window using the validated username.
        start_chat(username)

    # Create the connect button, assign its callback, and add the button to the login window.
    connect_button = ctk.CTkButton(
        login_window, 
        text="Connect", 
        command=connect
    )
    connect_button.pack()

    # Start the login window event loop.
    login_window.mainloop()

# Connect to the server, build chat UI, and manage message sending and receiving.
def start_chat(username):
    # Create the client TCP socket.
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect the socket to the configured server address.
    client_socket.connect((HOST, PORT))

    # Send the chosen username to the server immediately.
    client_socket.send(username.encode("utf-8"))

    # Track whether the chat is still active.
    running = True

    # Create a thread-safe queue for incoming messages.
    message_queue = queue.Queue()

    # Create the main chat window.
    window = ctk.CTk()
    window.title(f"Chat Application - {username}")
    window.geometry("600x500")
    window.resizable(False, False)

    # Create the chat display box as read-only.
    chat_box = ctk.CTkTextbox(
        window, 
        width=500, 
        height=350, 
        font=("Segoe UI", 14), 
        state="disabled"
    )
    # Place the chat box inside the window with padding.
    chat_box.pack(
        padx=20, 
        pady=20, 
        fill="both", 
        expand=True
    )

    # Create the message input field and place the input field with padding.
    message_entry = ctk.CTkEntry(
        window, 
        placeholder_text="Type a message..."
    )
    message_entry.pack(padx=20, pady=10, fill="x")

    # Bind Enter key to send the message.
    message_entry.bind("<Return>", lambda event: send_message())

    # Append a formatted message to the chat display and keep it read-only.
    def display_message(message):
        # Enable the chat box to allow text insertion.
        chat_box.configure(state="normal")

        # Insert the formatted message at the end of the chat box.
        chat_box.insert("end", message + "\n\n")

        # Scroll the chat box so the latest message is visible.
        chat_box.see("end")

        # Restore the chat box to read-only mode.
        chat_box.configure(state="disabled")

    # Send the current chat input as JSON to the server and clear the entry.
    def send_message():
        # Read the current text from the message input field.
        text = message_entry.get().strip()

        # Do not send empty or whitespace-only messages.
        if not text:
            return

        # Build the JSON object for the outgoing chat message.
        message = {
            "type": "chat",
            "username": username,
            "message": text,
            "time": datetime.now().strftime("%H:%M:%S")
        }

        try:
            # Serialize and send the message to the server.
            client_socket.send(json.dumps(message).encode("utf-8"))

            # Clear the input field after sending.
            message_entry.delete(0, "end")

        except Exception as error:
            # Print any errors that occur while sending.
            print("Error:", error)

    # Receive JSON messages from the server and queue them for GUI display.
    def receive_messages():
        # Continuously receive messages from the server while running is True.
        while running:
            try:
                # Receive raw data from the server.
                data = client_socket.recv(BUFFER_SIZE)

                # Stop receiving if the server closed the connection.
                if not data:
                    break

                # Decode the raw bytes and parse the JSON message.
                message = json.loads(data.decode("utf-8"))

                # Format the message text based on its type.
                if message["type"] == "chat":
                    text = f"[{message['time']}] {message['username']}: {message['message']} "

                elif message["type"] == "system":
                    text = "*** " + message["message"] + " ***"

                else:
                    text = str(message)

                # Queue the formatted text for display in the GUI thread.
                message_queue.put(text)
            
            except Exception as error:
                # Print the error only if the client is still considered running.
                if running:
                    print("Error:", error)
                break

    # Poll the message queue and display any queued messages periodically.
    def check_messages():
        # Stop processing if the client has been closed.
        if not running:
            return

        # Display all messages currently queued from the receive thread.
        while not message_queue.empty():
            display_message(message_queue.get())

        # Schedule another check shortly after this call.
        window.after(100, check_messages)

    # Stop message processing, close the socket, and destroy the chat window.
    def close_application():
        # Mark the client as no longer running.
        nonlocal running
        running = False

        try:
            # Shutdown the socket for both sending and receiving.
            client_socket.shutdown(socket.SHUT_RDWR)

            # Close the socket to release resources.
            client_socket.close()
        
        except Exception as error:
            # Print any error that occurs while closing.
            print("Error:", error)
        
        # Destroy the GUI window after cleanup.
        window.destroy()

    # Create the send button using the send_message callback and place the send button below the input field..
    send_button = ctk.CTkButton(
        window, 
        text="Send", 
        command=send_message
    )
    send_button.pack(pady=10)

    # Override the window close button to perform cleanup.
    window.protocol("WM_DELETE_WINDOW", close_application)

    # Start the background thread that receives messages and begin processing incoming messages in the background.
    receive_thread = threading.Thread(target=receive_messages, daemon=True)
    receive_thread.start()

    # Begin checking for queued messages and start the GUI loop.
    check_messages()
    window.mainloop()

login()
