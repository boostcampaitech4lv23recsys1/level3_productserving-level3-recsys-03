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
import importlib

from recbole.config import Config
from recbole.data import create_dataset, data_preparation
from recbole.utils import init_logger, get_trainer, init_seed, set_color

from sklearn.metrics import accuracy_score, roc_auc_score

import torch
import argparse

from utils import get_model, predict_for_all_item  # model import 하는 함수
 

### Parse Arguments
parser = argparse.ArgumentParser()

# MODEL = 'LightGCN'
# MODEL = 'SLIMElastic'
# MODEL = 'SASRec'
# MODEL = 'BERT4Rec'
# MODEL = 'GRU4Rec'
parser.add_argument("--model", default="SASRec", type=str)
parser.add_argument("--neg_sample", action='store_true')
parser.add_argument("--load_df", action='store_true')
parser.add_argument("--file_name", default=None, type=str)
parser.add_argument("--epoch", default=100, type=int)
parser.add_argument("--config_file", default='seq_data.yaml', type=str)


args = parser.parse_args()

if args.load_df:
    df = pd.read_csv('dataset/'+args.file_name)

else:
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

# 5명 제외
fiveguys = [
    'EZKg2x3FgvRNiQfgK0iNy1iz54k2',
    'Bq56PPLqLXQLGijMt7QLH9p3hyU2',  # 태엽 아이디중 테스트용
    'rFW8tuibA9cYaOummBR5nS5ucI53',
    'bR5SdsiXAlUoPmZAnWldnfhLJs92',
    'LH8ERBe1DpXavxtNNxKE0KIPyio2'
]
df_sel = df_sel.set_index('user_id').drop(fiveguys).reset_index()


# 0 - 1 switching
df_sel['rating'] = df_sel['rating'].apply(lambda x: 0 if x==1 else 1)






# 다섯문제 이상 푼 유저만 남김 - 
# sequential model은 효과적으로 나눌수있으므로 주석처리
# problems_user_solved = df_sel['user_id'].value_counts()
# user_over1 = problems_user_solved[problems_user_solved >= 5].index

# df_sel_over1 = df_sel.set_index('user_id').loc[user_over1, :].reset_index()


df_dd = df_sel.drop_duplicates(subset=['user_id', 'item_id'],
                                keep='last')

# 이전 문제풀이 sequence 추가
# item_list_by_user = df_sel.groupby('user_id')['item_id'].apply(list)

# df_sel['cumcount'] = df_sel.groupby('user_id')['item_id'].cumcount()

# df_sel = df_sel.set_index('user_id')
# df_sel.loc[:, 'item_id_list'] = item_list_by_user
# df_sel.loc[:, 'item_id_list_seq'] = df_sel.apply(lambda x: x.item_id_list[:int(x.cumcount)], axis=1)
# df_sel = df_sel.reset_index()

# df_sel.loc[:, 'item_id_list'] = df_sel.loc[:, 'item_id_list_seq']

# del df_sel['item_id_list_seq'], df_sel['cumcount']


# train, test 나누기
df_eval = df_dd.drop_duplicates(subset=['user_id'], keep='last')
# df_train = df_sel.drop(index = df_eval.index)

# train, test 안나누고 전체 데이터로 진행
df_train = df_dd.copy()   

# print('전체 데이터 수:', len(df_sel))
# print('train 데이터 수:', len(df_train))
# print('eval 데이터 수:', len(df_eval))


userid = sorted(list(set(df_sel['user_id'])))
itemid = sorted(list(set(df_sel['item_id'])))
n_user, n_item = len(userid), len(itemid)

# userid_2_index = {v:i        for i,v in enumerate(userid)}
# itemid_2_index = {v:i+n_user for i,v in enumerate(itemid)}
# id_2_index = dict(userid_2_index, **itemid_2_index)


## train data 생성
outpath = f"dataset/train_data"
outfile = f"dataset/train_data/train_data.inter"
# yamlfile = f"train_data.yaml"

os.makedirs(outpath, exist_ok=True)

print("Processing Start")
inter_table = []
for user, item, rating, tstamp in zip(df_train.user_id, df_train.item_id, df_train.rating, df_train.timestamp):
    # uid, iid = id_2_index[user], id_2_index[item]
    # tval = int(time.mktime(datetime.datetime.strptime(tstamp, "%Y-%m-%d %H:%M:%S").timetuple()))
    inter_table.append( [user, item, rating, tstamp] )

print("Processing Complete")

print("Dump Start")
# # 데이터 설정 파일 저장
# with open(yamlfile, "w") as f:
#     f.write(yamldata) 

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
# yamlfile = f"test_data.yaml"

os.makedirs(outpath, exist_ok=True)

print("Processing Start")
inter_table = []
for user, item, rating, tstamp in zip(df_eval.user_id, df_eval.item_id, df_eval.rating, df_eval.timestamp):
    # uid, iid = id_2_index[user], id_2_index[item]
    # tval = int(time.mktime(datetime.datetime.strptime(tstamp, "%Y-%m-%d %H:%M:%S").timetuple()))
    inter_table.append( [user, item, rating, tstamp] )

