import socket
import pickle
import sys
import time
import struct
from glob_inc.print_log import print_log
from glob_inc.color import color

def recvall(sock, n):
    # Helper function to recv n bytes or return None if EOF is hit
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data

def recv_gmodel(socket, filepath):
    print_log("Client is receiving global model . . .", "yellow")
    raw_data = recvall(socket, 4)
    if not raw_data:
        return False
    filesize = struct.unpack('>I', raw_data)[0]
    print("The size of the receiving file is", filesize, "byte(s)")
    content = recvall(socket, filesize)
    f = open(filepath, 'wb')
    f.write(content)
    f.close()
    print_log("CLIENT HAS RECEIVED GLOBAL MODEL", "yellow")
    return True

def recv_training_cmd(s):
    print_log("CLIENT RECEVING TRAINING COMMAND", "yellow")
    data = s.recv(8)
    # print_log(data)
    if data == b'training':
        return True
    else:
        return False

def send_weight(socket, weight):
    print_log("CLIENT IS SENDING UPDATED WEIGHT TO SERVER", "yellow")
    weight_byte = pickle.dumps(weight)
    weight_size = len(weight_byte)
    print("The size of the sending weight is", weight_size, "byte(s)")
    data = struct.pack('>I', weight_size) + weight_byte
    socket.sendall(data)
    print_log("CLIENT SENT WEIGHT TO SERVER", "green")

def send_client_id(s, id, check_cur_gmodel):
    print_log("CLIENT IS SENDING ID TO SERVER . . .", "yellow")
    msg = b'id'
    msg += id.to_bytes(1, 'big', signed=False)
    if check_cur_gmodel:
        msg += b'\x01'
    else:
        msg += b'\x00'
    print(msg)
    s.send(msg)
    print_log("CLIENT FINISED SENDING ID", "green")

def send_hello(sock):
    print_log("Client is sending hello message to server", "yellow")
    msg = b'hello'
    sock.send(msg)
    data = sock.recv(1024)
    print_log(f"Allocated ID: {repr(data)}", "green")
    client_id = int(data[-1])
    return client_id

def send_goodbye(HOST, PORT):
    print_log("Client is sending goodbye message to server", "yellow")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    msg = b'gdbye'
    sock.send(msg)
    print_log("Client sent goodbye message to server")

