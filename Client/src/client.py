import sys, socket, json, threading

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

'''I enter into the main cicle of the client'''
connected=True
while connected:
    command=input("What do you want to do? ")

    '''I check if there is a space inside the command receive and i split it'''
    if command.__contains__(" "):
        pos=command.index(" ")
        command=command[:pos]
        friend_nick=command[pos+1:]
    
    if command=="!connect":
        data={"command": command, "nickname": friend_nick}
        sock.sendall(json.dumps(data).encode())

        response=sock.recv(4096)
        response=json.loads(response)
        if response["code"]==200:
            sys.stdout.write("Starting chat with "+friend_nick)
            __start_chat(response["address"], response["port"])
        else:
            sys.stdout.write(response["message"])
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
        for i in data["commands"]:
            sys.stdout.write(i)
            sys.stdout.flush()
    else:
        sys.stdout.write("Error, command not found")
        sys.stdout.flush()
sock.close()


def __start_chat(self, address, port):
    pass