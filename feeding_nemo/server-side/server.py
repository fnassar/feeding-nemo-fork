import socket, threading, sys

MSG_LEN = 14
FORMAT = 'utf-8'
DISCONNECT_MSG = "##DISCONNECT##"

CONNECTIONS = []
SCORES = {1: "000", 2: "000", 3: "000"}

PORT = 4040
# SERVER = socket.gethostbyname(socket.gethostname())
SERVER = ''

ADDRESS = (SERVER, PORT)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(ADDRESS)
except:
    print("[ERROR] Can't bind server to given address.")
    sys.exit()

def start():
    print("STARTING SERVER...")
    server.listen()
    print("[LISTENING]")

    while True:
        con, addr = server.accept()
        thread = threading.Thread(target=communication, args=(con, addr))
        thread.start()

def communication(con, addr):
    print("[NEW CONNECTION]", addr, "_________ [ACTIVE]", threading.activeCount() - 1)

    if len(CONNECTIONS) <= 2:
        CONNECTIONS.append(con)
        con.send(str(len(CONNECTIONS)).encode(FORMAT))

        if len(CONNECTIONS) == 3:
            transmitData("[NEMO.INITIATE]")

        while True:
            print("[SCORES]", getScores())
            msg = ""
            try:
                msg = con.recv(MSG_LEN).decode(FORMAT)
            except:
                disconnect(con, addr)
                break
            
            if msg == DISCONNECT_MSG or msg == "":
                disconnect(con, addr)
                break
            else:
                print("[NEW MESSAGE] FROM", addr, "---", msg)

                try:
                    # update score data
                    data = msg.split(":")
                    player = int(data[0].split("_")[1])
                    score = data[1]

                    if player > 0:
                        SCORES[player] = score
                        con.send(getScores().encode(FORMAT))
                except:
                    disconnect(con, addr)
    else:
        con.send("F".encode(FORMAT))
        disconnect(con, addr)

    con.close()

def getScores():
    s = []
    for item in SCORES:
        s.append(str(item) + ":" + SCORES[item])

    d = ",".join(s)
    return "[" + str(d) + "]"

def disconnect(con, addr):
    if (threading.activeCount() - 2) == 0:
        global SCORES
        SCORES = {1: "000", 2: "000", 3: "000"}
        CONNECTIONS.clear()

    print("[DISCONNECTED]", addr, "_________ [NOW ACTIVE]", threading.activeCount() - 2)

def transmitData(msg):
    for con in CONNECTIONS:
        con.send(msg.encode(FORMAT))

start()