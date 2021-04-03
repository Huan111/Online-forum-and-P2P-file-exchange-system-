########### Please use python3 to run the codes. ##########
########### Usage: python3 server.py port_number try_times ###########
############ This program is simulate the server behaviour with different functions ########

from socket import *
import sys
import time
import datetime
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
            connectionSocket.send('Please enter your password:'.encode())
            passwd = connectionSocket.recv(1024).decode()
        
        # only input passwd
        else:
            passwd = connectionSocket.recv(1024).decode()
        
        #block the user if is in block list
        if user in block_list:
                connectionSocket.send('Failed.Your account is still in blocked, please try later.'.encode())
                break
        
        #check passwd
        if passwd == passwd_list[idx]:
            #successfully login in. added to active user log
            print(f'{user} logged in.')
            connectionSocket.send(f'Welcome {user}!\nEnter one of the following commands (MSG, DLT, EDT, RDM, ATU, OUT, UPD):'.encode())
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
            return user
        else:
            #passwd is not correct
            if try_count < TRY_count:
                connectionSocket.send(f'Password is not correct. Left trying time: {TRY_count - try_count}. Please reenter your password:'.encode())
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
def logout(conn,user):

    #find the log out user seq number
    with open('userlog.txt','r') as f:
        d = f.readlines()
        for i in d:
            name = i.strip().split('; ')[2]
            if user == name:
                idx = int(i.strip().split('; ')[0])
                break
            else:
                continue
    
    #delete the user from the active table
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
def post_message(user,message):
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
    print(f'{user} posted MSG # {idx} "{message}" at {temp_t}')
    return f'Message #{idx} posted at {temp_t}'

#user delete the message
def delete_message(user,check_list):
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
            print(f'{user} failed to delete MSG at {cur_t}')
            return 'Delete the message failed. Please check the input.'
        
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
            print(f'{user} deleted MSG # {idx} "{msg}" at {cur_t}')
            return f'Delete the message successfully. Message #{idx} deleted at {cur_t}.'
    #if the messages file is not created.
    except:
        cur_t = time.ctime()
        print(f'{user} failed to delete MSG at {cur_t}')
        return 'Delete the message failed. There is no messages'

#user edit the message
def edit_message(user,check_list):
    user_msg_list = []
    check = ' '.join(check_list[:5]) + ' ' + user
    new_msg = ' '.join(check_list[5:])
    
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
            print(f'{user} failed to edit MSG at {cur_t}')
            return 'Edited the message failed. Please check the input.'
        
        #start to edit message
        else:
            idx = user_msg_list.index(check) + 1
            with open('messagelog.txt','r+') as f:
                d = f.readlines()
                f.seek(0)
                for i in d:
                    temp_lst = i.strip().split('; ')
                    #replace the message and update information
                    if int(temp_lst[0]) == idx:
                        t = time.ctime().split()
                        cur_t = t[2] + ' ' + t[1] + ' ' + t[-1] + ' ' + t[-2]
                        temp_lst[1] = cur_t
                        temp_lst[-1] = 'yes'
                        temp_lst[-2] = new_msg
                        i = '; '.join(temp_lst) + '\n'
                    else:
                        pass
                    f.write(i)
                f.truncate()
            cur_t = time.ctime()
            print(f'{user} edited MSG # {idx} "{new_msg}" at {cur_t}')
            return f'Edit the message successfully. Message #{idx} edited at {cur_t}.'
    
    #if no message file created
    except:
        cur_t = time.ctime()
        print(f'{user} failed to Edit MSG at {cur_t}')
        return 'Edit the message failed. There is no messages'

