from glob_inc.print_log import print_log
from glob_inc.utils import *
import pickle
import struct

def recvall(sock, n):
    # Helper function to recv n bytes or return None if EOF is hit
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data

def send_flearn_request(sock, client_id):
    print_log(f"Client {client_id} is starting federated learning process", color_="yello")
    msg = b'fl' + int_to_ubyte(client_id)
    sock.send(msg)

def recv_flearn_population(sock):
    data = sock.recv(1024)
    print(data)
    if data[0:6] == b'fl_pop':
        print_log(f"Received federated learning population")
        return data[6:9], 0
    elif data[0:6] == b'fl_ref':
        time_to_fl = int.from_bytes(data[6:len(data)], "big", signed=False)
        return b'rejected', time_to_fl

def send_model_request(sock, model_version, client_id):
    print_log(f"Client {client_id} send model request: need version {model_version}")
    msg = b'model_r' + int_to_ubyte(client_id) + b'v' + model_version
    sock.send(msg)

def send_model_fine(sock, client_id):
    print_log(f"Client {client_id} does not need new model")
    msg = b'model_f' + int_to_ubyte(client_id)
    sock.send(msg)

def recv_global_model(sock, current_model_file):
    print_log("Client is receiving global model . . .", "yellow")
    raw_data = recvall(sock, 4)
    if not raw_data:
        return False
    filesize = struct.unpack('>I', raw_data)[0]
    print("The size of the receiving file is", filesize, "byte(s)")
    content = recvall(sock, filesize)
    f = open(current_model_file, 'wb')
    f.write(content)
    f.close()
    print_log("CLIENT HAS RECEIVED GLOBAL MODEL", "yellow")

def wait_for_training_command(sock):
    data = sock.recv(1024)
    if data == b'training':
        print_log(f"Client recevied training command", "yellow")
        return True
    else:
        return False

def send_weight(sock, weight, client_id):
    print_log("CLIENT IS SENDING UPDATED WEIGHT TO SERVER", "yellow")
    weight_byte = pickle.dumps(weight)
    weight_size = len(weight_byte)
    print("The size of the sending weight is", weight_size, "byte(s)")
    data = struct.pack('>I', weight_size) + int_to_ubyte(client_id) + weight_byte
    sock.sendall(data)
    print_log("CLIENT SENT WEIGHT TO SERVER", "green")

def recv_weight(sock):
    print_log("CLIENT IS RECEIVING AVG WEIGHT", "yellow")
    raw_data = recvall(sock, 4)
    if not raw_data:
        return None
    weight_size = struct.unpack('>I', raw_data)[0]
    print_log(f"The size of the receiving weight is {weight_size} byte(s)", show_time=False)
    weight_byte = recvall(sock, weight_size)
    weight = pickle.loads(weight_byte)
    print_log("CLIENT RECEIVED UPDATED WEIGHTS FROM SERVER", "green")
    return weight
