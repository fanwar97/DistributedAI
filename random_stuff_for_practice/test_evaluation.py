from keras.preprocessing.sequence import pad_sequences
from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation
from keras.layers.embeddings import Embedding
from keras.layers.recurrent import LSTM

from pandas import read_csv, concat

from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, roc_auc_score

import tldextract
import numpy as np
import tensorflow as tf
import sys
sys.path.insert(0, "/home/hieupt/DistributedAI")
from glob_inc.print_log import print_log
from Client.message import *
from glob_inc.utils import *
from Client.model import *

def do_evaluate_2(y, probs):
    num_sample = len(y)
    count = 0
    for i in range(0, num_sample):
        if (probs[i] >= 0.5):
            count += 1
    rate = count / num_sample
    print("DECTECTION RATE:", rate)
def do_evaluate(y, probs):
    print(probs)

    tmp = probs.flatten()
    for i in range(len(tmp)):
        if tmp[i] > 0.5:
            tmp[i] = 1
        else:
            tmp[i] = 0
    tmp = tmp.astype(int)
    print(tmp)
    tn, fp, fn, tp = confusion_matrix(y.to_numpy().tolist(), tmp.tolist()).ravel()
    precision = tp/(tp+fp)
    recall = tp/(tp+fn)
    if(tp == 0):
        recall = 1
        precision = 0 if fp > 0 else 1
    f1score = (2*precision*recall)/(precision+recall)
    print("TP: {}\nTN: {}\nFP: {}\nFN: {}\n".format(tp, tn, fp, fn))
    print("FP rate: {}%\nFN rate: {}%\n".format(fp/(fp+tp)*100, fn/(fn+tn)*100))
    print("Accuracy: {}".format((tp+tn)/(tp+tn+fp+fn)))
    print(f"Precision: {precision}")
    print(f"Recal: {recall}")
    print(f"F1-score: {f1score}")


def cal_avg(list_of_weight, num_client_this_round):
    global avg_weight
    for i in range(len(list_of_weight[0])):
        for j in range(1, len(list_of_weight)-1):
            list_of_weight[0][i] += list_of_weight[j][i]
        list_of_weight[0][i] /= num_client_this_round
    avg_weight = list_of_weight[0]


avg_weight = []
validChars = {chr(i+45): i for i in range(0, 78)}
maxlen = 127

current_model = tf.keras.models.load_model("/home/hieupt/DistributedAI/Client/client_model/simple_LSTM_model")
current_model.summary()

initial_w = current_model.get_weights()
train_domain = read_csv("/home/hieupt/DistributedAI/Client/train_file/corebot_500_01.txt", names=['domain'], nrows=10000)
train_domain['tld'] = [tldextract.extract(d).domain for d in train_domain['domain']]
train_domain = train_domain[~train_domain['tld'].str.contains('\`|-\.')]
train_domain = train_domain.drop_duplicates()
train_domain['label'] = 1
train_domain = train_domain.sample(frac=1).reset_index(drop=True)
X, y = train_domain['tld'], train_domain['label']
X = [[validChars[y] for y in x] for x in X]
X = pad_sequences(X, maxlen=maxlen)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

probs = current_model.predict(X)
do_evaluate_2(y, probs)

current_model.fit(X_train, y_train, batch_size=16, epochs=1)


trained_weights = current_model.get_weights()

list_of_weight = []
list_of_weight.append(initial_w)
list_of_weight.append(trained_weights)

cal_avg(list_of_weight, 2)
current_model.set_weights(avg_weight)


print("MODEL AFTER CAL AVG")
probs_2 = current_model.predict(X)

do_evaluate_2(y, probs_2)