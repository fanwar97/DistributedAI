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

validChars = {chr(i+45):i for i in range(0,78)}
# maxlen = 63
maxlen = 127
# def test_gg(validChars, X, y, model):
#     gg = "google"
#     gg_c = [validChars[y] for y in gg] 
#     gg_c = pad_sequences(gg_c, maxlen=maxlen)
#     print("result test gg")
#     res = model.predict(gg_c)
#     print(res)

def do_train_model(current_model, train_file):
    print(f"train with file {train_file}")
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
    # test_gg(validChars, X, y, current_model)
    current_model.fit(X_train, y_train, batch_size=16, epochs=1)    
    # test_gg(validChars, X, y, current_model)
    # if necessary, evaluate the model here
    probs = current_model.predict(X)
    
    tn, fp, fn, tp = confusion_matrix(y, probs > 0.5).ravel()
    print("TRAINING RESULT:------------------------------------------")
    print("TP: {}\nTN: {}\nFP: {}\nFN: {}\n".format(tp,tn,fp,fn))
    print("FP rate: {}%\nFN rate: {}%\n".format(fp/(fp+tp)*100,fn/(fn+tn)*100))
    precision = tp/(tp+fp)
    print("Precision: ", precision)
    print("Accuracy: {}\n".format((tp+tn)/(tp+tn+fp+fn)))

    return current_model.get_weights()