from socket import *
import sys
import time
import threading

serverPort = int(sys.argv[1])
TRY_count = sys.argv[2]

if float(TRY_count) != int(float(TRY_count)) or int(TRY_count)> 5:
    raise ValueError('The login trying number should be the integer between 1 and 5')

TRY_count = int(sys.argv[2])
#user login
def login(connectionSocket): 
    user_list = []
    passwd_list = []
    block_list = []
    try_count = 1

    with open('credentials.txt') as f:
        line = f.readline()
        while line:
            user,passwd = line.strip().split()
            user_list.append(user)
            passwd_list.append(passwd)
            line = f.readline()
    
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
                connectionSocket.send('Welcome to Toom!\n Enter one of the following commands (MSG, DLT, EDT, RDM, ATU, OUT):'.encode())
                return True
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

host = 'localhost'
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind((host,serverPort))
def start():
    serverSocket.listen()
    print('Server is listening...')
    while 1:
        conn, addr = serverSocket.accept()
        thread = threading.Thread(target=login,args=[conn])
        thread.start()
        print(f'[ACTIVE CONNECTIONS] {threading.active_count() - 1}')
start()
        
