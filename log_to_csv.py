import pandas as pd
import glob
import re
import numpy as np
import matplotlib.pyplot as plt
# Đặt tên file có dạng (training_log_'ten dga'.log)
files = glob.glob("*.log")
count = len(files)
df = pd.DataFrame()
dga_names = []
for f in files:
    # // lấy tên của dga
    dga_names.append(f[13:f.rfind(".")] +'_before')
    dga_names.append(f[13:f.rfind(".")] +'_after')
    csv = pd.read_csv(f)
    df = df.append(csv)
n_round = int((df.size+count)/(5*count))
# Lấy tất cả thông số detection_rate trong các file
detection_rate = []
for i in range(0,df.size):
    line = df.iat[i,0]
    x = re.findall("\d+\.\d+", line)
    if(x):
        detection_rate = np.concatenate([detection_rate,x])
detection_rate_before = np.reshape(detection_rate[::2],(-1,n_round))
detection_rate_after = np.reshape(detection_rate[1::2],(-1,n_round))
header = []
for i in range(0,n_round):
    header.append('Round_'+str(i+1))
data = []
for i in range(0,count):
    data.append(detection_rate_before[i])
    data.append(detection_rate_after[i])
pd.DataFrame(data).to_csv('out.csv',index=False,header = header)
df2 = pd.read_csv('out.csv')

# Thêm cột tên dga
df2.insert(0, "Name", dga_names, False)
pd.DataFrame(df2).to_csv('out.csv',index=False)

# Vẽ biểu đồ 
