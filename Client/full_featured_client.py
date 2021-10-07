import os
from threading import *
import time
import signal
import sys
from scapy.all import *

sys.path.insert(0, os.getcwd() + "/../")

from detail_proc import *
from glob_inc.print_log import print_log

def handle_sigint(sig, frame):
    global raw_domain_thread
    global is_exit
    print_log("Main thread received SIGINT")
    # raw_domain_thread.stop()
    is_exit = True

def is_stop():
    return is_exit
    
def asyn_capture_domain():
    global queue
    global mutex

    t = AsyncSniffer(iface = "ens33", prn=handle_packet(queue, mutex), store = 0)
    t.start()

def capture_domain():
    global queue
    global mutex

    sniff(iface = "ens33", prn=handle_packet(queue, mutex), store = 0)

def init_domain_capture_thread():
    print_log("Main thread is creating a thread to capture domain . . .")
    thread = Thread(target=asyn_capture_domain(), args=())
    # print_log("CAPTURE DOMAIN THREAD HAS STARTED")
    return thread

def start_periodic_fed_learn_process():
    global cur_model_info
    global client_id
    global round_counter

    t = Timer(time_to_fl + 4, fed_learn_process, args=(host, port, train_file, client_id, cur_model_info, cur_model_file, is_exit, WAIT_TIME * 60, round_counter))
    t.start()
    time.sleep(time_to_fl + 5)
    if is_exit == True:
        t.cancel()
        return
    t.cancel()

def main_comm_process_func():
    global client_id
    global time_to_fl
    if is_exit == True:
        return 
    if client_id == -1:
        client_id, time_to_fl = do_hello_process(host, port, client_id)
        print(f"Start FL request in {time_to_fl}")

    start_periodic_fed_learn_process()

def init_main_comm_thread():
    print_log("Main thread is creating main communication thread . . .")
    thread = Thread(target=main_comm_process_func, args=())
    # thread.daemon = True
    return thread

def init_dga_detection_thread():
    global cur_model_info
    global cur_model_file
    global queue
    global mutex
    print_log("Main thread is creating dga detection thread . . .")
    thread = Thread(target=dga_detection_func, args=(cur_model_file, cur_model_info, queue, mutex, is_exit))
    return thread

def read_conf_file(filename):
    global port
    global host     
    global train_file

    f_config = open(os.getcwd() + "/../" + filename)
    print_log("Main thread is reading config file . . .")
    for lines in f_config:
        split_line = lines.split("=")
        conf_type = split_line[0].strip()
        conf_value = split_line[1].strip()
        if conf_type == "PORT":
            port = conf_value
            port = int(port)
        elif conf_type == "CAPTURE_DUR":
            nfstream_dur = conf_value
        elif conf_type == "TRAIN_FILE":
            train_file = os.getcwd() + "/" + conf_value
        elif conf_type == "SERVER_IP":
            host = conf_value
    f_config.close()

if __name__ == "__main__":
    cur_model_file  = os.getcwd() + "/client_model/simple_LSTM_model"
    cur_model_info = ["non_exist", 0, -1]
    client_id = -1
    is_exit=False
    time_to_fl = 0
    WAIT_TIME = 1
    round_counter = 0

    port = -1
    train_file = "none"
    host = "localhost"
    read_conf_file("distributedai.config")

    queue = []
    mutex = Lock()
    signal.signal(signal.SIGINT, handle_sigint)
    sigset = [signal.SIGINT]
    
    # raw_domain_thread = AsyncSniffer(iface = "ens33", prn=handle_packet(queue, mutex), store = 0, stop_filter = is_exit)
    main_comm_thread = init_main_comm_thread()
    # dga_detection_thread = init_dga_detection_thread()

    main_comm_thread.start()
    print_log(f"Thread control federated learning function has started")
    # dga_detection_thread.start()
    # print_log(f"Thread for dga detection has started")
    # raw_domain_thread.start()
    # print_log(f"Thread for capturing domain from network has started")

    signal.sigwait(sigset)

    # raw_domain_thread.join()
    main_comm_thread.join()
    # dga_detection_thread.join()

    do_goodbye_process(host, port, client_id)

    print_log(f"CLIENT {client_id} HAS STOPPED WORKING", "red")

