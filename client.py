########### Please use python3 to run the codes. ##########
########### Usage: python3 client.py server_ip port_number UDP_port_number ############
########### This program is simulate the client behaviour with server interation ########

from socket import *
import sys
import time
import threading
import os

if len(sys.argv) != 4:
    raise ValueError('Invalid arguments. The terminal command format should meet: python3 client.py server_IP server_port client_udp_port.')

serverName = sys.argv[1]
serverPort = int(sys.argv[2])
UDPport = sys.argv[3]
#t_lock=threading.Condition()
connected = True

def send_file(file_name,local_file_name,read_size,des_ip,des_port,UDPclientSocket):
    with open(local_file_name, "rb") as video:
        temp = video.read(read_size)
        while temp:
            time.sleep(1)
            UDPclientSocket.sendto(temp,(des_ip, des_port))
            #print('send filr to user')
            temp = video.read(read_size)
            #msg,serverAddress = UDPclientSocket.recvfrom(2048)
            #print(f'Received from server {serverAddress}: received {msg} bytes')
        UDPclientSocket.sendto('Finished'.encode(),(des_ip, des_port))
        #print('finished')
        UDPclientSocket.close()

def TCP_server_handler():

    global connected
    global file_name
    read_size = 65500
    message = ''

    while connected:
        #with t_lock:
        data = clientSocket.recv(1024).decode()

        #user login and other input commands
        if data[0] != 'F' and data[0] != 'S' and data[0] != 'W' and data[0] != 'T':
            message = input(data)
            while message.strip() == '':
                message = input('Input should not be empty. Please enter again:')
            clientSocket.send(message.encode())

        #user login succeffully,sending udp port number
        elif data[0] == 'W':
            clientSocket.send(UDPport.encode())
            message = input(data)
            clientSocket.send(message.encode())

        #UDP transfer file
        elif data[0] == 'T':
            #get the target informations
            des_ip, des_port, file_name = data.strip().split('\n')[0].split()[1:]
            user_name = file_name.split('_')[0]
            local_file_name = file_name.split('_')[1]
            des_port = int(des_port)
            #print(f'ip:{des_ip} desport:{des_port} file_name:{file_name}, username:{user_name}, local_file:{local_file_name}')

            print("Sending video..")
            UDPclientSocket = socket(AF_INET, SOCK_DGRAM)
            UDPclientSocket.sendto(file_name.encode(),(des_ip,des_port))
            UDPclientthread = threading.Thread(target=send_file,args=[file_name,local_file_name,read_size,des_ip,des_port,UDPclientSocket])
            UDPclientthread.start()

            msg = f"{local_file_name} has been sent to {user_name}\n" + data.strip().split('\n')[1] 
            message = input(msg)
            clientSocket.send(message.encode())

        #logout or other failure
        else:
            print(data)
            clientSocket.close()
            connected = False
            UDPclientSocket = socket(AF_INET, SOCK_DGRAM)
            UDPclientSocket.sendto('Disconnected'.encode(),(UDP_server,int(UDPport)))
            #print(f'connected is {connected}')
            #t_lock.notify()

#Simulate UDP server
def UDP_Server_handler(UDPserverSocket):

    global connected
    global file_name
    write_size = 65500
    buffer = ''
    #file_name = ''

    while connected:

        if not buffer:
            file_name,clientAddress = UDPserverSocket.recvfrom(write_size)
            buffer = 'Y'
        buffer,clientAddress = UDPserverSocket.recvfrom(write_size)
        
        with open(file_name, "ab") as video:
            video.write(buffer)
        
        if buffer == b'Disconnected':
            #print('received disconnected')
            connected = False
            break

        if buffer == b'Finished':
            #print('finished')
            sender = file_name.decode().split('_')[0]
            print()
            print(f'Recived file from {sender}')
            print('Enter one of the following commands (MSG, DLT, EDT, RDM, ATU, OUT, UPD):')
            continue
        
#TCP connect
clientSocket = socket(AF_INET, SOCK_STREAM)

#UDP connect
#read the server ip address through command line

#Define UDP server and client sockets
#UDP_server = os.popen('ip addr show eth0').read().split("inet ")[1].split("/")[0]
#UDP_server = 'localhost'
#UDP_server = gethostbyname(gethostname())

#fing private ip

def find_ip():
    s = socket(AF_INET, SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    res = s.getsockname()[0]
    s.close()
    return res
UDP_server = find_ip()
UDPserverSocket = socket(AF_INET, SOCK_DGRAM)
UDPserverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
UDPclientSocket = socket(AF_INET, SOCK_DGRAM)
UDPserverSocket.bind((UDP_server,int(UDPport)))
#print(f'UDP server is {UDP_server},port is {UDPport}')

#TCP_server_handler()

#UDP_thread=threading.Thread(name="UDP_Server", target=UDP_Server_handler)
#UDP_thread.daemon=True
#UDP_thread.start()

#main function
def start(): 
    clientSocket.connect((serverName, serverPort))
    TCPthread=threading.Thread(name="TCP_Server", target=TCP_server_handler)
    TCPthread.start()
    UDPserverthread = threading.Thread(target=UDP_Server_handler,args=[UDPserverSocket])
    UDPserverthread.start()
    
start()

