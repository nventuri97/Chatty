import sys, socket, json, os, time
from _thread import *


def __handle_chat(chatting):
    data, addr=udpSock.recvfrom(4096)
    data=json.loads(data)
    print(addr)
    if (data["code"]==300) & (not chatting):
        print("\nReceive request to chat from "+ data["nick-sender"])
        chatting=True
        response={"code": 301, "msg":"READY_TO_CHAT"}
        udpSock.sendto(json.dumps(response).encode(), addr)


def __start_chat(address, port):
    friendAddr=(address, port)
    data={"code": 300, "msg":"START_NEW_CHAT", "nick-sender": nickname}
    udpSock.sendto(json.dumps(data).encode(), friendAddr)
    response=udpSock.recv(4096)
    response=json.loads(response)
    if response["code"]==301:
        sys.stdout.write("Starting chat with "+friend_nick+"\n")
        sys.stdout.flush()

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

start_new_thread(__handle_chat, (chatting,))
sys.stdout.write("Commands available\n!help\n!connect\n!terminate\n!quit\n")
time.sleep(3)

'''I enter into the main cicle of the client'''
while connected:
    os.system("clear")
    command=input("What do you want to do? ")

    '''I check if there is a space inside the command receive and i split it'''
    if "!connect" in command:
        command=command.split(" ", 2)
        friend_nick=command[1]
        command=command[0]
        print(command)
        print(friend_nick)
    
    if command=="!connect":
        data={"command": command, "nickname": friend_nick}
        sock.sendall(json.dumps(data).encode())

        response=sock.recv(4096)
        response=json.loads(response)
        if response["code"]==200:
            __start_chat(response["ip"], response["port"])
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
    time.sleep(4)

sock.close()