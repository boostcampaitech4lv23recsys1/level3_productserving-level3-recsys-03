from fastapi import FastAPI, UploadFile, File
from fastapi.param_functions import Depends
# from pydantic import BaseModel, Field
# from uuid import UUID, uuid4
# from typing import List, Union, Optional, Dict, Any

# from datetime import datetime
from app.firebase_db import load_database, get_user_solved, get_dataframe

# import requests
# from app.model import load_data, tfidf_recommender

from logging import getLogger
import os
import json
import pandas as pd
# import time, datetime


from recbole.config import Config
from recbole.data import create_dataset, data_preparation
from recbole.utils import init_logger, get_trainer, init_seed, set_color

from sklearn.metrics import accuracy_score, roc_auc_score

import torch



### MODEL 설정
# MODEL = 'LightGCN'
# MODEL = 'SLIMElastic'
MODEL = 'SASRec'

app = FastAPI()
db = load_database()
df = get_dataframe(db)


df_sel = df.loc[:, ['userUID', 'problemCode', 'isCorrect', 'solvedAt']]
df_sel['isCorrect'] = df_sel['isCorrect'].apply(int)

df_sel = df_sel.rename(columns={'userUID':'user_id',
                'problemCode':'item_id',
                'isCorrect':'rating',
                'solvedAt':'timestamp'
                })


# 0 - 1 switching
df_sel['rating'] = df_sel['rating'].apply(lambda x: 0 if x==1 else 1)



# 한문제만 푼 유저는 제거
problems_user_solved = df_sel['user_id'].value_counts()
user_over1 = problems_user_solved[problems_user_solved > 1].index

df_sel_over1 = df_sel.set_index('user_id').loc[user_over1, :].reset_index()


df_dd = df_sel_over1.drop_duplicates(subset=['user_id', 'item_id'],
                                keep='last')

df_eval = df_dd.drop_duplicates(subset=['user_id'], keep='last')
df_train = df_dd.drop(index = df_eval.index)


print('전체 데이터 수:', len(df_dd))
print('train 데이터 수:', len(df_train))
print('eval 데이터 수:', len(df_eval))


userid = sorted(list(set(df_dd['user_id'])))
itemid = sorted(list(set(df_dd['item_id'])))
n_user, n_item = len(userid), len(itemid)

userid_2_index = {v:i        for i,v in enumerate(userid)}
itemid_2_index = {v:i+n_user for i,v in enumerate(itemid)}
id_2_index = dict(userid_2_index, **itemid_2_index)


yamldata = """
USER_ID_FIELD: user_id
ITEM_ID_FIELD: item_id
RATING_FIELD: rating
TIME_FIELD: timestamp

load_col:
    inter: [user_id, item_id, rating, timestamp]

user_inter_num_interval: "[0,inf)"
item_inter_num_interval: "[0,inf)"
val_interval:
    rating: "[0,1]"
    timestamp: "[1672892980000, inf)"

neg_sampling: ~
"""

## train data 생성
outpath = f"dataset/train_data"
outfile = f"dataset/train_data/train_data.inter"
yamlfile = f"train_data.yaml"

os.makedirs(outpath, exist_ok=True)

print("Processing Start")
inter_table = []
for user, item, acode, tstamp in zip(df_train.user_id, df_train.item_id, df_train.rating, df_train.timestamp):
    uid, iid = id_2_index[user], id_2_index[item]
    # tval = int(time.mktime(datetime.datetime.strptime(tstamp, "%Y-%m-%d %H:%M:%S").timetuple()))
    inter_table.append( [uid, iid, max(acode,0), tstamp] )

print("Processing Complete")

print("Dump Start")
# 데이터 설정 파일 저장
with open(yamlfile, "w") as f:
    f.write(yamldata) 

# 데이터 파일 저장
with open(outfile, "w") as f:
    # write header
    f.write("user_id:token\titem_id:token\trating:float\ttimestamp:float\n")
    for row in inter_table:
        f.write("\t".join([str(x) for x in row])+"\n")

