"""
Testing trace
"""
import os

os.add_dll_directory("C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v11.4/bin")
# pylint: disable=C0413
import numpy as np
import tensorflow as tf
import tldextract
from keras.preprocessing.sequence import pad_sequences
from pandas import read_csv
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split

# from print_log import print_log
# from message import *
# from utils import *
# from model import *

def do_evaluate(matrix, probs):
    """Evaluate predictions"""
    print(probs)

    tmp = probs.flatten()
    with np.nditer(tmp, op_flags=["readwrite"]) as iterator:
        for value in iterator:
            if value > 0.5:
                value[...] = 1
            else:
                value[...] = 0
    tmp = tmp.astype(int)
    print(tmp)
    true_neg, false_pos, false_neg, true_pos = confusion_matrix(matrix.to_numpy().tolist(),
                                                                tmp.tolist()).ravel()

    precision = true_pos/(true_pos+false_pos)
    recall = true_pos/(true_pos+false_neg)
    f1score = (2*precision*recall)/(precision+recall)
    print(f"TP: {true_pos}\nTN: {true_neg}\nFP: {false_pos}\nFN: {false_neg}\n")
    print(f"FP rate: {false_pos/(false_pos+true_pos)*100}%\n"
            f"FN rate: {false_neg/(false_neg+true_neg)*100}%\n")
    print(f"Accuracy: {(true_pos+true_neg)/(true_pos+true_neg+false_pos+false_neg)}")
    print(f"Precision: {precision}")
    print(f"Recal: {recall}")
    print(f"F1-score: {f1score}")


def cal_avg(a_weight, list_of_weight, num_client_this_round):
    """Calculate average"""
    for i in range(len(list_of_weight[0])):
        for j in range(1, num_client_this_round-1):
            list_of_weight[0][i] += list_of_weight[j][i]
        list_of_weight[0][i] /= num_client_this_round
    a_weight = list_of_weight[0]
    return a_weight


avg_weight = []
validChars = {chr(i+45): i for i in range(0, 78)}
MAXLEN = 127

current_model = tf.keras.models.load_model("saved_model\\model_500_char_based")
current_model.summary()

initial_w = current_model.get_weights()
train_domain = read_csv("benign_500.txt", names=['domain'])
train_domain['tld'] = [tldextract.extract(d).domain for d in train_domain['domain']]
train_domain = train_domain[~train_domain['tld'].str.contains(r'\`|-\.')]
train_domain = train_domain.drop_duplicates()
train_domain['label'] = 0
train_domain = train_domain.sample(frac=1).reset_index(drop=True)
tld_matrix, label_matrix = train_domain['tld'], train_domain['label']
tld_matrix = [[validChars[y] for y in x] for x in tld_matrix]
tld_matrix = pad_sequences(tld_matrix, maxlen=MAXLEN)

tld_train, tld_test, label_train, label_test = train_test_split(tld_matrix, label_matrix,
                                                                test_size=0.2)

guess = current_model.predict(tld_matrix)
do_evaluate(label_matrix, guess)

current_model.fit(tld_train, label_train, batch_size=16, epochs=1)


trained_weights = current_model.get_weights()

weight_list = []
weight_list.append(initial_w)
weight_list.append(trained_weights)

avg_weight = cal_avg(avg_weight, weight_list, 2)
current_model.set_weights(avg_weight)


print("MODEL AFTER CAL AVG")
probs_2 = current_model.predict(tld_matrix)

do_evaluate(label_matrix, probs_2)
