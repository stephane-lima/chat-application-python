# Overview

This project is a Python-based chat application designed to demonstrate practical networking skills, concurrent programming, and GUI design. It combines a server that accepts multiple client connections with a client app that provides a graphical chat interface.

The software consists of two programs: `server.py` and `client.py`. Start the server first by running `python server.py` in a terminal. Then run `python client.py` for each chat user, enter a username in the login window, and begin exchanging messages. The server broadcasts all messages to every connected client.

The purpose of this software is to learn how to build a simple, real-time networked application with reliable message delivery, JSON serialization, and a responsive client UI.

# Network Communication

This chat application uses a client/server architecture. A central server accepts connections from multiple clients and forwards messages to all connected clients/participants.

The application uses TCP for reliable ordered delivery. The server listens on `127.0.0.1:9999`, and each client connects to that same host and port.

Messages are exchanged as UTF-8 encoded JSON strings. Each message contains these fields:
- `type`: either `chat` for regular chat messages or `system` for notifications.
- `username`: the sender's username.
- `message`: the chat text or system notification.
- `time`: a timestamp formatted as `HH:MM:SS`.

# Development Environment

I developed this software using Visual Studio Code with Git (v2.50.0) for version control

The programming language is Python (v3.14.6) with the following libraries:
- `sockets`
- `threading`
- `json`
- `datetime`
- `customtkinter`
- `queue`

# Useful Websites

* [Python socket programming documentation](https://docs.python.org/3/library/socket.html)
* [Python threading documentation](https://docs.python.org/3/library/threading.html)
* [CustomTkinter documentation](https://customtkinter.tomschimansky.com/)

# Future Work

* Add a settings screen for selecting host and port values.
* Display a list of connected users inside the chat interface.
* Add support for private messages, file transfer, or message history logging.