print("Dump Complete")



## test data 생성
outpath = f"dataset/test_data"
outfile = f"dataset/test_data/test_data.inter"
yamlfile = f"test_data.yaml"

os.makedirs(outpath, exist_ok=True)

print("Processing Start")
inter_table = []
for user, item, acode, tstamp in zip(df_eval.user_id, df_eval.item_id, df_eval.rating, df_eval.timestamp):
    uid, iid = id_2_index[user], id_2_index[item]
    # tval = int(time.mktime(datetime.datetime.strptime(tstamp, "%Y-%m-%d %H:%M:%S").timetuple()))
    inter_table.append( [uid, iid, max(acode,0), tstamp] )

print("Processing Complete")

print("Dump Start")
# 데이터 설정 파일 저장
with open(yamlfile, "w") as f:
    f.write(yamldata) 

# 데이터 파일 저장
with open(outfile, "w") as f:
    # write header
    f.write("user_id:token\titem_id:token\trating:float\ttimestamp:float\n")
    for row in inter_table:
        f.write("\t".join([str(x) for x in row])+"\n")

print("Dump Complete")


logger = getLogger()
config = Config(model=MODEL, dataset='train_data', config_file_list=[f'train_data.yaml'])
config['epochs'] = 100
config['valid_metric'] = 'Recall@10'
config['show_progress'] = False
config['device'] = 'cuda' if torch.cuda.is_available() else 'cpu'


init_seed(config['seed'], config['reproducibility'])

# logger init
init_logger(config)

logger.info(config)

# dataset filtering
dataset = create_dataset(config)
logger.info(dataset)

# dataset splitting
train_data, valid_data, test_data = data_preparation(config, dataset)


# model loading and init
init_seed(config['seed'], config['reproducibility'])

if MODEL == 'LightGCN':
    from recbole.model.general_recommender.lightgcn import LightGCN
    model = LightGCN(config, train_data.dataset).to(config['device'])

if MODEL == 'SLIMElastic':
    from recbole.model.general_recommender.slimelastic import SLIMElastic
    model = SLIMElastic(config, train_data.dataset).to(config['device'])

if MODEL == 'SASRec':
    from recbole.model.sequential_recommender.sasrec import SASRec
    model = SASRec(config, train_data.dataset).to(config['device'])

logger.info(model)

## LightGCN
### 1-0 역전 - 틀릴 문제 추천하기 위해
# trainer loading and initialization
trainer = get_trainer(config['MODEL_TYPE'], config['model'])(config, model)

# model training
# breakpoint()
best_valid_score, best_valid_result = trainer.fit(
    train_data, valid_data, saved=True, show_progress=config['show_progress']
)


# model evaluation
test_result = trainer.evaluate(test_data, load_best_model="True", show_progress=config['show_progress'])

logger.info(set_color('best valid ', 'yellow') + f': {best_valid_result}')
logger.info(set_color('test result', 'yellow') + f': {test_result}')

result = {
    'best_valid_score': best_valid_score,
    'valid_score_bigger': config['valid_metric_bigger'],
    'best_valid_result': best_valid_result,
    'test_result': test_result
}

print(json.dumps(result, indent=4))





# # configurations initialization
# config = Config(model='LightGCN', dataset="test_data", config_file_list=[f'test_data.yaml'])
# config['epochs'] = 1
# init_seed(config['seed'], config['reproducibility'])
# # logger initialization
# init_logger(config)

# # dataset filtering
# test_dataset = create_dataset(config)
# logger.info(test_dataset)

# # 성능 측정
# a_prob = model.predict(test_dataset).tolist()
# a_true = [val for val in test_dataset.inter_feat["rating"]]
# a_pred = [round(v) for v in a_prob] 

# print("Test data prediction")
# print(f" - Accuracy = {100*accuracy_score(a_true, a_pred):.2f}%")
# print(f" - ROC-AUC  = {100*roc_auc_score(a_true, a_prob):.2f}%")