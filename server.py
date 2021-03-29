########### Please use python3 to run the codes. ##########
########### This program is simulate the server behaviour with different functions ########

from socket import *
import sys
import time
import threading

#check the input arguments
if len(sys.argv) != 3:
    raise ValueError('Invalid arguments. The terminal command should meet the format: python3 server.py serverport number_of_consecutive_failed_attempts.')

serverPort = int(sys.argv[1])
TRY_count = sys.argv[2]

#define message types
POST_MESSAGE = 'MSG'
DELETE_MESSAGE = 'DLT'
EDIT_MESSAGE = 'EDT'
READ_MESSAGE = 'RDM'
ACTIVATE_USERS = 'ATU'
UPLOAD_FILE = 'UPD'
DISCONNECT_MESSAGE = 'OUT'

#check the attempt numbers
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
            #if the current time is 10s less than the last failed login time. remain in the block list
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
    
    #inplement login
    while True:
        #first try. with user name and passwd
        if try_count == 1:
            connectionSocket.send('Please enter your username:'.encode())
            user = connectionSocket.recv(1024).decode()
            idx = user_list.index(user)
            #print(f'user is {user}')
            connectionSocket.send('Please enter your password:'.encode())
            passwd = connectionSocket.recv(1024).decode()
            #print(f'passwd is {passwd}')
        
        # only input passwd
        else:
            connectionSocket.send('Please enter your password:'.encode())
            passwd = connectionSocket.recv(1024).decode()
            #print(f'passwd is {passwd}')
        
        #block the user if is in block list
        if user in block_list:
                connectionSocket.send('Failed.Your account is still in blocked, please try later.'.encode())
                break
        
        #check passwd
        if passwd == passwd_list[idx]:
            #successfully login in. added to active user log
            print(f'{user} logged in.')
            connectionSocket.send(f'Welcome {user}!\nEnter one of the following commands (MSG, DLT, EDT, RDM, ATU, OUT, UDP):'.encode())
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
            #passwd is not correct
            if try_count < TRY_count:
                connectionSocket.send(f'password is not correct. Please try again. Left trying time: {TRY_count - try_count}.\n'.encode())
                try_count += 1
                continue
            #try times execeeded. add to block list
            else:
                t = str(time.time())
                temp = user + ' ' + t + '\n'
                with open('block.txt','a') as f:
                    f.write(temp)
                connectionSocket.send('Failed.You have tried many times and the account has been blocked, please come back later.\n'.encode())
                break
    return False

#user log out
def logout(conn,user,idx):
    with open('userlog.txt','r+') as f:
        d = f.readlines()
        f.seek(0)
        #remove the user in the active user log
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
    print(f'{user} logged out.')
    conn.send(f'Successfully disconnted with the server. See ya {user}!'.encode())


#user send the message
def post_message(conn,user,message):
    t = time.ctime().split()
    temp_t = t[2] + ' ' + t[1] + ' ' + t[-1] + ' ' + t[-2]
    try:
        with open('messagelog.txt') as f:
            d = f.readlines()
        idx = len(d) + 1
        with open('messagelog.txt','a') as f:
            temp = str(idx) + '; ' + temp_t + '; ' + user + '; ' + message + '; no'+ '\n'
            f.write(temp)
    except:
        idx = 1
        with open("messagelog.txt", "a") as f:
            temp = '1' + '; ' + temp_t + '; ' + user + '; ' + message + '; no'+ '\n'
            f.write(temp)
    conn.send(f'Message #{idx} posted at {temp_t}'.encode())
    print(f'{user} posted MSG # {idx} "{message}" at {temp_t}')

