'''
Feeding Nemo
Python script that handles multiplayer data on the
Microsoft Azure VM
'''

import socket, threading, sys

# basic info
MSG_LEN = 14
FORMAT = 'utf-8'
DISCONNECT_MSG = "##DISCONNECT##"

# for active connections
CONNECTIONS = []

# scores for 3 players
SCORES = {1: "000", 2: "000", 3: "000"}

# server info
PORT = 4040
SERVER = ''
ADDRESS = (SERVER, PORT)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    # binding server to the ADDRESS
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(ADDRESS)
except:
    # on error
    print("[ERROR] Can't bind server to given address.")
    sys.exit()

# function that starts listening on the server
def start():
    print("STARTING SERVER...")
    server.listen()
    print("[LISTENING]")

    while True:
        # accepting connections
        con, addr = server.accept()

        # starting the communication thread
        thread = threading.Thread(target=communication, args=(con, addr))
        thread.start()

# function that handles client-server communication
def communication(con, addr):
    print("[NEW CONNECTION]", addr, "_________ [ACTIVE]", threading.activeCount() - 1)

    if len(CONNECTIONS) <= 2:
        CONNECTIONS.append(con)
        # sending the client its player position
        con.send(str(len(CONNECTIONS)).encode(FORMAT))

        # if 3 connections have been made, starting game for everyone
        if len(CONNECTIONS) == 3:
            transmitData("[NEMO.INITIATE]")

        # listening to score changes
        while True:
            print("[SCORES]", getScores())
            msg = ""
            try:
                msg = con.recv(MSG_LEN).decode(FORMAT)
            except:
                disconnect(con, addr)
                break
            
            if msg == DISCONNECT_MSG or msg == "":
                # if the server receives DISCONNECT_MSG
                disconnect(con, addr)
                break
            else:
                print("[NEW MESSAGE] FROM", addr, "---", msg)

                try:
                    # updating score data
                    data = msg.split(":")
                    player = int(data[0].split("_")[1])
                    score = data[1]

                    if player > 0:
                        SCORES[player] = score
                        
                        # sending updated score to the client
                        con.send(getScores().encode(FORMAT))
                except:
                    # on error disconnect the client
                    disconnect(con, addr)
    else:
        # sending "F" if the server already has 3 connections
        con.send("F".encode(FORMAT))
        disconnect(con, addr)

    # closing the connection
    con.close()

# function to get score data
def getScores():
    s = []
    for item in SCORES:
        s.append(str(item) + ":" + SCORES[item])

    d = ",".join(s)
    return "[" + str(d) + "]"

# function to disconnect the client
def disconnect(con, addr):
    if (threading.activeCount() - 2) == 0:
        global SCORES
        SCORES = {1: "000", 2: "000", 3: "000"}
        CONNECTIONS.clear()

    print("[DISCONNECTED]", addr, "_________ [NOW ACTIVE]", threading.activeCount() - 2)

# function to transmit data to all connections
def transmitData(msg):
    for con in CONNECTIONS:
        con.send(msg.encode(FORMAT))

# starting the script
start()