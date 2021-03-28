
from socket import *
import sys
import time
#Define connection (socket) parameters
#Address + Port no
#Server would be running on the same host as Client
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
    if data[0] != 'F' and data[0] != 'D' and data[0] != 'W':
        message = input(data)
        while message.strip() == '':
            print('Input should not be empty. Please enter again.')
            message = input(data)
        clientSocket.send(message.encode())
    elif data[0] == 'W':
        clientSocket.send(UDPport.encode())
        message = input(data)
        clientSocket.send(message.encode())
    else:
        print(data)
        clientSocket.close()
        connected = False