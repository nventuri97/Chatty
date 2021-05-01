import sys, socket, json, os, time
from _thread import *

'''-----------------UTILITY FUNCTIONS-----------------'''
'''Function to start a new chat with a friend
friendAddr: friend's address where we have to link
'''
def start_chat(udpSock, friendAddr, chatting):
    while True:
        if not chatting:
            data={"code": 300, "msg": "START_NEW_CHAT"}
            udpSock.sendto(json.dumps(data).encode(), friendAddr)
            data, friendAddr=udpSock.recvfrom(4096)
            data=json.loads(data)
            if data["msg"]=="ALREADY_BUSY":
                global friend_nick
                print(friend_nick+"is already busy in a chat")
                break
            else:
                chatting=True
        else:
            global nickname
            msg=input(nickname+": ")
            data={"code": 300, "msg": msg}
            udpSock.sendto(json.dumps(data).encode(), friendAddr)

'''Function to receive message from a chat
udpSock: UDP socket to receive message
chatting: boolean that specifies if we are chatting
'''
def handle_chat(udpSock, chatting):
    while True:
        data, friendAddr= udpSock.recvfrom(4096)
        data=json.loads(data)

        if (not chatting) & (data["msg"]=="START_NEW_CHAT"):

            chatting=True
            data={"code": 300, "msg": "READY_TO_CHAT"}
            udpSock.sendto(json.dumps(data).encode(), friendAddr)
            start_chat(udpSock, friendAddr, chatting)
        
        elif (chatting) & (data["msg"]=="START_NEW_CHAT"):

            data={"code": 305, "msg": "ALREADY_BUSY"}
            udpSock.sendto(json.dumps(data).encode(), friendAddr)

        elif data["msg"]=="!terminate":
            break

        else:

            global friend_nick
            print(friend_nick+": "+data["msg"])

'''-----------------MAIN SCRIPT-----------------'''

nickname=input("Insert your nickname: ")
ip=input("Insert your ip address: ")
port=int(input("Insert the port: "))

server_addr=("127.0.0.1", 8081)

try:
    sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error as msg:
    sys.stdout.write('Failed to create socket. Error code: '+ str(msg[0])+ ', Error message: '+str(msg[1]))
    sys.exit()

sock.connect(server_addr)
data={"command": "!new", "nickname": nickname, "ip": ip, "port": port}
sock.sendall(json.dumps(data).encode())

response=sock.recv(4096)
response=json.loads(response)
if response["code"]==500:
    print(response["message"])
    sys.exit()


connected=True
chatting=False
'''UDP socket instantiation'''
udpSock=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udpSock.bind((ip, port))

start_new_thread(handle_chat, (udpSock,chatting, ))
sys.stdout.write("Commands available\n!help\n!connect\n!terminate\n!quit\n")
time.sleep(3)

'''I enter into the main cicle of the client'''
while connected:
    command=input("What do you want to do? ")

    '''I check if there is a space inside the command receive and i split it'''
    if "!connect" in command:
        command=command.split(" ", 2)
        friend_nick=command[1]
        command=command[0]
    
    if command=="!connect":
        data={"command": command, "nickname": friend_nick}
        sock.sendall(json.dumps(data).encode())

        response=sock.recv(4096)
        response=json.loads(response)
        if response["code"]==200:
            start_chat(udpSock, (response["ip"], response["port"]), chatting)
        else:
            sys.stdout.write(response["message"]+"\n")
            sys.stdout.flush()
    elif command=="!quit":

        data={"command": command}
        sock.sendall(json.dumps(data).encode())

        response=sock.recv(4096)
        sys.stdout.write("Client is shutting down")
        sys.stdout.flush()
        connected=False

    elif command=="!help":
        data={"command": command}
        sock.sendall(json.dumps(data).encode())

        data=sock.recv(4096)
        data=json.loads(data)
        '''Print all commands available'''
        sys.stdout.write("Command available\n")
        for i in data["commands"]:
            sys.stdout.write(i+"\n")
            sys.stdout.flush()
    else:
        sys.stdout.write("Error, command not found")
        sys.stdout.flush()

sock.close()