import pandas as pd
import numpy as np
import sys
import pickle
import torch
sys.path.append('/opt/ml/level3_productserving-level3-recsys-03/backend')

from model import EASE
from app.firebase_db import get_dataframe, load_database

def split_train_test_proportion(data, test_prop=0.2):
    data_grouped_by_user = data.groupby('user')
    tr_list, te_list = list(), list()

    np.random.seed(98765)
    
    for _, group in data_grouped_by_user:
        n_items_u = len(group)
        
        if n_items_u >= 5:
            idx = np.zeros(n_items_u, dtype='bool')
            idx[np.random.choice(n_items_u, size=int(test_prop * n_items_u), replace=False).astype('int64')] = True

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


def main(lambd, k):
    df = get_dataframe(load_database())[['userUID','problemCode','isCorrect']]
    df = df.drop_duplicates(subset=['userUID','problemCode'],
                                keep='last')
    df= df[df.userUID.map((df.userUID.value_counts()>=5).to_dict())]
    df.columns = ['user','item','rating']

    items = df["item"].unique()
    
    train_df, test_df = split_train_test_proportion(df)

    model = EASE()
    model.fit(df, train_df, lambda_= lambd)
 
    result_df = model.predict(train_df, train_df.user.unique(), items, k)
    recall = Recall_at_k_batch(result_df[["user", "item"]], test_df[["user", "item"]])
    print(f"recall@{k} : {recall}")

    model_dict = {}
    model_dict['B'] = model.B
    model_dict['token2id'] = {j:i for i,j in enumerate(model.item_enc.classes_)}
    model_dict['id2token'] = {i:j for i,j in enumerate(model.item_enc.classes_)}

    with open('/opt/ml/level3_productserving-level3-recsys-03/backend/saved/ease_dict.pkl','wb') as f:
        pickle.dump(model_dict,f)



if __name__ == "__main__":
    main(500, 10)
    

