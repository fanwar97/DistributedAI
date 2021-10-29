from keras.preprocessing.sequence import pad_sequences
from keras.layers.core import Dense, Dropout, Activation
from keras.layers.embeddings import Embedding
from keras.layers.recurrent import LSTM

from pandas import read_csv, concat

from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, roc_auc_score, log_loss

import tldextract
import os

validChars = {chr(i+45): i for i in range(0, 78)}
maxlen = 127

def do_evaluate(y, probs, round, before, filename, label, end):
    project_dir = os.getcwd() + "/../"
    f = open(project_dir + "Client/log/training_log", "a")
    if before == 1:
        f.write("---------------------Round" + str(round) + "\n")
        # f.write("Round" + str(round) + ":before get avg_weight\n")
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
    else:
        f.write("++++++ after get avg_weight ++++++\n")
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
    # f.write("TP: {}\nTN: {}\nFP: {}\nFN: {}\n".format(tp, tn, fp, fn))
    # f.write("FP rate: {}%\nFN rate: {}%\n".format(fp/(fp+tp)*100, fn/(fn+tn)*100))
    # f.write("Accuracy: {}".format((tp+tn)/(tp+tn+fp+fn)))
    # f.write(f"Precision: {precision}")
    # f.write(f"Recal: {recall}")
    # f.write(f"F1-score: {f1score}")
    if before == 0 and end == 1:
        f.write("-------------------------END OF ROUND " + str(round) + "--------------------------------\n")

def test_with_dic_based_atk(model, round, before):
    test_domain = read_csv(os.getcwd() + "/../attacks/attack_dict_based.txt", names=['domain'])
    test_domain['tld'] = [tldextract.extract(d).domain for d in test_domain['domain']]
    test_domain = test_domain[~test_domain['tld'].str.contains('\`|-\.')]
    test_domain = test_domain.drop_duplicates()
    test_domain['label'] = 1
    test_domain = test_domain.sample(frac=1).reset_index(drop=True)
    X, y = test_domain['tld'], test_domain['label']
    X = [[validChars[y] for y in x] for x in X]
    X = pad_sequences(X, maxlen=maxlen)

    probs = model.predict(X)
    do_evaluate(y, probs, round, before)

def test_with_data(model, avg_weight, round, file, label, end):
    file_to_test = "/../" + file
    test_domain = read_csv(os.getcwd() + file_to_test, names=['domain'], nrows= 20000)
    test_domain['tld'] = [tldextract.extract(d).domain for d in test_domain['domain']]
    test_domain = test_domain[~test_domain['tld'].str.contains('\`|-\.')]
    test_domain = test_domain.drop_duplicates()
    test_domain['label'] = label
    test_domain = test_domain.sample(frac=1).reset_index(drop=True)
    X, y = test_domain['tld'], test_domain['label']
    X = [[validChars[y] for y in x] for x in X]
    X = pad_sequences(X, maxlen=maxlen)

    probs = model.predict(X)
    do_evaluate(y, probs, round, 1, file, label, 0)

    model.set_weights(avg_weight)

    probs2 = model.predict(X)
    do_evaluate(y, probs2, round, 0, file, label, end)