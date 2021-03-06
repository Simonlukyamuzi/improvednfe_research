import xgboost as xgb
from time import time 
import numpy as np
#import pandas as pd
from utils import get_all_files_features_and_labels, seperate_to_train_and_test
from sklearn.model_selection import train_test_split
from sys import argv

def learn_with_XGBClassifier(train_data, train_lbl, test_files, test_lbl, lr=0.22,n_esti=40,seed=123):
    train_time = time()
    xg_cl = xgb.XGBClassifier(objective='multi:softmax', num_class= 10, learning_rate=lr,
                                    n_estimators=n_esti, seed=seed)
    xg_cl.fit(train_data, train_lbl)
    train_time = time() - train_time
    test_time = time()
    preds = xg_cl.predict(test_files)
    test_time = time() - test_time
    accuracy = float(np.sum(preds == test_lbl)) / test_lbl.shape[0]
    return {"train time: ": train_time, "test time: ": test_time, "accuracy: ": accuracy*100}

def learn_with_dt(train_files, train_lbl, test_file, test_lbl):
    train_time = time()
    xg_dt = DecisionTreeClassifier()
    xg_dt = xg_dt.fit(train_files, train_lbl)
    train_time = time() - train_time
    test_time = time()
    preds = xg_dt.predict(test_file)
    test_time = time() - test_time
    accuracy = float(np.sum(preds == test_lbl)) / test_lbl.shape[0]
    return {"train time: ": train_time, "test time: ": test_time, "accuracy: ": accuracy*100}


def learn_with_cv(X,Y):
    t=time()
    early_stopping = 10
    churn_dmatrix = xgb.DMatrix(X,Y)
    params = {"objective": "multi:softmax", "max_depth": 4, "num_class": 10, "silent": 1,
              "seed": 99, }
    cv_results = xgb.cv(dtrain=churn_dmatrix, params=params, nfold=6, num_boost_round=30,
                       metrics="merror", as_pandas=True, early_stopping_rounds=early_stopping)
    t= time()-t
    return {"time: ": t, "params: ": params, "early stopping": early_stopping, "accuracy": cv_results}






def main(malware_dir, benign_dir, ns, num_of_files):
    file = open("results.txt", "a")
    learner ="cv"

    print("start processing input")
    features, labels, ngrams_sets, i2ngram, ngram2i, labels_dict  = get_all_files_features_and_labels(malware_dir,
                                                                                                      benign_dir,
                                                                                                      ns ,num_of_files)

    X, Y = np.array(features), np.array(labels)
    if learner == "Classifier":

        #X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.5, random_state=111)
        X_train, X_test, y_train, y_test = seperate_to_train_and_test(features,labels)
        print("start learning counter...")
        print (learn_with_XGBClassifier(np.array(X_train), np.array(y_train), np.array(X_test), np.array(y_test)))
        X_train, X_test, y_train, y_test = (np.array(X_train) > 0).astype(int), (np.array(X_test) > 0).astype(int), np.array(y_train), np.array(y_test),
        print("start learning bool...")
        print (learn_with_XGBClassifier(X_train, y_train, X_test, y_test))
        pass
    print("strat learning cv")
    res = learn_with_cv((X > 0).astype(int), Y)
    num_res = "real accuracy:{}".format(list(map(lambda x: (1-x)*100,res["accuracy"]["test-merror-mean"])))
    print(res)
    print(num_res)
    file.writelines(str(res))
    file.writelines(str(num_res))
    file.writelines("\n-----------------------------------------------------------------------")
    file.close()

if __name__ == "__main__":
    malware = "/media/user/New Volume/train"
    benign = "/media/user/New Volume/benign"
    ns = [4]
    num_of_files = 100
    if len(argv) >= 3:
        malware = argv[1]
        benign = argv[2]
        if len(argv) >= 4:
            ns = map(int, list(argv[3]))
            if len(argv) >= 5:
                num_of_files = 100

    main(malware, benign, ns, num_of_files)
