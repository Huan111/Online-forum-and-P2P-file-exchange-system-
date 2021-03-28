
from socket import *
import sys
import time
#Define connection (socket) parameters
#Address + Port no
#Server would be running on the same host as Client

serverName = sys.argv[1]

serverPort = int(sys.argv[2])
clientSocket = socket(AF_INET, SOCK_STREAM)

clientSocket.connect((serverName, serverPort))
message = ''
connected = True
while connected:
    data = clientSocket.recv(1024).decode()
    if data[0] != 'F':
        message = input(data)
        clientSocket.send(message.encode())
    else:
        print(data)
        clientSocket.close()
        connected = False