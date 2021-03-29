########### Please use python3 to run the codes. ##########
########### This program is simulate the client behaviour with server interation ########

from socket import *
import sys
import time


if len(sys.argv) != 4:
    raise ValueError('Invalid arguments. The terminal command format should meet: python3 client.py server_IP server_port client_udp_port.')
serverName = sys.argv[1]
serverPort = int(sys.argv[2])
UDPport = sys.argv[3]

clientSocket = socket(AF_INET, SOCK_STREAM)

clientSocket.connect((serverName, serverPort))
message = ''
connected = True
while connected:
    data = clientSocket.recv(1024).decode()
    #user login and other input commands
    if data[0] != 'F' and data[0] != 'S' and data[0] != 'W' and data[0] != 'M' and data[0] != 'C' and data[0] != 'D':
        message = input(data)
        while message.strip() == '':
            message = input('Input should not be empty. Please enter again:')
        clientSocket.send(message.encode())
    #user login succeffully,sending udp port number
    elif data[0] == 'W':
        clientSocket.send(UDPport.encode())
        message = input(data)
        clientSocket.send(message.encode())
    #sending message, deleting message,active user respense
    elif data[0] == 'M' or data[0] == 'C' or data[0] == 'D':
        print(data)
    #failure
    else:
        print(data)
        clientSocket.close()
        connected = False