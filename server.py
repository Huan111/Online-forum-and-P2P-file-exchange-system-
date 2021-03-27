from socket import *
import sys

serverPort = int(sys.argv[1])
TRY_count = int(sys.argv[2])

#user login
def login():    
    user_list = []
    passwd_list = []
    try_count = 0
    with open('credentials.txt') as f:
        line = f.readline()
        while line:
            user,passwd = line.strip().split()
            user_list.append(user)
            passwd_list.append(passwd)
            line = f.readline()

    while try_count < TRY_count:
        try:
            user = input('Please enter the user name:')
            passwd = input('Please enter the password:')
            idx = user_list.index(user)
            if passwd == passwd_list[idx]:
                print('login success')
                return True
                break
            else:
                print('User name or password is not correct. Please try again')
                try_count += 1
                print(f'Left trying time: {TRY_count - try_count}')
                continue
        except:
            print('User name or password not correct. Please try again.')
            try_count += 1
            print(f'Left trying time: {TRY_count - try_count}')
    print('You have tried many times, please come back later.')
    return False

serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('localhost', 5050))
