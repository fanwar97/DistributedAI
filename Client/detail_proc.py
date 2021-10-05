import socket
import time
from scapy.all import *
from scapy.layers.dns import *
import tldextract
from threading import *
import struct

from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

from glob_inc.print_log import print_log
from message import *
from glob_inc.utils import *
from model import *

# validChars = {chr(i+45):i for i in range(0,78)}

def enqueue(queue, mutex, domain):
    mutex.acquire(1)
    queue.append(domain)
    mutex.release()

def dequeue(queue, mutex):
    if len(queue) > 0:
        mutex.acquire(1)
        i = queue.pop(0)
        mutex.release()
        return i
    else:
        return "Empty"

def handle_packet(queue, mutex):
    def find_domain(packet):
        if packet.haslayer(DNS):
            url = packet[DNSQR].qname
            url_str = url.decode()
            # print(str(packet[DNSQR].qname))
            dns = tldextract.extract(url_str)
            if 'local' in dns.domain:
                pass
            else:
                print(f"Captured domain: {dns.domain}")
                enqueue(queue, mutex, dns.domain)
    return find_domain

def update_current_model(avg_weight, cur_model_info, cur_model_file):
    # if cur_model_info[0] == "wait_for_load":
    #     g_model = tf.keras.models.load_model(cur_model_file)
    #     g_model.summary()
    #     cur_model_info[1] = g_model
    #     cur_model_info[0] = "updated"
    #     return
    current_model = cur_model_info[1]
    current_model.set_weights(avg_weight)
    cur_model_info[1] = current_model

def train_current_model(cur_model_info, train_file):
    if isinstance(cur_model_info[1], int): 
        current_model = tf.keras.models.load_model("simple_LSTM_model")  
    else:     
        current_model = cur_model_info[1]
    
    ret = do_train_model(current_model, train_file)
    # left it empty here for further update
    return ret

def is_new_model_required(cur_model_info, lastest_model_ver):
    lastest_model_ver = float(lastest_model_ver)
    cur_model_ver = cur_model_info[2]
    print(f"{cur_model_ver}, {lastest_model_ver}")
    if lastest_model_ver > cur_model_ver:
        return True
    return False

def fed_learn_process(host, port, train_file, client_id, cur_model_info, cur_model_file, is_exit, time_to_fl):

    if is_exit == True:
        return

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    print_log(f"Client {client_id} has started federated learning proc with server", "green")

    send_flearn_request(sock, client_id)
    lastest_model_ver, time_to_fl_from_sv = recv_flearn_population(sock)
    if lastest_model_ver == b'rejected':
        print("client rejected")
        t = Timer(time_to_fl_from_sv, fed_learn_process, args=(host, port, train_file, client_id, cur_model_info, cur_model_file, is_exit, time_to_fl_from_sv))
        t.start()
        sock.close()
        return
    if is_new_model_required(cur_model_info, lastest_model_ver) == True:
        cur_model_info[0] = "updating"
        send_model_request(sock, lastest_model_ver, client_id)
        recv_global_model(sock, cur_model_file)
        cur_model_info[0] = "wait_for_load"
        cur_model_info[2] = lastest_model_ver
        g_model = tf.keras.models.load_model(cur_model_file)
        g_model.summary()
        cur_model_info[1] = g_model
        cur_model_info[0] = "updated"
    else:
        send_model_fine(sock, client_id)

    if wait_for_training_command(sock) == True:
        updated_weights = train_current_model(cur_model_info, train_file)
    send_weight(sock, updated_weights, client_id)
    avg_weight = recv_weight(sock)
    sock.close()
    update_current_model(avg_weight, cur_model_info, cur_model_file)
    
    if is_exit == True:
        return
    t = Timer(time_to_fl, fed_learn_process, args=(host, port, train_file, client_id, cur_model_info, cur_model_file, is_exit, time_to_fl))
    t.start()

def do_hello_process(host, port, client_id):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    print_log("Client is sending hello message to server", "yellow")
    msg = b'hl'
    sock.send(msg)
    data = sock.recv(1024)
    client_id = int(data[0])
    time_to_fl = int.from_bytes(data[1:len(data)], "big", signed=False)
    print_log(f"Allocated ID: {client_id}", "green")
    sock.close()
    return client_id, time_to_fl

def do_goodbye_process(host, port, client_id):
    print_log("Client is sending goodbye message to server", "yellow")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    msg = b'gb' + int_to_ubyte(client_id)
    sock.send(msg)
    print_log("Client sent goodbye message to server")
    sock.close()

def detect_dga(model, queue, mutex):
    captured_domain = dequeue(queue, mutex)
    if captured_domain != "Empty":
        domain = [[validChars[ch] for ch in captured_domain]]
        domain = pad_sequences(domain, maxlen=maxlen)
        res = model.predict(domain)
        print(f"res = {res}")
        print(f"{captured_domain} is ", end="")
        if res > 0.5:
            print("DGA")
        else:
            print("legal domain")

def check_training_cond(cur_model_info, cur_model_file):
    model_status = cur_model_info[0]

    if model_status == "wait_for_load":
        g_model = tf.keras.models.load_model(cur_model_file)
        cur_model_info[1] = g_model
        cur_model_info[0] = "updated"
        return True
    elif model_status == "updated":
        return True
    else:
        return False

def dga_detection_func(cur_model_file, cur_model_info, queue, mutex, is_exit):
    while is_exit == False:
        if len(queue) > 0:
            if check_training_cond(cur_model_info, cur_model_file) == True:
                # print_log(f"Detecting DGAs with model ver {cur_model_info[2]}")
                detect_dga(cur_model_info[1], queue, mutex)

