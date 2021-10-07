from keras.preprocessing.sequence import pad_sequences
from keras.layers.core import Dense, Dropout, Activation
from keras.layers.embeddings import Embedding
from keras.layers.recurrent import LSTM

from pandas import read_csv, concat

from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, roc_auc_score

import tldextract
import os

validChars = {chr(i+45): i for i in range(0, 78)}
maxlen = 127

def do_evaluate(y, probs, round, before):
    # print(probs)

    # tmp = probs.flatten()
    # for i in range(len(tmp)):
    #     if tmp[i] > 0.5:
    #         tmp[i] = 1
    #     else:
    #         tmp[i] = 0
    # tmp = tmp.astype(int)
    # print(tmp)
    # tn, fp, fn, tp = confusion_matrix(y.to_numpy().tolist(), tmp.tolist()).ravel()
    # precision = tp/(tp+fp)
    # recall = tp/(tp+fn)
    # if(tp == 0):
    #     recall = 1
    #     precision = 0 if fp > 0 else 1
    # f1score = (2*precision*recall)/(precision+recall)
    # print("TP: {}\nTN: {}\nFP: {}\nFN: {}\n".format(tp, tn, fp, fn))
    # print("FP rate: {}%\nFN rate: {}%\n".format(fp/(fp+tp)*100, fn/(fn+tn)*100))
    # print("Accuracy: {}".format((tp+tn)/(tp+tn+fp+fn)))
    # print(f"Precision: {precision}")
    # print(f"Recal: {recall}")
    # print(f"F1-score: {f1score}")
    project_dir = os.getcwd() + "/../"
    f = open(project_dir + "Client/log/training_log", "a")
    if before == 1:
        f.write("Round" + str(round) + ":before get avg_weight\n")
    else:
        f.write("+++ after get avg_weight +++\n")
    # f.write("TP: {}\nTN: {}\nFP: {}\nFN: {}\n".format(tp, tn, fp, fn))
    # f.write("FP rate: {}%\nFN rate: {}%\n".format(fp/(fp+tp)*100, fn/(fn+tn)*100))
    # f.write("Accuracy: {}".format((tp+tn)/(tp+tn+fp+fn)))
    # f.write(f"Precision: {precision}")
    # f.write(f"Recal: {recall}")
    # f.write(f"F1-score: {f1score}")
    num_sample = len(y)
    count = 0
    for i in range(0, num_sample):
        if (probs[i] >= 0.5):
            count += 1
    rate = count / num_sample
    f.write(f"Detection rate: {rate}\n")
    if before == 0:
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