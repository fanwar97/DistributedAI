import os
import threading
import time
import socket
import pickle
import signal
import time
import numpy
import pandas as pd
import sys

from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

# from nfstream import NFStreamer
from scapy.all import *
from scapy.layers.dns import *
import tldextract

# import client
import client_utils
from print_log import print_log

def compare_array(arr1, arr2):
    comparison = arr1 == arr2
    equal_arrays = comparison.all()
    # print_log(equal_arrays)
    return equal_arrays

def compare_weights(list1, list2):
    for i in range(len(list1)):
        if compare_array(list1[i], list2[i]) == False:
            return False
    return True

def accuracy(confusion_matrix):
    diagonal_sum = confusion_matrix.trace()
    sum_of_all_elements = confusion_matrix.sum()
    return diagonal_sum / sum_of_all_elements

def enqueue(arr):
    mutex.acquire(1)
    queue.append(arr)
    mutex.release()

    print_log(f"Add {arr} to the queue", "green")
    print_log(f"Number of domain in queue: {len(queue)}", "cyan")
    # print_log (f"Size of queue : {sys.getsizeof(queue)} bytes\n")
        
def dequeue():
    if len(queue) > 0:
        mutex.acquire(1)
        i = queue.pop(0)
        mutex.release()

        print_log(f"Remove \"{i}\" from the queue", "green")
        print_log(f"Number of domain in queue: {len(queue)}", "cyan")
        # print_log (f"Size of queue : {sys.getsizeof(queue)} bytes\n")
        return i
    else:
        return "Empty"
        
def handle_packet(pkt):
    if pkt.haslayer(DNS):
        url = pkt[DNSQR].qname
        url_str = url.decode()
        # print(str(pkt[DNSQR].qname))
        dns = tldextract.extract(url_str)
        print("Captured domain: {dns.domain}")
        enqueue(dns.domain)

""" Function to train MLP model """
def ai_train(model_file, train_file):
    model = pickle.load(open(model_file, 'rb'))
    initial_weights = model.coefs_
    print_log("MODEL INFORMATION")
    print_log(model)

    data = pd.read_csv(train_file)
    data = data[['protocol','bidirectional_duration_ms', 'bidirectional_packets'
                , 'bidirectional_bytes', 'bidirectional_min_ps', 'bidirectional_mean_ps'
                , 'bidirectional_stddev_ps', 'bidirectional_max_ps', 'bidirectional_min_piat_ms'
                , 'bidirectional_mean_piat_ms', 'bidirectional_stddev_piat_ms', 'bidirectional_max_piat_ms'
                , 'Label']]

    # Label encoding
    le = LabelEncoder()
    # data['application_category_name'] = le.fit_transform(data['application_category_name'])

    # sc = StandardScaler()
    # data.iloc[:,0:-1] = sc.fit_transform(data.iloc[:,0:-1])
    # print_log(data)

    # Splitting the dataset into  training and validation sets

    training_set, validation_set = train_test_split(data, test_size = 0.3, random_state = 21)

    # #classifying the predictors and target variables as X and Y
    X_train = training_set.iloc[:,0:-1].values
    Y_train = training_set.iloc[:,-1].values
    X_val = validation_set.iloc[:,0:-1].values
    y_val = validation_set.iloc[:,-1].values

    #Initializing the MLPClassifier
    # classifier = MLPClassifier(hidden_layer_sizes=(150,100,50), max_iter=300,activation = 'relu',solver='adam',random_state=1)

    #Fitting the training data to the network
    print_log("Starting to train Model")
    model.fit(X_train, Y_train)
    y_pred = model.predict(X_val)

    #Printing the accuracy
    cm = confusion_matrix(y_pred, y_val)
    print_log(f"Accuracy of MLPClassifier : {accuracy(cm)}", "yellow", False)
    print(classification_report(y_pred, y_val))

    # weight_matrix = loaded_model.coefs_
    # bias_matrix = loaded_model.intercepts_
    if compare_weights(initial_weights, model.coefs_):
        print_log("Train fail----")
    else:
        print_log("Seem fine-----")
    return model

""" Function to train model each round """
def ai_train_dga(model_file):
    print("THIS IS AI_TRAIN_DGA")
    return [1,2]
def thread_nfstream_func(a, b):
    my_streamer = NFStreamer(source="WannaCry.pcap",
                            bpf_filter=None,
                            promiscuous_mode=True,
                            snapshot_length=1536,
                            idle_timeout=10,
                            active_timeout=10,
                            accounting_mode=0,
                            udps=None,
                            n_dissections=20,
                            statistical_analysis=True,
                            splt_analysis=0,
                            n_meters=0,
                            performance_report=0)
    for flow in my_streamer:
        if flow.id % 1 == 0:
            arr = [flow.protocol, flow.bidirectional_duration_ms, flow.bidirectional_packets
                , flow.bidirectional_bytes, flow.bidirectional_min_ps, flow.bidirectional_mean_ps
                , flow.bidirectional_stddev_ps, flow.bidirectional_max_ps, flow.bidirectional_min_piat_ms
                , flow.bidirectional_mean_piat_ms, flow.bidirectional_stddev_piat_ms, flow.bidirectional_max_piat_ms]
            print_log("nfstream enqueue a flow", "green")
            enqueue(arr)

