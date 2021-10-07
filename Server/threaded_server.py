# import socket programming library
import socket
import threading
import time
import sys
import math
import os
from sklearn.neural_network import MLPClassifier

sys.path.insert(0, os.getcwd() + "/../")

from server_utils import *
from glob_inc.print_log import print_log
from glob_inc.utils import *

def remain_to_fl(start_time, duration):
    cur_time = time.time()
    remain_time = duration*60 - (cur_time - start_time)
    remain_time = math.floor(remain_time)
    if remain_time < 0:
        return 0
    else:
        return remain_time

def handle_hello_msg(conn, addr):
    global id_ip_map_list

    for i in range(len(id_ip_map_list)):
        if id_ip_map_list[i] == 'none':
            id_ip_map_list[i] = addr
            print_log(f"allocate id = {i} for client {addr}", "yellow")
            conn.send(int_to_ubyte(i) + int_to_Nubyte(remain_to_fl(start_wait_time, WAIT_TIME), 32))
            return i

def handle_goodbye_msg(conn, client_id):
    global id_ip_map_list

    client_id = int(client_id)
    id_ip_map_list[client_id] = 'none'
    print_log(f"removed client {client_id}", "red")

def raise_signal(client_id):
    global raise_signal_list

    raise_signal_list[client_id] = 1

def handle_fl_request(conn, client_id):
    global updated_weight_list
    global num_clients_upt_this_round
    client_id = int(client_id)
    send_flearn_population(conn, cur_model_info)
    requirement = recv_model_requirement(conn)
    if requirement == 1:
        print_log(f"Client {client_id} need model version {cur_model_info[2]}")
        send_gmodel(conn, gmodel_path)
    elif requirement == 0:
        pass
    send_training_cmd(conn, client_id)
    updated_weight_list[client_id] = recv_updated_weight(conn)
    num_clients_upt_this_round += 1
    raise_signal(client_id)
    
    while 1:
        if avg_weight_ready == 1:
            send_weight(conn, avg_weight, client_id)
            break
    print_log(f"finish flearn round for client {client_id}")
    conn.close()

def handle_client(conn, addr):
    global num_clients_this_round

    raw_msg = conn.recv(3)

    if raw_msg[0:2] == b'hl':
        print_log(f"Connected to {addr[0]}, {addr[1]} --- hello message", "green")
        handle_hello_msg(conn, addr)
    elif raw_msg[0:2] == b'gb':
        print_log(f"Connected to {addr[0]}, {addr[1]} --- goodbye message", "green")
        handle_goodbye_msg(conn, raw_msg[2])
    elif raw_msg[0:2] == b'fl':
        print_log(f"Connected to {addr[0]}, {addr[1]} --- flearn request message", "green")
        if is_flearn_time == True:
            num_clients_this_round += 1
            handle_fl_request(conn, raw_msg[2])
        else:
            ref = b'fl_ref' + int_to_Nubyte(remain_to_fl(start_wait_time, WAIT_TIME), 32)
            conn.send(ref)

def print_weight(updated_weight_list):
    for i in range(len(updated_weight_list)):
        print_log(f"UPDATED WEIGHT RECV FROM CLIENT {i}", "yellow", False)
        print_log(updated_weight_list[i], show_time=False)

def cal_avg():
    global avg_weight
    global avg_weight_ready
    global id_ip_map_list
    global updated_weight_list
    global raise_signal_list
    list_of_weight = []
    for i in range(MAX_CLIENT):
        if updated_weight_list[i] != -1:
            list_of_weight.append(updated_weight_list[i])
    for i in range(len(list_of_weight[0])):
        for j in range(1, len(list_of_weight) - 1):
            list_of_weight[0][i] += list_of_weight[j][i]
        list_of_weight[0][i] /= num_clients_this_round 
    avg_weight = list_of_weight[0]
    # print_log(f"avg_weight for this round is:")
    # print(avg_weight)    
    avg_weight_ready = 1

def is_time_to_avg():
    for i in range(MAX_CLIENT):
        if id_ip_map_list[i] != 'none' and raise_signal_list[i] == 1:
            pass
        else:
            return 0
    return 1

def do_federated_avg():
    global avg_weight_ready
    global id_ip_map_list
    global updated_weight_list
    global raise_signal_list

    num_client_this_round = 0
    list_of_weight = []

    while 1:
        if is_time_to_avg() == 1:
            for i in range(MAX_CLIENT):
                if raise_signal_list[i] == 1:
                    num_client_this_round += 1
                    list_of_weight.append(updated_weight_list[i])
            cal_avg(list_of_weight, num_client_this_round)
            avg_weight_ready = 1
            raise_signal_list = [-1] * MAX_CLIENT

def stop_federated_learning():
    global is_flearn_time
    global num_clients_this_round
    global num_clients_upt_this_round
    global start_wait_time
    if num_clients_this_round > 0:
        print(f"{num_clients_this_round}, {num_clients_upt_this_round}")
        if num_clients_this_round == num_clients_upt_this_round:
            cal_avg()
    start_wait_time = time.time()
    num_clients_this_round = 0
    num_clients_upt_this_round = 0
    is_flearn_time = False
    print("STOP FEDERATED LEARNING ROUND")    
    t = threading.Timer(WAIT_TIME * 60, start_federated_learning)
    t.start()

def start_federated_learning():
    global is_flearn_time
    global start_wait_time
    global avg_weight_ready
    global avg_weight
    avg_weight = []
    avg_weight_ready = 0
    is_flearn_time = True
    print("START FEDERATED LEARNING ROUND")
    t = threading.Timer(FL_DUR * 60, stop_federated_learning)
    t.start()

if __name__ == '__main__':
    MAX_CLIENT = 20
    WAIT_TIME = 1
    FL_DUR = 1
    gmodel_path = os.getcwd() + "/global_model/my_model_new"
    cur_model_info = [0, 0, b'0.0']
    avg_weight_ready = 0
    num_clients_this_round = 0
    num_clients_upt_this_round = 0
    updated_weight_list =[-1] * MAX_CLIENT
    id_ip_map_list = ['none'] * MAX_CLIENT
    raise_signal_list = [-1] * MAX_CLIENT
    thread_list = []
    avg_weight = []
    is_flearn_time = False
    start_wait_time = time.time()
    
    try:
        # avg_thread = threading.Thread(target=do_federated_avg, args=())
        # avg_thread.daemon = True
        # thread_list.append(avg_thread)
        # avg_thread.start()

        host = "localhost"
        port = 12345
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((host, port))   
        print_log(f"SOCKET BINDED TO PORT {port}", show_time=False)

        
        t = threading.Timer(WAIT_TIME * 60, start_federated_learning)
        t.start()

        # put the socket into listening mode
        s.listen(5)
        print_log("SERVER IS LISTENING . . .")
        # a forever loop until client wants to exit
    
        while True:
            # establish connection with client
            conn, addr = s.accept()
            # Start a new thread and return its identifier
            new_thread = threading.Thread(target=handle_client, args=(conn,addr))
            new_thread.daemon = True
            thread_list.append(new_thread)
            new_thread.start()

    except KeyboardInterrupt:
        for t in thread_list:
            t.join()
        s.close()
        # print_weight(updated_weight_list)