print("Processing Complete")

print("Dump Start")
# # 데이터 설정 파일 저장
# with open(yamlfile, "w") as f:
#     f.write(yamldata) 

# 데이터 파일 저장
with open(outfile, "w") as f:
    # write header
    f.write("user_id:token\titem_id:token\trating:float\ttimestamp:float\n")
    for row in inter_table:
        f.write("\t".join([str(x) for x in row])+"\n")

print("Dump Complete")


logger = getLogger()
config = Config(model=args.model, dataset='train_data', config_file_list=['dataset/'+args.config_file])
config['epochs'] = args.epoch
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

if config['MODEL_TYPE'].name == 'SEQUENTIAL':
    module_to_import = 'recbole.model.sequential_recommender.'
else:
    module_to_import = 'recbole.model.general_recommender.'

model = getattr(
    importlib.import_module(module_to_import+config['model'].lower()),
    config['model']
    )(config, train_data.dataset).to(config['device'])

# model = get_model(args.model)(config, train_data.dataset).to(config['device'])

logger.info(model)

### 1-0 역전 - 틀릴 문제 추천하기 위해
# trainer loading and initialization
trainer = get_trainer(config['MODEL_TYPE'], config['model'])(config, model)

# model training

best_valid_score, best_valid_result = trainer.fit(
    train_data, valid_data, saved=True, show_progress=config['show_progress']
)

# columns_to_pop = ['item_id_list', 'rating_list', 'timestamp_list']
# columns_to_pop = ['rating_list', 'timestamp_list']

# for col in columns_to_pop:
#     train_data.dataset.inter_feat.interaction.pop(col)
    # valid_data.dataset.inter_feat.interaction.pop(col)
    # test_data.dataset.inter_feat.interaction.pop(col)

# pd.DataFrame.from_dict(train_data.dataset.inter_feat.interaction).to_csv('dataset/train_split.csv', index=None)
# pd.DataFrame.from_dict(valid_data.dataset.inter_feat.interaction).to_csv('dataset/valid_split.csv', index=None)
# pd.DataFrame.from_dict(test_data.dataset.inter_feat.interaction).to_csv('dataset/test_split.csv', index=None)



# model evaluation - train_data에서 나누어진 
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




# configurations initialization
# config = Config(model=args.model, dataset="test_data", config_file_list=['dataset/'+args.config_file])
# config['epochs'] = 1
# config['device'] = 'cuda' if torch.cuda.is_available() else 'cpu'
# init_seed(config['seed'], config['reproducibility'])
# logger initialization
# init_logger(config)

# dataset filtering
# test_dataset = create_dataset(config)
# train2, val2, test2 = data_preparation(config, test_dataset)

# logger.info(test_dataset)


external_user_id = 'e9pNYfHjZjdZnN2Vsq9rMuGFsB02'

# external_user_id = 'FmL23zENfmNrPPZBZcF8JB1RrAq2' # 태엽

# time check
import time
t0 = time.time()

# 이미 푼 문제는 제외
user_solved = dataset.token2id(
    'item_id', 
    df_train.loc[df_train.user_id == external_user_id, 'item_id'].values
)

print('user_solved:', user_solved)

if config['MODEL_TYPE'].name == 'SEQUENTIAL':
    prediction = predict_for_all_item(
                external_user_id, dataset, test_data, model, config, user_solved
            )


    print(
        dataset.id2token(
            dataset.iid_field, prediction.indices.data[0].cpu().numpy()
        ),
        prediction
    )

else: # general recommendation
    # config = Config(model=config['model'], dataset="test_data", config_file_list=['dataset/'+args.config_file])
    # config['epochs'] = 1
    # init_seed(config['seed'], config['reproducibility'])
    # # logger initialization
    # init_logger(config)

    # dataset filtering
    # test_dataset = create_dataset(config)
    # logger.info(test_dataset)
    # 성능 측정
    a_prob = model.full_sort_predict(dataset)
    

    # a_prob = model.predict(test_dataset).tolist()
    # a_true = [val for val in test_dataset.inter_feat["rating"]]
    # a_pred = [round(v) for v in a_prob] 
    # print("Test data prediction")
    # print(f" - Accuracy = {100*accuracy_score(a_true, a_pred):.2f}%")
    # print(f" - ROC-AUC  = {100*roc_auc_score(a_true, a_prob):.2f}%")


print('inference time: ', time.time()-t0)



# train, valid, test_data

# 유저 1명당 800 : 100 : 100    -> 100문제 푼사람은 최근 10개 데이터가 안들어감 
# 최종적으로는 5개 추천인데 +10 해서 15개추천 

# 어차피 회차별로 풀기때문에 같은 유형끼리는 50문제차이


# train과정은 train800, valid100 

# inference : 마지막 100개  

# 그러면 inference 에서는 데이터를 따로 -> train , test 900:100 


# 모델 811(데이터 나누기 -> test_data만 이용), 
# 991(811의 test_data를 넣어 예측) 

# 100-5 : 5 : 5   inference용 