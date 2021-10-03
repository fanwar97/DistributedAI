import pickle
import socket
import signal
import time
import sys

def hello(HOST, PORT):
    global client_id
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    s.sendall(b'ineedid')
    data = s.recv(1024)
    print("Data received from sv", repr(data))
    client_id = int(data[-1])
    print("ID allocated is", client_id)
    s.close()

def goodbye():
    global HOST
    global PORT
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    s.sendall(b'iquit')
    s.close()
    print("client just send goodbye message")
    sys.exit()

def handle_signal(sig, frame):
    print("You just pressed ctrl+C")
    goodbye()
    print("this client has exited properly")

if __name__ == "__main__":
    HOST = 'localhost'
    PORT = 50000
    client_id = -1

    if client_id == -1:
        hello(HOST, PORT)
    
    signal.signal(signal.SIGINT, handle_signal)
    print("Start to wait 10s")
    time.sleep(10)
    print("finished wait 10s")