#user read new message
def read_message(user,check_list):
    date_time_str = ' '.join(check_list)

    #check if input datetime format correct,conver to datetime object
    try:
        comp_date = datetime.datetime.strptime(date_time_str, '%d %b %Y %H:%M:%S')
    except:
        print(f'{user} issued RDM command failed.')
        return 'Read message fail. Invalid datetime format.Please follow(dd mm yyyy hh:mm:s).'
    
    #Reading message, compare to the request time, if bigger, add to the msg
    try:
        msg = ''
        with open("messagelog.txt", "r") as f:
            d = f.readlines()
            for i in d:
                temp = i.strip().split('; ')
                temp_date = temp[1]
                date_time_obj = datetime.datetime.strptime(temp_date, '%d %b %Y %H:%M:%S')
                if date_time_obj >= comp_date:
                    if temp[-1] == 'no':
                        msg += '#' + temp[0] + '; ' + temp[-3] + ': ' + f'"{temp[-2]}" ' + 'posted at ' + temp[1] + '.\n'
                    else:
                        msg += '#' + temp[0] + '; ' + temp[-3] + ': ' + f'"{temp[-2]}" ' + 'edited at ' + temp[1] + '.\n'
                else:
                    continue
        
        #if no new message
        if msg == '':
            print(f'{user} issued RDM command failed.')
            return 'Read message failed. There is no new message'
        
        #send required messages
        else:
            print(f'{user} issued RDM command.\nReturn message:\n{msg}')
            return f'Read message successfully. The new message is:\n{msg}'
    
    #if message file not created
    except:
        print(f'{user} issued RDM command failed.')
        return 'Read the message failed. There is no messages'

#user apply for current active users
def download_active_users(user):
    active_count = 0

    #read the active user file
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
    
    #only one user active
    if active_count == 0:
        print(f'{user} issued ATU command ATU.')
        return 'Currently no other user is in active.'
    
    #return user list
    else:
        print(f'{user} issued ATU command ATU.')
        print(f'Return active user list: \n{temp_str}')
        return temp_str

#user issued uploaded file
def upload_file(user,temp_list):
    #if the input is not corret, return back the message
    if len(temp_list) != 2:
        return 'Unsuccessfully require sending file. Input format not correct. Please retry.'

    check_user = temp_list[0]
    file_name = temp_list[1]
    users = []
    ips = []
    ports = []

    #read the current active users
    with open('userlog.txt') as f:
        d = f.readlines()
        for i in d:
            lst = i.strip().split('; ')
            users.append(lst[-3])
            ips.append(lst[-2])
            ports.append(lst[-1])
    
    #if target user is not active
    if check_user not in users:
        return 'Unsuccessfully require sending file. Target user is not active.'

    #Server send back the detail of the target user to sender
    else:
        msg = 'Transfer '
        idx = users.index(check_user)
        des_ip = ips[idx]
        des_port = ports[idx]
        file_name = user + '_' + file_name
        msg += des_ip + ' ' + des_port + ' ' + file_name + ' ' + check_user
        return msg

#main function to handle user message
def handle_client(conn, addr):
    user = login(conn,addr[0])
    if user:
        print(f'[NEW CONNECTION] {addr} connected.')
        connected = True
    else:
        connected = False
    while connected:
        msg = conn.recv(1024).decode()
        temp_str = msg.strip().split()
        command = temp_str[0]
        check_str = temp_str[1:]
        
        #Dealing with all kinds of different functions
        if command == ACTIVATE_USERS or command == DISCONNECT_MESSAGE:
            if len(temp_str) != 1:
                conn.send(f'Invalid format of {command}. There should be no arguments for this command. Please retry:'.encode())
                continue
            else:  
                if command == DISCONNECT_MESSAGE:
                    connected = False
                    logout(conn,user)
                    break
                else:
                    res = download_active_users(user)
        elif command == POST_MESSAGE:
            temp_meg = ' '.join(check_str)
            res = post_message(user,temp_meg)
        elif command == DELETE_MESSAGE:
            res = delete_message(user,check_str)
        elif command == EDIT_MESSAGE:
            res = edit_message(user,check_str)
        elif command == UPLOAD_FILE:
            res = upload_file(user,check_str)
        elif command == READ_MESSAGE:
            res = read_message(user,check_str)
        else:
            conn.send('Invalid command. Please use available command (MSG, DLT, EDT, RDM, ATU, OUT, UPD):'.encode())
            continue
        res += '\nEnter one of the following commands (MSG, DLT, EDT, RDM, ATU, OUT, UPD):'
        conn.send(res.encode())
    conn.close()


#SERVER = 'localhost'

#get server name
SERVER = gethostbyname(gethostname())

serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind((SERVER,serverPort))

#server multithreading process
def start():
    serverSocket.listen()
    print(f'Server is listening,the IP address is {SERVER}.')
    while 1:
        conn, addr = serverSocket.accept()
        thread = threading.Thread(target=handle_client,args=[conn,addr])
        thread.start()
        print(f'[ACTIVE CONNECTIONS] {threading.active_count() - 1}')
    
start()
        
