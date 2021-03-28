from socket import *
import sys
import time
import threading

if len(sys.argv) != 3:
    raise ValueError('Invalid arguments. The terminal command should meet the format: python3 server.py serverport number_of_consecutive_failed_attempts.')
serverPort = int(sys.argv[1])
TRY_count = sys.argv[2]
DISCONNECT_MESSAGE = 'OUT'


if float(TRY_count) != int(float(TRY_count)) or int(TRY_count)> 5:
    raise ValueError('The login trying number should be the integer between 1 and 5')
TRY_count = int(TRY_count)

#user login
def login(connectionSocket,address): 
    user_list = []
    passwd_list = []
    block_list = []
    try_count = 1
    #Get the users and passwds
    with open('credentials.txt') as f:
        line = f.readline()
        while line:
            user,passwd = line.strip().split()
            user_list.append(user)
            passwd_list.append(passwd)
            line = f.readline()
    #Produce block list
    try:
        with open("block.txt", "r+") as f:
            d = f.readlines()
            t = time.time()
            f.seek(0)
            for i in d:
                b_t = float(i.strip().split()[1])
                if (t - b_t) <= 10:
                    f.write(i)
            f.truncate()

        with open("block.txt") as f:
            d = f.readlines()
            for i in d:
                block_list.append(i.strip().split()[0])
    except:
        pass

    while True:
        connectionSocket.send('Please enter your username:'.encode())
        user = connectionSocket.recv(1024).decode()
        print(f'user is {user}')
        connectionSocket.send('Please enter your password:'.encode())
        passwd = connectionSocket.recv(1024).decode()
        print(f'passwd is {passwd}')
        if user in user_list:
            idx = user_list.index(user)
        else:
            if try_count < TRY_count:
                connectionSocket.send(f'User name or password not correct. Please try again. Left trying time: {TRY_count - try_count}\n'.encode())
                try_count += 1
                continue
            else:
                t = str(time.time())
                temp = user + ' ' + t + '\n'
                with open('block.txt','a') as f:
                    f.write(temp)
                connectionSocket.send('Failed.You have tried many times and the account has been blocked, please come back later.\n'.encode())
                break
        if passwd == passwd_list[idx]:
            if user in block_list:
                connectionSocket.send('Failed.Your account is still in blocked, please try later.'.encode())
                break
            else:
                connectionSocket.send(f'Welcome {user}!\nEnter one of the following commands (MSG, DLT, EDT, RDM, ATU, OUT):'.encode())
                UDP_port = connectionSocket.recv(1024).decode()
                t = time.ctime().split()
                temp_t = t[2] + ' ' + t[1] + ' ' + t[-1] + ' ' + t[-2]
                try:
                    with open('userlog.txt') as f:
                        d = f.readlines()
                    idx = len(d) + 1
                    with open('userlog.txt','a') as f:
                        temp = str(idx) + '; ' + temp_t + '; ' + user + '; ' + address + '; ' + UDP_port + '\n'
                        f.write(temp)
                except:
                    idx = 1
                    with open("userlog.txt", "a") as f:
                        temp = '1' + '; ' + temp_t + '; ' + user + '; ' + address + '; ' + UDP_port + '\n'
                        f.write(temp)
                return user,idx
        else:
            if try_count < TRY_count:
                connectionSocket.send(f'User name or password is not correct. Please try again. Left trying time: {TRY_count - try_count}\n'.encode())
                try_count += 1
                continue
            else:
                t = str(time.time())
                temp = user + ' ' + t + '\n'
                with open('block.txt','a') as f:
                    f.write(temp)
                connectionSocket.send('Failed.You have tried many times and the account has been blocked, please come back later.\n'.encode())
                break
    return False

def logout(conn,user,idx):
    with open('userlog.txt','r+') as f:
        d = f.readlines()
        f.seek(0)
        for i in d:
            temp_list = i.strip().split('; ')
            if temp_list[2] != user:
                if int(temp_list[0]) > idx:
                    new_idx = str(int(temp_list[0]) - 1)
                    temp_list[0] = new_idx
                    i = '; '.join(temp_list) + '\n'
                else:
                    pass
                f.write(i)
        f.truncate()
    conn.send(f'Successfully disconnted with the server. See ya {user}!'.encode())

def handle_client(conn, addr):
    user,idx = login(conn,addr[0])
    if user:
        print(f'[NEW CONNECTION] {addr} connected.')
        connected = True
    else:
        connected = False
    while connected:
        msg = conn.recv(1024).decode()
        if msg == DISCONNECT_MESSAGE:
            connected = False
            logout(conn,user,idx)
    conn.close()

SERVER = 'localhost'
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind((SERVER,serverPort))

def start():
    serverSocket.listen()
    print('Server is listening...')
    while 1:
        conn, addr = serverSocket.accept()
        thread = threading.Thread(target=handle_client,args=[conn,addr])
        thread.start()
        print(f'[ACTIVE CONNECTIONS] {threading.active_count() - 1}')

start()
        
