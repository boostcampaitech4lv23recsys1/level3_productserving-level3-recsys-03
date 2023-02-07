from scipy.sparse import csr_matrix
import numpy as np
import torch
import pandas as pd

import torch.nn as nn
from sklearn.preprocessing import LabelEncoder
from multiprocessing import Pool, cpu_count


class EASE(nn.Module):
    def __init__(self):
        self.user_enc = LabelEncoder()
        self.item_enc = LabelEncoder()

    def fit(self, data, df, lambda_: float = 0.5, implicit=True):
        self.user_enc.fit(data.loc[:, 'user'])
        self.item_enc.fit(data.loc[:, 'item'])
        
        users, items = self.user_enc.transform(df.loc[:, 'user']), self.item_enc.transform(df.loc[:, 'item'])
        values = (
            np.ones(df.shape[0])
            if implicit
            else df['rating'].to_numpy() / df['rating'].max()
        )

        X = csr_matrix((values, (users, items)))
        self.X = X

        G = X.T.dot(X).toarray()
        diagIndices = np.diag_indices(G.shape[0])
        G[diagIndices] += lambda_
        P = np.linalg.inv(G)
        B = P / (-np.diag(P))
        B[diagIndices] = 0

        self.B = B
        self.pred = X.dot(B)
    
    def forword(self):
        pass

    def predict(self, train, users, items, k):
        items = self.item_enc.transform(items)
        dd = train.loc[train.user.isin(users)]
        dd['ci'] = self.item_enc.transform(dd.item)
        dd['cu'] = self.user_enc.transform(dd.user)
        g = dd.groupby('cu')
        with Pool(cpu_count()) as p:
            user_preds = p.starmap(
                self.predict_for_user,
                [(user, group, self.pred[user, :], items, k) for user, group in g],
            )
        df = pd.concat(user_preds)
        df['item'] = self.item_enc.inverse_transform(df['item'])
        df['user'] = self.user_enc.inverse_transform(df['user'])
        return df

    @staticmethod
    def predict_for_user(user, group, pred, items, k):
        watched = set(group['ci'])
        candidates = [item for item in items if item not in watched]
        pred = np.take(pred, candidates)
        res = np.argpartition(pred, -k)[-k:]
        r = pd.DataFrame(
            {
                "user": [user] * len(res),
                "item": np.take(candidates, res),
                "score": np.take(pred, res),
            }
        ).sort_values('score', ascending=False)
        return r


    def full_sort_predict(self, user):
        r = self.X[user, :] @ self.B
        return torch.from_numpy(r.flatten())
    
    def get_X_B(self):
        return self.X, self.B


    def userUID_predict(self,user_interaction):
        return user_interaction @ self.B