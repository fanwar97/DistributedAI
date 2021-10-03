import socket

def allocate_id(addr):
    global ip_id_map_list
    for i in range(len(ip_id_map_list)):
        if ip_id_map_list[i] == 'none':
            ip_id_map_list[i] = addr[0]
            print("current list", ip_id_map_list)
            return i
    
def deallocate_id(addr):
    global ip_id_map_list
    for i in range(len(ip_id_map_list)):
        if ip_id_map_list[i] == addr[0]:
            ip_id_map_list[i] = 'none'
    print("current list", ip_id_map_list)

HOST = 'localhost'
PORT = 50000
ip_id_map_list = ['none'] * 10

s = socket.socket(socket.AF_INET, socket. SOCK_STREAM)
s.bind((HOST, PORT))
remaining_time = 2
while(remaining_time > 0):
    s.listen()
    conn, addr = s.accept()
    data = conn.recv(1024)
    if data == b'ineedid':
        id = allocate_id(addr)
        remaining_time -= 1
        conn.sendall(id.to_bytes(1, 'big'))
    if data == b'iquit':
        deallocate_id(addr)
        remaining_time -= 1


