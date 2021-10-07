import socket
import sys
import pickle
import os
import threading
import struct

from glob_inc.print_log import print_log
from glob_inc.utils import *

def recvall(sock, n):
    # Helper function to recv n bytes or return None if EOF is hit
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data

def recv_client_id(s):
    print_log("Receiving client id . . .")
    data = s.recv(4)
    if data[0:2] == b'id':
        print(data[2], data[3])
        return data[2], data[3]
    else:
        print_log("CLIENT IS NOT SENDING ID", "red")
        return "fault"

def send_gmodel(sock, filepath):
    filesize = os.path.getsize(filepath)
    print_log("SERVER IS SENDING GLOBAL MODEL TO CLIENT", "yello")
    print_log(f"The size of the Gmodel file is {filesize} byte(s)", show_time=False)
    f = open(filepath, 'rb')
    content = f.read()
    f.close()
    data = struct.pack('>I', filesize) + content
    sock.sendall(data)
    print_log("SERVER SENDS GLOBAL MODEL --- FINISHED", "green")

def send_training_cmd(s, client_id):
    msg = b'training'
    print_log(f"SENDING TRAINING COMMAND TO CLIENT {client_id}", "yellow")
    s.send(msg)
    print_log("FINISHED SEND TRAINING COMMAND", "green")

def recv_updated_weight(sock):
    print_log("SERVER IS RECEVING UPDATED WEIGHTS", "yellow")
    raw_data = recvall(sock, 5)
    if not raw_data:
        return None
    client_id = int(raw_data[4])
    raw_data = raw_data[0:4]
    weight_size = struct.unpack('>I', raw_data)[0]
    print_log(f"The size of the receiving weight is {weight_size} byte(s)", show_time=False)
    weight_byte = recvall(sock, weight_size)
    weight = pickle.loads(weight_byte)
    print_log("SERVER RECEIVED UPDATED WEIGHTS FROM CLIENT", "green")
    return weight

def recv_hello(sock, addr):
    data = sock.recv(1024)
    if data == b'hello':
        print_log("Receive hello message from {addr}")

def send_weight(sock, weight, client_id):
    print_log(f"server is sending avg_weight to client {client_id}", "yellow")
    weight_byte = pickle.dumps(weight)
    weight_size = len(weight_byte)
    print("The size of the sending weight is", weight_size, "byte(s)")
    data = struct.pack('>I', weight_size) + weight_byte
    sock.sendall(data)
    print_log(f"server sent avg_weight to client {client_id}", "green")

def send_flearn_population(conn, cur_model_info):
    version = cur_model_info[2]
    msg = b'fl_pop' + version
    conn.send(msg)

def recv_model_requirement(conn):
    raw_data = conn.recv(1024)
    if raw_data[0:7] == b'model_r':
        return 1
    elif raw_data[0:7] == b'model_f':
        return 0;