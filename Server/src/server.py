import sys, socket, json
from _thread import *

def clienthandle(conn):
    connected=True
    nickname=""
    try:
        while connected:
            data=conn.recv(4096)

            data=json.loads(data)
            command=data["command"]
            print(command)
            if(command=="!new"):
                nickname=data["nickname"]
            elif(command=="!connect"):
                friend_nick=data["nickname"]
            global database
            if command=="!new":
                '''Check for the unicity of the nickname'''
                if not data["nickname"] in database:
                    database[nickname]=(data["ip"], data["port"])
                    response={"code": 200}
                else:
                    response={"code": 500, "message": "Nickname already used"}

                conn.sendall(json.dumps(response).encode())
            elif command=="!connect":
                print(friend_nick)
                if (friend_nick in database.keys()):
                    (ip,port)=database[friend_nick]
                    response={"code": 200,
                                "ip": ip,
                                "port": port}
                else:
                    message="No user connected with nickname "+friend_nick
                    response={"code": 500, "message": message}

                conn.sendall(json.dumps(response).encode())
            elif command=="!quit":
                del database[nickname]
                response={"code": 200}
                conn.sendall(json.dumps(response).encode())
            elif command=="!help":
                response={"code": 200, "commands": ["!help", "!connect", "!disconnect", "!terminate", "!quit"]}
                conn.sendall(json.dumps(response).encode())
    except json.JSONDecodeError:
        del database[nickname]
        

IP='127.0.0.1'
PORT=8081
database={}

try:
    sockServer=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error as msg:
    print('Failed to create socket. Error code: '+ str(msg[0])+ ', Error message: '+str(msg[1]))
    sys.exit()

sockServer.bind((IP, PORT))
'''Max number of simultaneous connections'''
sockServer.listen(20)
print("Server ready for listen")

while True:
    conn, addr=sockServer.accept()

    start_new_thread(clienthandle, (conn,))

sockServer.close()