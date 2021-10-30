import pandas as pd
import glob
import re
import numpy as np
import matplotlib.pyplot as plt
# Đặt tên file có dạng (training_log_'ten dga'.log)
files = glob.glob("/logs/*.log")
count = len(files)
df = pd.DataFrame()
dga_names = []
for f in files:
    # // lấy tên của dga
    dga_names.append(f[13:f.rfind(".")]+ '_detection_rate' +'_before')
    dga_names.append(f[13:f.rfind(".")]+ '_log_loss' +'_before')
    dga_names.append(f[13:f.rfind(".")]+ '_detection_rate' +'_after')
    dga_names.append(f[13:f.rfind(".")] + '_log_loss' +'_after')
    csv = pd.read_csv(f)
    df = df.append(csv)
n_round = int((df.size+count)/(7*count))

rate = []
for i in range(0,df.size):
    line = df.iat[i,0]
    x = re.findall("\d+\.\d+", line)
    if(x):
        rate = np.concatenate([rate,x])

detection_rate = rate[::2]
log_loss = rate[1::2]

detection_rate_before = np.reshape(detection_rate[::2],(-1,n_round))
detection_rate_after = np.reshape(detection_rate[1::2],(-1,n_round))
log_loss_before = np.reshape(log_loss[::2],(-1,n_round))
log_loss_after = np.reshape(log_loss[1::2],(-1,n_round))

data = []
for i in range (0,4*count):
    if(i%4 == 0):
        a = np.append(dga_names[i],detection_rate_before[int(i/4)])
        data.append(a)
    elif(i%4 == 1):
        b = np.append(dga_names[i],log_loss_before[int((i-1)/4)])
        data.append(b)
    elif(i%4 == 2):
        c = np.append(dga_names[i],detection_rate_after[int((i-2)/4)])
        data.append(c)
    elif(i%4 == 3):
        d = np.append(dga_names[i],log_loss_after[int((i-3)/4)])
        data.append(d)

header = ['Name']
for i in range(0,n_round):
    header.append('Round_'+str(i+1))
pd.DataFrame(data).to_csv('out.csv',index = False,header = header)
    
