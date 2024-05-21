# UDP Chat Application

This project is a simple UDP-based chat application that allows users to send and receive messages over a network. The application supports message integrity checking using a custom UDP checksum calculation and file transfer using TCP.

## Features

- **UDP Messaging**: Allows users to send and receive text messages.
- **Message Integrity Check**: Ensures message integrity using a custom checksum calculation.
- **File Transfer**: Supports file transfer between users using TCP.
- **Multiple Contacts**: Users can select from a list of predefined contacts to chat with.

## Requirements

- Python
- Socket library (standard library)
- Threading library (standard library)
- OS library (standard library)
- Time library (standard library)
- ipaddress library (standard library)

## Usage

1. **Run the Application**: 
    ```bash
    python filename.py
    ```

2. **Select Sender**:
    - Enter the sender's name from the predefined contact list.

3. **Select Contact**:
    - Enter the contact's name to start messaging.

4. **Messaging**:
    - Type your message and press Enter to send.
    - Type `close` to exit the chat.
    - Type `sendfile` to send a file.

5. **File Transfer**:
    - Follow the prompts to send or receive files.
