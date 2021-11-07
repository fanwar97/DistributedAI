from keras.preprocessing.sequence import pad_sequences
from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation
from keras.layers.embeddings import Embedding
from keras.layers.recurrent import LSTM

from pandas import read_csv, concat

from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, roc_auc_score, log_loss

import tldextract
import numpy as np
import tensorflow as tf
import sys
import os
validChars = {chr(i+45): i for i in range(0, 78)}
maxlen = 127
def do_evaluate(y, probs, round, filename, label):
    f = open("log/standalone_char.log", "a")
    f.write("---------------------Round" + str(round) + "\n")
    num_sample = len(y)
    count = 0
    for i in range(0, num_sample):
        if label == 1 and probs[i] >= 0.5:
            count += 1
        if label == 0 and probs[i] < 0.5:
            count += 1
    rate = count / num_sample
    f.write(f"Detection rate for {filename}: {rate}\n")
    y2 = y.to_numpy(dtype='float64')
    y2 = y2.reshape(y2.shape[0], 1)
    probs = probs.astype('float64')
    cross_entropy = log_loss(y2, probs, labels=[1,0])
    f.write(f"Cross-Entropy/Log loss for {filename}: {cross_entropy}\n")
    f.write("-------------------------END OF ROUND " + str(round) + "--------------------------------\n")
    f.close()
def choose_file_in_folder_by_order(folder, file_order):
    dir_name = folder
    # Get list of all files in a given directory sorted by name
    list_of_files = sorted( filter( lambda x: os.path.isfile(os.path.join(dir_name, x)),
                        os.listdir(dir_name) ) )
    return list_of_files[file_order]

def test_with_char_based(model, i):
    test_file = os.getcwd() + "/../attacks/attack_char_based.txt";
    print(f"testing with {test_file}")
    train_domain = read_csv(test_file, names=['domain'])
    train_domain['tld'] = [tldextract.extract(d).domain for d in train_domain['domain']]
    train_domain = train_domain[~train_domain['tld'].str.contains('\`|-\.')]
    train_domain = train_domain.drop_duplicates()
    train_domain['label'] = 1
    train_domain = train_domain.sample(frac=1).reset_index(drop=True)
    X, y = train_domain['tld'], train_domain['label']
    X = [[validChars[y] for y in x] for x in X]
    X = pad_sequences(X, maxlen=maxlen)
    probs = model.predict(X)
    do_evaluate(y, probs, i, "char_based", 1)

if __name__ == "__main__":

    current_model = tf.keras.models.load_model("client_model/simple_LSTM_model")
    current_model.summary()
    
    for i in range(1, 11):
        file_to_train = choose_file_in_folder_by_order("train_file/", i - 1)
        print(f"train with {file_to_train}")
        train_file = "train_file/" + file_to_train
        train_domain = read_csv(train_file, names=['domain'])
        train_domain['tld'] = [tldextract.extract(d).domain for d in train_domain['domain']]
        train_domain = train_domain[~train_domain['tld'].str.contains('\`|-\.')]
        train_domain = train_domain.drop_duplicates()
        train_domain['label'] = 1
        train_domain = train_domain.sample(frac=1).reset_index(drop=True)
        X, y = train_domain['tld'], train_domain['label']
        X = [[validChars[y] for y in x] for x in X]
        X = pad_sequences(X, maxlen=maxlen)
        current_model.fit(X,y, batch_size=16, epochs=1)    
        # if necessary, evaluate the model here
        probs = current_model.predict(X)
        test_with_char_based(current_model, i)
