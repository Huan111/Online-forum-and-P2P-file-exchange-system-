# Python Socket programming: Online forum and P2P file exchange system

##  General Description
This project is using python socket progamming to simulate online forum functionality in both server and clients
sides.

---

## Program Design
This online videoconferencing and messaging application is implemented by two main python3 programs: server.py, client.py.  Each part achieved by similar code design.

**Server side:**
It contains of 3 main parts. 

- First part is defined of different basic application functions, such as login, post message, delete message, edit message, download active users, and upload file so on. In this part, different usages written into different functions which separated from each other and using for the next integrated part. Most of the functions are based on the data storing and reading from the txt file. For example, to implement block the user for 10 seconds, after he/she exceeded the try number, the username and the time will be stored in the block.txt file. In the next time login, the login function will record the username and current time and match the data in that file. If the time difference is no more than 10s, the function will return an error message and refuse to login. If 10s exceeded, the server will allow the user to login and erase the username data in the block file. Other basic functions are most based on this file writing and retrieving methods to achieve their functionalities. 

- The second part is integrated function handle_client(). This function contains all the call of the part1 functions by recognized the corresponding command. These commands are represented by the constant value such as POST_MESSAGE = ‘MSG’. It also deals with the receiving the message send by the client side and send back the responds, as well as close the server.  

- The finial part is the start() function which contains the multi-threading to and call the handle_client function to start the server and wait for connecting. The multi-threading part is implemented by the python threading module with passing the integrated function and arguments.

**Client side:**

This usage also contains 3 parts. 

- First part is implementing the TCP connection. This is achieved by the TCP_server_handler function and used to dealing with the server-side functions based on the TCP connections, such as login, post message and so on. It uses the first character of the respond message, (in code, is data[0]) to decide what kind of messages it currently dealing with. Because each particular function responses are designed to embed with different starting word, so is makes this method became possible to routing to different functions. For example, ‘F’ and ’S’ are represented login failure and logout success which cause disconnect with the server. ‘T’ is for P2P file exchange and ‘W’ is for login success and send the user UDP data to server. The others are dealing with basic responses.

- The second part is P2P file exchange functions. It includes UDP_Server_handler() and send_file(). First function is to act as the UDP client-side server which run as the client login to main server. It keeps listening the requirements with buffering the segment data. Send_file function is for sending the file to the target client. It first read the local file with read_size which segments the file into different chunk to send. With each sending, these is a flow control time.sleep(1), which control the sending time interval to guarantee the successful of receiving entire file. After finished the sending, it will send a ‘Finished’ message to indicate the ending of sending file and reset the buffer to empty.

- Final part is implementing multi-threading between TCP and UDP services, which call by the start() function. Because we want both sender and receiver can doing other TCP connecting basic functions while sending or receiving the file, those 2 parts should run without affecting each other. There are 3 threading in the client sides functions which corresponding to the part1 and 2 functions. The send_file function thread is embedded in the TCP_server_handler thread undering the ‘T’ condition. After calling the start function, the TCP and UDP server threads should start and the send_file thread is waiting for calling from the client.

---

## Features
- User login and logout
- Message post, edit, delete and read
- Check the current active users
- Multi-clients supports
- P2P file exchanges

---

## Usage Examples

**Activate the server**

**Terminal 1**
```bash
# python3 server.py port passwd_attempt_times
$ python3 server.py 4000 3
```
After running it, you will see a activated message with server ip address which is the ip address of the host machine.

**Teminal 2**
```bash
# python3 client.py server_ip server_port client_udp_port
$ python3 client.py 127.0.0.1 4000 6666

```
After that, you will see the prompt in the client to imply you to enter the user name and password. A sample crenditials.txt file has been provided. You can define your own crenditials file.

```bash
Please enter the user name: Hans
Please enter the password:Jedi*knight
$ Welcome Hans!
Enter one of the following commands (MSG, DLT, EDT, RDM, ATU, OUT):

```
**Fourm functions**
- Yoda executes MSG command followed by a command that is not supported. Obi-wan executes
MSG. Yoda and Obi-wan execute log out.