#user delete the message
def delete_message(conn,user,check_list):
    user_msg_list = []
    check = ' '.join(check_list) + ' ' + user

    try:
        #extract the message file
        with open("messagelog.txt", "r") as f:
            d = f.readlines()
            for i in d:
                lst = i.strip().split('; ')
                temp_user = lst[2]
                temp_mg = lst[1]
                temp_num = lst[0]
                user_msg_list.append( '#' + temp_num + ' ' + temp_mg + ' ' + temp_user)

        #if the 3 condctions are not matched, send back error message 
        if check not in user_msg_list:
            cur_t = time.ctime()
            conn.send('Delete the message failed. Please check the input.'.encode())
            print(f'{user} failed to delete MSG at {cur_t}')
        
        #if match, find the corresponding seq number then delete, and move up
        else:
            idx = user_msg_list.index(check) + 1
            with open('messagelog.txt','r+') as f:
                d = f.readlines()
                f.seek(0)
                for i in d:
                    temp_lst = i.strip().split('; ')
                    if int(temp_lst[0]) != idx:
                        if int(temp_lst[0]) > idx:
                            new_idx = str(int(temp_lst[0]) - 1)
                            temp_lst[0] = new_idx
                            i = '; '.join(temp_lst) + '\n'
                        else:
                            pass
                        f.write(i)
                    else:
                        msg = temp_lst[-2]
                        continue
                f.truncate()
            cur_t = time.ctime()
            conn.send(f'Delete the message successfully. Message #{idx} deleted at {cur_t}.'.encode())
            print(f'{user} deleted MSG # {idx} "{msg}" at {cur_t}')
    
    #if the messages file is not created.
    except:
        cur_t = time.ctime()
        conn.send('Delete the message failed. There is no messages'.encode())
        print(f'{user} failed to delete MSG at {cur_t}')

def edit_message(conn,user):
    pass

def read_message(conn,user):
    pass

def download_active_users(conn,user):
    active_count = 0
    with open('userlog.txt') as f:
        d = f.readlines()
        temp_str = 'Current active users is:\n'
        for i in d:
            temp_list = i.strip().split('; ')
            name = temp_list[2]
            if user == name:
                continue
            t = temp_list[1]
            ip = temp_list[-2]
            port = temp_list[-1]
            temp_str += name + ', '+ ip + ', ' + port + ', active since ' + t +'\n'
            active_count += 1
    if active_count == 0:
        conn.send('Currently no other user is in active.'.encode())
        print(f'{user} issued ATU command ATU.')
    else:
        conn.send(temp_str.encode())
        print(f'{user} issued ATU command ATU.')
        print(f'Return active user list: \n{temp_str}')

def upload_file(conn,user):
    pass

#main function to handle user message
def handle_client(conn, addr):
    user,idx = login(conn,addr[0])
    if user:
        print(f'[NEW CONNECTION] {addr} connected.')
        connected = True
    else:
        connected = False
    while connected:
        msg = conn.recv(1024).decode()
        temp_str = msg.strip().split()
        print(temp_str)
        command = temp_str[0]
        print(command)
        if command == ACTIVATE_USERS or command == DISCONNECT_MESSAGE:
            if len(temp_str) != 1:
                conn.send(f'Invalid format of {command}. There should be no arguments for this command. Please retry:'.encode())
                continue
            else:  
                if command == DISCONNECT_MESSAGE:
                    connected = False
                    logout(conn,user,idx)
                    break
                else:
                    download_active_users(conn,user)
        elif command == POST_MESSAGE:
            temp_meg = ' '.join(temp_str[1:])
            post_message(conn,user,temp_meg)
        elif command == DELETE_MESSAGE:
            temp_check = temp_str[1:]
            delete_message(conn,user,temp_check)
        elif command == EDIT_MESSAGE:
            pass
        elif command == UPLOAD_FILE:
            pass
        elif command == READ_MESSAGE:
            pass
        elif command == ACTIVATE_USERS:
            download_active_users(conn,user)
        else:
            conn.send('Invalid command. Please use available command (MSG, DLT, EDT, RDM, ATU, OUT, UDP):'.encode())
            continue
        conn.send('Enter one of the following commands (MSG, DLT, EDT, RDM, ATU, OUT, UDP):'.encode())
    conn.close()

#define server ip and port
SERVER = 'localhost'
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind((SERVER,serverPort))

#server multithreading process
def start():
    serverSocket.listen()
    print('Server is listening...')
    while 1:
        conn, addr = serverSocket.accept()
        thread = threading.Thread(target=handle_client,args=[conn,addr])
        thread.start()
        print(f'[ACTIVE CONNECTIONS] {threading.active_count() - 1}')

start()
        
