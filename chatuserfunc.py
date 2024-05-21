import socket
import threading
import os
import time
import ipaddress
import queue


def ip_to_int(ip):
    # Convert the IP address to an ip_address object and then get its integer representation
    return int(ipaddress.ip_address(ip))

def udp_checksum(src_ip, dest_ip, src_port,dest_port, length, data):
    checksum = 0
    checksum += src_port
    checksum += dest_port
    checksum += src_ip
    checksum += dest_ip
    checksum += length
    # print(src_ip," ", dest_ip," ", src_port," ",dest_port," ", length," ", data)
    for i in range(0, len(data), 2):
        if i+1 < len(data):
            checksum += (data[i] << 8) + data[i+1]
        else:
            checksum += (data[i] << 8)
    carry = (checksum >> 16)
    checksum = (checksum & 0xffff) + carry
    return checksum

# creating a dictionary of known contacts
sender = {
    "Hanine": ('127.0.0.1', 2223),
    "Pamela": ('127.0.0.2', 2223),
    "Rawan": ('127.0.0.3', 2223),
    "Cynthia": ('127.0.0.4', 2223),
    "Ayman": ('127.0.0.5', 2223),
}

contacts = {
    "Hanine": ('127.0.0.1', 2223),
    "Pamela": ('127.0.0.2', 2223),
    "Rawan": ('127.0.0.3', 2223),
    "Cynthia": ('127.0.0.4', 2223),
    "Ayman": ('127.0.0.5', 2223),
}

# printing the list of contacts
print("Who is the sender of the message?")
global s_name 
global s_ip
global s_port
global s_checksum
global s_ipint
global ipint
ipint = 0
s_ipint = 0

s_name= ""
s_ip = ""
s_port = ""
for name in sender:
    s_name = input("Enter the sender name: ")
    if s_name in sender:
        s_ip, s_port = sender[s_name]
        s_ipint = ip_to_int(s_ip)
        break
    else:
        print("Invalid sender name. Please try again.\n")



print("Hello this is the contact list:")
for name in contacts:
    print(name)



# prompting the user to select a contact from the list
name = ""
global ip 
global port
global checksum
checksum = 0
ip = ""
port = ""   
while True:
    contact_name = input("Enter a contact name to message: ")
    print()
    if contact_name in contacts and contact_name != s_name:
        ip, port = contacts[contact_name]
        name = contact_name
        ipint = ip_to_int(ip)
        break
    else:
        print("Invalid contact name. Please try again.\n")
print("You're in the chat. Type 'close' to exit or sendfile to send a file.\n")



def send():
    global SeqNum
    global ip 
    global port
    global s_ip
    global s_port
    while True:
        # creating a UDP socket using 
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM )
        message = input("") # This blocks until an item is available
        if message == 'close':
           os._exit(1)
        elif message=='sendfile':
            sendfile()

        else:
                # ack bit = 0 & the current sequence number are sent along with the inputted message 
                sm = "{}:{}:{}".format('0', SeqNum, message)
                AckY = SeqNum
                length = len(message)
                sum = udp_checksum(s_ipint, ipint, s_port, port, length, message.encode())
                mask = 0xFFFF  # 16 bits all set to 1
                s_checksum_inv = sum ^ mask
                ss = format(s_checksum_inv, '016b')

                # Append checksum to message and send
                sm += ":" + ss
                s.sendto(sm.encode(), (ip, int(port)))

                while True:
                    # assigning the timeout to be 0.25 second
                    time.sleep(0.25)
                    # resending message if the AckY variable didn't change
                    # this means that an ACK wasn't received yet
                    if AckY == SeqNum:
                        print("Resending message.\n")
                        s.sendto(sm.encode(), (ip, int(port)))
                # message received if the AckY variable changes 
                # this means the sequence number was changed after an ACK was received
                    else:
                        print("Message received.\n")
                        break



