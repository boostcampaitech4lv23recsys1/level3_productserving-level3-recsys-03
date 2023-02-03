from fastapi import FastAPI
from app.firebase_db import load_database, get_dataframe

from logging import getLogger
import os

from recbole.config import Config
from recbole.data import create_dataset, data_preparation
from recbole.utils import init_logger
from recbole.quick_start.quick_start import load_data_and_model

from utils import predict_for_all_item  # model import 하는 함수
 
import time
t0 = time.time()

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

df_dd = df_sel.drop_duplicates(subset=['user_id', 'item_id'],
                                keep='last')


# train, test 나누기
df_eval = df_dd.drop_duplicates(subset=['user_id'], keep='last')

df_train = df_dd.copy()   

MODEL_PATH = 'SASRec-Feb-02-2023_18-25-34.pth'

config, model, _, _, _, _ = load_data_and_model(
    'saved/'+MODEL_PATH
)


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


# logger = getLogger()
config = Config(model=config['model'], dataset='train_data', config_file_list=['dataset/seq_data.yaml'])
# config['epochs'] = args.epoch
# config['show_progress'] = False 
# config['device'] = 'cuda' if torch.cuda.is_available() else 'cpu'

    
# init_seed(config['seed'], config['reproducibility'])

# # logger init
# init_logger(config)

# logger.info(config)

# dataset filtering
dataset = create_dataset(config)

# logger.info(dataset)

# dataset splitting
train_data, valid_data, test_data = data_preparation(config, dataset)


# # model loading and init
# init_seed(config['seed'], config['reproducibility'])


external_user_id = 'e9pNYfHjZjdZnN2Vsq9rMuGFsB02'

# external_user_id = 'FmL23zENfmNrPPZBZcF8JB1RrAq2' # 태엽

# time check


# 이미 푼 문제는 제외
user_solved = dataset.token2id(
    'item_id', 
    df_train.loc[df_train.user_id == external_user_id, 'item_id'].values
)

# print('user_solved:', user_solved)

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