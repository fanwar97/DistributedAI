# Import socket module
import socket
import random
import time
import pickle
import sys

import client_utils

if __name__ == '__main__':
	this_client_id = sys.argv[1]
	print(this_client_id)
	recv_gmodel = False
	host = 'localhost'
	port = 12345
	s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	s.connect((host,port))
	s.setblocking(True)
	client_utils.send_client_id(s, this_client_id)
	if  recv_gmodel == False:
		recv_ok = client_utils.recv_gmodel(s, "recv_gmodel.sav")
		if recv_ok == True:
			loaded_model = pickle.load(open("recv_gmodel.sav", 'rb'))
			print(loaded_model)
	if client_utils.recv_training_cmd(s) == True:
		# Fake training
		print("Training")
		time.sleep(3)
		print("finish training")

		fake_weight = [int(this_client_id),2,3,4,5,21,0, 1.11111, [1,2,3, 1,1,1,1,1,1,1,11,1]]
		client_utils.send_weight(s, fake_weight)

	s.close()