def rec():
    global SeqNum
    global checksum
    while (True):
        # creating a UDP socket using 
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM )

        # binding the created socket s to IP and port number assigned to sender
        s.bind((s_ip, 2223))
        
        # receives data from the UDP socket s with a maximum buffer size of 1024 bytes
        # recvfrom() is a blocking call

        rec = s.recvfrom(1024)
        received = rec[0].decode().split(":")
        ackBit = received[0]
        SequenceNum= received[1]
        message1 = received[2].split(":")[-1]
        # print("Message is ", message1)
        # the complement of a sequence number is its opposite, it is used to keep track of ACKs that were lost through the unreliable network
        SeqComplement = '0' if SeqNum =='1' else '1'
        # changing the sequence number if the client receives ACK for a previously sent message
        if ackBit == '1' and SequenceNum == SeqNum:
            if SeqNum == '0':
               SeqNum = '1'
            else:
               SeqNum = '0'
        # changing the sequence number & sending an ACK if the client receives a new message
        elif ackBit == '0' and SequenceNum == SeqNum:
            AcknowledgmentMessage = "Ack"
            sm = "{}:{}:{}".format('1', SeqNum, AcknowledgmentMessage)
            s.sendto(sm.encode(), (ip, int(port)))
            print(">> From " + name + ": " + received[2])
            print()
            
            # Decode message and convert to integer
            s_checksum = received[3]
            s_checksum_int = int(s_checksum, 2)

            # Compute checksum
            checksum = udp_checksum(s_ipint, ipint, int(s_port), int(port), len(message1), message1.encode())

            # Compute sum of checksums and apply bitwise AND with 0xFFFF to ensure it's a 16-bit number
            Summation = (checksum + s_checksum_int) & 0xFFFF
            # print(Summation)

            # Convert sum to binary string
            Summationbin = format(Summation, '016b')
            # print(Summationbin)

            # Check if sum is equal to 0xFFFF
            if Summationbin == "1111111111111111":
                print("message is valid")
            else:
                print("message is invalid")

            if SeqNum == '0':
               SeqNum = '1'
            else:
               SeqNum = '0'  
        # if a non-corrupted message of a complement sequence number is received, we reACK it without changing the sequence number        
        elif ackBit == '0' and SequenceNum == SeqComplement:
            AcknowledgmentMessage = "Ack"
            sm = "{}:{}:{}".format(1, SeqComplement, AcknowledgmentMessage)
            s.sendto(sm.encode(), (ip, int(port))) 





def sendfile():

    # creating a new TCP socket using 
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # attempting to connect the TCP socket to receiver's server
    # printing an error message and exiting the program if the connection is refused by the server
    try:
        sock.connect((ip, 8000))

    except ConnectionRefusedError:
        print("Could not connect.\n")
        exit()

    filename = input('Input file name you want to send: ')

    print()

    while True:
        try:
            # reading file and sending data to receiver's server
            fi = open(filename, "rb")
            data = fi.read()

            # if file is empty then break
            if not data:
                break

            # while file is not empty
            while data:
                sock.send(data)
                data = fi.read()

            # file is closed after data is sent
            print("Data sent successfully.\n")
            fi.close()
            break;

        except IOError:
            print('You entered an invalid file name! Please enter a valid name.\n')
            filename = input('Input filename you want to send: ') 
            print()


def receivefile():
    # creating a new TCP socket using 
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # binding the created socket sock to IP of sender and port number assigned for receiving files 
    sock.bind((s_ip, 8000))

    fileno = 0

    while True:

        # setting the socket to listen for incoming connections, with a  maximum backlog of 1
        # listen() is a blocking call
        sock.listen(1)

        # accepting connection from sender in order to receive a file
        conn = sock.accept()

        filename = 'RcvFile('+str(fileno)+')'
        fileno = fileno+1
        fo = open(filename, "wb")
        
        # conn[0] is the socket object representing the connection between sender and recv
        # receiving data from the socket  with a maximum buffer size of 1024 bytes
        data = conn[0].recv(1024)
        
        # while the file is not completely received yet
        while data:
                if not data:
                        break
                else:
                        fo.write(data)
                        data = conn[0].recv(1024)

        # file is closed after data is sent
        fo.close()
        print('File received successfully! New file name is:', filename)
        conn[0].close()
        print()

global SeqNum

# assigning initial sequence number to be 0
SeqNum = '0'

# creating a thread x1 to execute the send method()
x1 = threading.Thread(target = send)

# creating a thread x2 to execute the rec method()
x2 = threading.Thread(target = rec)

# creating a thread x3 to execute the receivefile method()
x3 = threading.Thread(target = receivefile)


# starting all threads
x1.start()
x2.start()
x3.start()




