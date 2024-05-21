import tkinter as tk
from tkinter import messagebox, PhotoImage, Canvas, simpledialog, scrolledtext, filedialog
import socket
import threading

# Pre-defined user and contact details
contacts = {
    "Hanine": ("127.0.0.1", 2223),
    "Pamela": ("127.0.0.2", 2223),
    "Cynthia": ("127.0.0.3", 2223),
    "Rawan": ("127.0.0.4", 2223),
    "Ayman": ("127.0.0.5", 2223),
}

class ChatApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('PieChat')
        self.geometry('1200x1000')

        self.client_socket = None
        self.host = None
        self.port = None
        self.user_id = None
        self.contact_name = None
        self.seq_num = '0'

        self.setup_login()

    def setup_login(self):
        self.login_frame = tk.Frame(self)
        self.login_frame.pack(fill='both', expand=True)

        self.welcome_label = tk.Label(self.login_frame, text="Welcome to PieChat", font=('Helvetica', 24))
        self.welcome_label.pack(side=tk.TOP, pady=20)

        self.image = PhotoImage(file='your_image.png')  # Update path as needed
        self.image_label = tk.Label(self.login_frame, image=self.image)
        self.image_label.pack(side=tk.LEFT, padx=20)

        self.name_entry = tk.Entry(self.login_frame, font=('Helvetica', 12))
        self.name_entry.pack(side=tk.TOP, padx=20, pady=10)

        self.submit_button = tk.Button(self.login_frame, text="Login", font=('Helvetica', 12), command=self.show_greeting)
        self.submit_button.pack(side=tk.TOP, pady=10)

    def show_greeting(self):
        self.user_id = self.name_entry.get()
        if self.user_id in contacts:
            self.welcome_label.config(text=f"Hi, {self.user_id}! Select a contact to chat with.")
            self.login_frame.pack_forget()
            self.display_contacts()
        else:
            messagebox.showerror("Authentication Error", "You are not authenticated.")

    def display_contacts(self):
        self.main_frame = tk.Frame(self)
        self.main_frame.pack(fill='both', expand=True)
        for contact, info in contacts.items():
            if contact != self.user_id:  # Exclude the current user
                frame = tk.Frame(self.main_frame, pady=10)
                frame.pack(fill='x')
                canvas = Canvas(frame, width=40, height=40, bg='white', highlightthickness=0)
                canvas.pack(side=tk.LEFT, padx=10)
                img = PhotoImage(file='profile_icon.png') 
                canvas.create_image(20, 20, image=img)
                canvas.image = img  # Keep a reference to prevent garbage-collection
                tk.Label(frame, text=contact, font=('Helvetica', 14)).pack(side=tk.LEFT)
                frame.bind("<Button-1>", lambda e, c=contact: self.start_chat(c))

    def start_chat(self, contact_name):
        self.contact_name = contact_name
        self.main_frame.pack_forget()
        self.chat_frame = tk.Frame(self)
        self.chat_frame.pack(fill='both', expand=True)

        self.chat_label = tk.Label(self.chat_frame, text=f"You're in the chat with {contact_name}", font=('Helvetica', 16))
        self.chat_label.pack(side=tk.TOP, pady=10)

        self.messages_frame = scrolledtext.ScrolledText(self.chat_frame, state='disabled', height=15)
        self.messages_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        self.msg_entry = tk.Text(self.chat_frame, height=3)
        self.msg_entry.pack(padx=20, pady=10, fill=tk.X, expand=False)

        self.send_button = tk.Button(self.chat_frame, text="Send", command=lambda: self.send_message(contact_name))
        self.send_button.pack(side=tk.LEFT, padx=(20, 10), pady=10)

        self.send_file_button = tk.Button(self.chat_frame, text="Send File", command=self.sendfile)
        self.send_file_button.pack(side=tk.RIGHT, padx=(10, 20), pady=10)

        self.setup_networking(contact_name)
        threading.Thread(target=self.receive_file, daemon=True).start()  # Start listening for incoming files

    def setup_networking(self, contact_name):
        self.host, self.port = contacts[self.user_id]
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client_socket.bind((self.host, self.port))

        self.recipient_host, self.recipient_port = contacts[contact_name]
        threading.Thread(target=self.receive_messages, daemon=True).start()

    def send_message(self, contact_name):
        msg = self.msg_entry.get('1.0', tk.END).strip()
        if msg:
            message_packet = f"{self.seq_num}:{msg}".encode('utf-8')
            self.client_socket.sendto(message_packet, (self.recipient_host, self.recipient_port))
            self.messages_frame.config(state='normal')
            self.messages_frame.insert(tk.END, f"You: {msg}\n")
            self.messages_frame.config(state='disabled')
            self.msg_entry.delete('1.0', tk.END)
            self.seq_num = '1' if self.seq_num == '0' else '0'

    def receive_messages(self):
        while True:
            try:
                msg, addr = self.client_socket.recvfrom(1024)
                decoded_msg = msg.decode('utf-8')
                seq, message = decoded_msg.split(':')
                if seq == self.seq_num:
                    self.messages_frame.config(state='normal')
                    self.messages_frame.insert(tk.END, f"From {self.contact_name}: {message}\n")
                    self.messages_frame.config(state='disabled')
                    self.seq_num = '1' if self.seq_num == '0' else '0'
            except Exception as e:
                print(f"An error occurred: {e}")
                break

    def sendfile(self):
        filename = filedialog.askopenfilename()
        if not filename:
            return
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((self.recipient_host, 8000))
            with open(filename, "rb") as fi:
                data = fi.read(1024)
                while data:
                    sock.send(data)
                    data = fi.read(1024)
            messagebox.showinfo("Success", "File sent successfully.")

    def receive_file(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, 8000))
        server_socket.listen(1)
        while True:
            client_socket, addr = server_socket.accept()
            with client_socket:
                received_file = f"received_{self.contact_name}.bin"
                with open(received_file, 'wb') as file:
                    while True:
                        data = client_socket.recv(1024)
                        if not data:
                            break
                        file.write(data)
                print(f"Received file saved as {received_file}")

if __name__ == "__main__":
    app = ChatApp()
    app.mainloop()

