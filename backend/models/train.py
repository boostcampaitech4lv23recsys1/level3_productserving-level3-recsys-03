import pandas as pd
import numpy as np
import os
import sys
import pickle
import argparse

from preprocess import data_augmentation


sys.path.append('../..') #경로 추가

from model import EASE
from app.firebase_db import pg_get_dataframe, pg_load_database

def split_train_test_proportion(data, test_prop=0.2):
    data_grouped_by_user = data.groupby('user')
    tr_list, te_list = list(), list()

    np.random.seed(98765)
    
    for _, group in data_grouped_by_user:
        n_items_u = len(group)
        
        if n_items_u >= 5:
            idx = np.zeros(n_items_u, dtype='bool')

            # idx[np.random.choice(n_items_u, size=int(test_prop * n_items_u), replace=False).astype('int64')] = True
            idx[np.arange((1-test_prop) * n_items_u,n_items_u).astype('int64')] = True

            tr_list.append(group[np.logical_not(idx)])
            te_list.append(group[idx])
        
        else:
            tr_list.append(group)
    
    data_tr = pd.concat(tr_list)
    data_te = pd.concat(te_list)

    return data_tr, data_te


def Recall_at_k_batch(result_df, test_df_te, k=10):
    result_df = pd.DataFrame(result_df.groupby("user").item.apply(lambda x:set(x)))
    test_df_te = pd.DataFrame(test_df_te.groupby("user").item.apply(lambda x:set(x)))
    df = result_df.merge(test_df_te,on = "user", how = 'inner').reset_index()

    recall = 0
    for i in df.index:
        if len(df.loc[i,"item_y"]) < 10:
            recall += (len(df.loc[i,"item_x"] & df.loc[i,"item_y"])/len(df.loc[i,"item_y"]))
        else:
            recall += (len(df.loc[i,"item_x"] & df.loc[i,"item_y"])/10)

    recall_k = recall/len(df)

    return recall_k


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("--data_aug", default = False, type=bool)
    parser.add_argument("--data_split", default = False, type=bool)
    parser.add_argument("--lambd", default=500, type = float)
    parser.add_argument("--top_k", default=10, type=int)

    args = parser.parse_args()

    db = pg_load_database()
    df = pg_get_dataframe(db)

    df = df[df.problemCode.apply(lambda x: True if x[0] == 'a' else False)]
    df = df.drop_duplicates(subset=['userUID','problemCode'],
                                keep='last')
    df= df[df.userUID.map((df.userUID.value_counts()>=10).to_dict())]

    if args.data_split:
        df = data_augmentation.df_split(df) # Dats split

    if args.data_aug:
        df = data_augmentation.preprocess(df, db) # Data Augmentation

    df = df[['userUID','problemCode','isCorrect']]
    df.columns = ['user','item','rating']
    df['rating'] = df['rating'].apply(lambda x: 0 if x else 1)

    items = df["item"].unique()
    
    train_df, test_df = split_train_test_proportion(df)

    model = EASE()
    model.fit(df, train_df, lambda_= args.lambd)
    
    result_df = model.predict(train_df, train_df.user.unique(), items, args.top_k)
    test_df = test_df[test_df.rating == 1]
    recall = Recall_at_k_batch(result_df[["user", "item"]], test_df[["user", "item"]])
    print(f"recall@{args.top_k} : {recall}")

    model_dict = {}
    model_dict['B'] = model.B
    model_dict['token2id'] = {j:i for i,j in enumerate(model.item_enc.classes_)}
    model_dict['id2token'] = {i:j for i,j in enumerate(model.item_enc.classes_)}

    with open(os.getcwd() + '/saved/ease_false.pkl','wb') as f:
        pickle.dump(model_dict,f)



if __name__ == "__main__":
    main()
    

