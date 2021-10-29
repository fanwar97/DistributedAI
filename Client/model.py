from keras.preprocessing.sequence import pad_sequences
from keras.models import Sequential
from keras.layers.core import Dense,Dropout,Activation
from keras.layers.embeddings import Embedding
from keras.layers.recurrent import LSTM

from pandas import read_csv,concat

from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix,roc_auc_score

import tldextract
import numpy as np
import os

validChars = {chr(i+45):i for i in range(0,78)}
# maxlen = 63
maxlen = 127

def do_train_model(current_model, train_file):
    print(f"train with file {train_file}")
    current_model.summary()
    train_file = os.getcwd() + "/train_file/" + train_file
    train_domain = read_csv(train_file, names=['domain'])
    train_domain['tld'] = [tldextract.extract(d).domain for d in train_domain['domain']]
    train_domain = train_domain[~train_domain['tld'].str.contains('\`|-\.')]
    train_domain = train_domain.drop_duplicates()
    train_domain['label'] = 1
    train_domain = train_domain.sample(frac=1).reset_index(drop=True)
    X, y = train_domain['tld'], train_domain['label']
    X = [[validChars[y] for y in x] for x in X]
    X = pad_sequences(X, maxlen=maxlen)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    current_model.fit(X_train, y_train, batch_size=16, epochs=1)    
    # if necessary, evaluate the model here
    probs = current_model.predict(X)
        
    # tn, fp, fn, tp = confusion_matrix(y, probs > 0.5).ravel()
    # precision = tp/(tp+fp)
    # recall = tp/(tp+fn)
    # if(tp == 0):
    #     recall = 1
    #     precision = 0 if fp > 0 else 1
    # f1score = (2*precision*recall)/(precision+recall)
    # print("TRAINING RESULT:------------------------------------------")
    # print("TP: {}\nTN: {}\nFP: {}\nFN: {}\n".format(tp, tn, fp, fn))
    # print("FP rate: {}%\nFN rate: {}%\n".format(fp/(fp+tp)*100, fn/(fn+tn)*100))
    # print("Accuracy: {}".format((tp+tn)/(tp+tn+fp+fn)))
    # print(f"Precision: {precision}")
    # print(f"Recal: {recall}")
    # print(f"F1-score: {f1score}")
    num_sample = len(y)
    count = 0
    for i in range(0, num_sample):
        if (probs[i] >= 0.5):
            count += 1
    rate = count / num_sample
    print("DECTECTION RATE:", rate)

    return current_model.get_weights(),  current_model