**Yoda’s Terminal** 
```
> Enter one of the
following commands (MSG,
DLT, EDT, RDM, ATU,
OUT,UPD): MSG Hello
> Message #1 posted at
23 Feb 2021 15:00:01.
> Enter one of the
following commands (MSG,
DLT, EDT, RDM, ATU,
OUT): whatsthedate
> Invalid command. Please
retry.
> Enter one of the
following commands (MSG,
DLT, EDT, RDM, ATU,
OUT):

> Enter one of the
following commands (MSG,
DLT, EDT, RDM, ATU,
OUT): OUT
> Successfully logout, seya Yoda!
```

**server’s Terminal**
```
> Yoda posted MSG #1
“Hello” at 23 Feb 2021
15:00:01.
14
> Obi-Wan issued RDM
command.
> Return messages:
#1 Yoda: “Compute
Network Rocks” posted at
23 Feb 2021 15:00:01.

> Yoda logout.

> Obi-wan logout.
```

**Obi-wan’s Terminal** 
```
> Enter one of the
following commands (MSG,
DLT, EDT, RDM, ATU,
OUT): RDM 23 Feb 2021
15:00:00
> #1; Yoda: “Hello”
posted at 23 Feb 2021
15:00:01.
> Enter one of the
following commands (MSG,
DLT, EDT, RDM, ATU,
OUT):

> Enter one of the
following commands (MSG,
DLT, EDT, RDM, ATU,
OUT): OUT
> Successfully logout, seya Obi-wan!
```

**P2P communication**
P2P communication:  Before Yoda uploads a video file lecture1.mp4
to Obi-wan, Yoda issues the `ATU` command to find out the IP address and UDP server port
number of Obi-wan.

**Yoda’s Terminal**
```bash
$ Enter one of the
following commands (MSG,
DLT, EDT, RDM, ATU, OUT,
UPD): ATU
> Obi-wan, 129.129.2.1,
8001, active since 23 Feb
2021 16:00:01.
Han, 129.128.2.1, 9000,
active since 23 Feb 2021
16:00:10

$ Enter one of the
following commands (MSG,
DLT, EDT, RDM, ATU, OUT,
UPD): UPD Obi-wan
lecture1.mp4
> lecture1.mp4 has been
uploaded

$ Enter one of the
following commands (MSG,
DLT, EDT, RDM, ATU, OUT,
UPD):
```
**Obi-wan’s Terminal**
```bash
$ Enter one of the
following commands (MSG,
DLT, EDT, RDM, ATU, OUT,
UPD):








$ Received lecture1.mp4
from Yoda
$ Enter one of the
following commands (MSG,
DLT, EDT, RDM, ATU, OUT,
UPD):
```

**Server’s Terminal**

```
> Yoda issued ATU command
ATU.
> Return active user
list: Obi-wan;
129.129.2.1; 8001; active
since 23 Feb 2021
16:00:01. (assume that
the IP address and UDP
server port number of
Obi-wan are 129.129.2.1
and 8001 respectively.)
Hans; 129.128.2.1; 9000;
active since 23 Feb 2021
16:00:10 (assume that
Hans is active with this
details).
(note that the server is
not aware of the P2P UDP
communication between
Yoda and Obi-wan)
```

---

## Important usage notes
Here are some situations that may have bothering, or problems that causing some functions can not implement correctly.
- Please make sure credentials file exists before running the program. Other files can be created by the program when it’s running.
- When test the program in same machine, please make sure that the main server ip is the same as client TCP connection address. This is because the code using gethostbyname(gethostname()) to define both main server and client UDP server ip address but storing the client ip address in the server side by conn, addr = socket.accept(). This ensures the P2P file exchange process work successfully. If the P2P file exchange failed due to this situation, please comment out the SERVER = ‘localhost’ in the server.py and UDP_server = ‘localhost’ in client.py to test the P2P functions.

---

## Future improvement:
The program is not support with the user not in that credentials.txt and will not throw out error. For achieving this, we can first search through the file to find if there is a match or not, then throw back the error if the user does not exist. Also adding creating the user account as writing new user data into credentials.txt.

---

## License
>You can check out the full license [here](https://github.com/Huan111/Python-socket-programming-Online-forum-and-P2P-file-exchange-system-/blob/master/LICENSE)

This project is licensed under the terms of the **MIT** license.