""" Function to capture network data and save domains in queue """
def capture_domain():
    sniff(iface = "ens33", prn=handle_packet, store = 0)

""" Function to load simple MLP model to detect WannaCry (no longer used) """
def detection(model_file):
    data_str = dequeue()
    if data_str != "Empty":
        model = pickle.load(open(model_file, 'rb'))
        data_arr = numpy.array(data_str)
        data_arr2 = numpy.reshape(data_arr, (-1, 12))
        #Predicting y for X_val
        y_pred = model.predict(data_arr2)
        if "WannaCry" in y_pred:
            print_log("DETECT WANNACRY", "red", False)
        else:
            print_log("NORMAL FLOW", show_time=False)
            

""" Function to load simple LSTM model and detect dga """
def detection_dga(model_file):
    new_model = tf.keras.models.load_model(current_model_file)
    captured_domain = dequeue()
    domain = [[validChars[ch] for ch in captured_domain]]
    print(domain)

    # Check model architecture
    print_log("CURRENT MODEL ARCHITECTURE:", show_time=False)
    new_model.summary()
    res = new_model.predict(domain)
    print(f"{captured_domain} is ", end="")
    if res > 0.5:
        print("DGA")
    else:
        print("legal domain")
""" Define whole communication process vs server """
def comm_process(HOST, POST, train_file):
    global recv_gmodel
    global cur_model_status

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print_log(f"Connecting to server {(HOST, PORT)} . . .", "yellow")
    s.connect((HOST, PORT))
    print_log(f"CLIENT {this_client_id} HAS CONNECTED TO SERVER!", "green")
    
    # client_utils.send_client_id(s, this_client_id, cur_model_status)
    

    if cur_model_status == True:
        pass
    else:
            recv_ok = client_utils.recv_gmodel(s, current_model_file)
            if recv_ok == True:
                cur_model_status = True
                print_log(f"Client {this_client_id} received global model from server", "green")

    if client_utils.recv_training_cmd(s) == True:
        updated_weights = ai_train_dga(current_model_file, train_file)
        # updated_weights = updated_model.coefs_
        client_utils.send_weight(s, updated_weights)
    else:
        print_log("AI thread does not receive correct training command \n", "red")
        print_log("AI THREAD IS TERMINATING . . .", show_time=False)
        s.close()
        return
    s.close()
    
    t = threading.Timer(10, comm_process, args=(HOST, PORT, train_file))
    t.daemon = True
    t.start()

""" Thread AI_func handle communication vs server, detection function and training """
def thread_ai_func(HOST, PORT, train_file):
    global cur_model_status
    global this_client_id

    if this_client_id == -1:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print_log(f"Connecting to server {(HOST, PORT)} to get ID", "yellow")
        sock.connect((HOST, PORT))
        this_client_id = client_utils.send_hello(sock)
        sock.close()

    t = threading.Timer(10, comm_process, args=(HOST, PORT, train_file))
    t.daemon = True
    t.start()
    while True:
        try:
            if cur_model_status == True:
                detection_dga(current_model_file)
        except KeyboardInterrupt:
            print_log("AI THREAD IS TERMINATING . . .", "red")
            t.cancel()
            return

if __name__ == "__main__":
    try:
        current_model_file = "simple_LSTM_model"
        cur_model_status = os.path.exists(current_model_file)
        # this_client_id = sys.argv[1]
        this_client_id = -1
        # this_client_id = int(this_client_id)
        validChars = {chr(i+45):i for i in range(0,78)}
        if this_client_id == -1:
            print_log("This client does not have ID", "red")
        else:
            print_log(f"[Client {this_client_id} is starting . . .]")
            
        f_config = open("distributedai.config", "r")
        print_log("Main thread is reading config file . . .")
        for lines in f_config:
            split_line = lines.split("=")
            conf_type = split_line[0].strip()
            conf_value = split_line[1].strip()
            if conf_type == "PORT":
                port = conf_value
            elif conf_type == "CAPTURE_DUR":
                nfstream_dur = conf_value
            elif conf_type == "TRAIN_FILE":
                train_file = conf_value
            elif conf_type == "SERVER_IP":
                server_ip = conf_value
        print_log("MAIN THREAD FINISHED READING CONFIG FILE")        
        queue = []
        mutex = threading.Lock()
        
        print_log("Main thread is creating caputre domain thread . . .")
        capture_domain_thread = threading.Thread(target=capture_domain(), args=())
        capture_domain_thread.daemon = True
        capture_domain_thread.start()
        print_log("CAPTURE DOMAIN THREAD HAS STARTED")
        
        HOST = server_ip
        PORT = int(port)

        print_log("Main thread is creating ai_thread . . .")
        thread_ai = threading.Thread(target=thread_ai_func, args=(HOST, PORT, train_file))
        thread_ai.daemon = True
        thread_ai.start()
        print_log("AI_THREAD HAS STARTED")
        capture_domain_thread.join()
        thread_ai.join()
        client_utils.send_goodbye(HOST, PORT)

    except KeyboardInterrupt:
        capture_domain_thread.join()
        thread_ai.join()
        client_utils.send_goodbye(HOST, PORT)
        print_log("--------------------------QUIT MAIN THREAD--------------------------", "red")