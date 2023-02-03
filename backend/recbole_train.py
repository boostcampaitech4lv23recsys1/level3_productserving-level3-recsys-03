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
import argparse

from utils import get_model  # model import 하는 함수
 

### Parse Arguments
parser = argparse.ArgumentParser()

# MODEL = 'LightGCN'
# MODEL = 'SLIMElastic'
# MODEL = 'SASRec'
# MODEL = 'BERT4Rec'
# MODEL = 'GRU4Rec'
parser.add_argument("--model", default="EASE", type=str)
parser.add_argument("--neg_sample", default=False, type=bool)
args = parser.parse_args()


db = load_database()
df = get_dataframe(db)


df_sel = df.loc[:, ['userUID', 'problemCode', 'isCorrect', 'solvedAt']]

df_sel = df_sel.rename(columns={'userUID':'user_id',
                'problemCode':'item_id',
                'isCorrect':'rating',
                'solvedAt':'timestamp'
                })

# 5명 제외
# fiveguys = [
#     'EZKg2x3FgvRNiQfgK0iNy1iz54k2',
#     'Bq56PPLqLXQLGijMt7QLH9p3hyU2',  # 태엽 아이디중 테스트용
#     'rFW8tuibA9cYaOummBR5nS5ucI53',
#     'bR5SdsiXAlUoPmZAnWldnfhLJs92',
#     'LH8ERBe1DpXavxtNNxKE0KIPyio2'
# ]
# df_sel = df_sel.set_index('user_id').drop(fiveguys).reset_index()


# 0 - 1 switching
df_sel['rating'] = df_sel['rating'].apply(lambda x: 0 if x else 1)



# 다섯문제 이상 푼 유저만 남김
df_dd = df_sel.drop_duplicates(subset=['user_id', 'item_id'],
                                keep='last')
df_dd = df_dd[df_dd.item_id.apply(lambda x: True if x[0] == 'a' else False)]
df_train = df_dd[df_dd.user_id.map((df_dd.user_id.value_counts()>=5).to_dict())]


print('전체 데이터 수:', len(df_train))
print('train 데이터 수:', len(df_train))

# neg_sampling set to none using sequential modeling  
yamldata = """
USER_ID_FIELD: user_id
ITEM_ID_FIELD: item_id
RATING_FIELD: rating
TIME_FIELD: timestamp

load_col:
    inter: [user_id, item_id, rating, timestamp]

eval_args:                      
  split: {'LS':'valid_and_test'}   
  group_by: user                
  order: RO                     
  mode: full
eval_batch_size: 1 
neg_sampling: ~
user_inter_num_interval: "[0,inf)"
item_inter_num_interval: "[0,inf)"
val_interval:
    rating: "[0,1]"
    timestamp: "[1672892980000, inf)"
    
hidden_act: 'gelu'              # (str) The activation function in feed-forward layer.
loss_type: 'BPR'                 # (str) The type of loss function. Range in ['BPR', 'CE'].
"""

# if not args.neg_sample:
#     yamldata += 'neg_sampling: ~'
    


## train data 생성
outpath = f"dataset/train_data"
outfile = f"dataset/train_data/train_data.inter"
yamlfile = f"train_data.yaml"

os.makedirs(outpath, exist_ok=True)

print("Processing Start")
inter_table = []
for user, item, acode, tstamp in zip(df_train.user_id, df_train.item_id, df_train.rating, df_train.timestamp):
    inter_table.append( [user, item, max(acode,0), tstamp] )

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
config = Config(model=args.model, dataset='train_data', config_file_list=[f'train_data.yaml'])
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

model = get_model(args.model)(config, train_data.dataset).to(config['device'])
a =model.full_sort_predict({'user_id':torch.tensor([1]).to(config['device'])})

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

b =model.full_sort_predict({'user_id':torch.tensor([1]).to(config['device'])})
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
