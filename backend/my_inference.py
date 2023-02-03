# run_inference.py 구현 예시

import argparse
import torch
import json
import numpy as np
import pandas as pd
import torch
import os

from app.firebase_db import load_database, get_user_solved

from scipy.sparse import csr_matrix
from datetime import datetime
from collections import defaultdict

from models.ease import EASE
from logging import getLogger

from recbole.data import (
    create_dataset,
    data_preparation, 
    get_dataloader
)
from recbole.utils import (
    init_logger,
    get_model,
    init_seed
)
from recbole.quick_start.quick_start import load_data_and_model

from recbole.config import Config

from utils import predict_for_all_item

def load_data_and_model_ih(model_file):

    checkpoint = torch.load(model_file)
    config = checkpoint["config"]
    # config.final_config_dict['data_path'] = "/opt/ml/dataset/test_data"
    # config.final_config_dict['dataset'] = "test123"
    init_seed(config["seed"], config["reproducibility"])
    init_logger(config)
    logger = getLogger()
    logger.info(config)

    dataset = create_dataset(config)
    logger.info(dataset)
    train_data, valid_data, test_data = data_preparation(config, dataset)

    init_seed(config["seed"], config["reproducibility"])
    model = EASE(config, train_data.dataset).to(config["device"])
    model.load_state_dict(checkpoint["state_dict"])
    model.load_other_parameter(checkpoint.get("other_parameter"))

    return config, model, dataset

def inference_main(userUID, user_problem_lst, model_path):
    # parser = argparse.ArgumentParser()
    # parser.add_argument('--model_path', '-m', type=str, default=model_path, 
    #                     help='name of models')  # '/opt/ml/saved/EASE-Feb-02-2023_06-01-26.pth'
    # args, _ = parser.parse_known_args()
    
    # model 불러오기
    config, model, dataset = load_data_and_model_ih(model_path)

    # device 설정
    device = config.final_config_dict['device']
    
    # user, item id -> token 변환 array
    item_id2token = dataset.field2id_token['item_id']
    token2item_id = dataset.field2token_id['item_id']
    
    user_problem_lst = list(map((lambda x : token2item_id[x]),user_problem_lst))
    user_problem_arr = np.zeros(len(token2item_id))
    for i in user_problem_lst:
        user_problem_arr[i] = 1
        
    model.eval()
    interaction = csr_matrix(user_problem_arr) # 1 X 800 @ 800X800 = 1X800
    r = model.userUID_predict(interaction)
    score = torch.from_numpy(r.flatten())
    
    rating_pred = score.cpu().data.numpy().copy()
    rating_pred[(user_problem_arr>0).reshape(1,-1)] = 0
    ind = np.argpartition(rating_pred, -5)[:, -5:]
    
    arr_ind = rating_pred[np.arange(len(rating_pred))[:, None], ind]

    arr_ind_argsort = np.argsort(arr_ind)[np.arange(len(rating_pred)), ::-1]

    batch_pred_list = list(ind[
        np.arange(len(rating_pred))[:, None], arr_ind_argsort
    ][0])
    batch_pred_list = list(map((lambda x : item_id2token[x]),batch_pred_list))
    return batch_pred_list     

def inference_seq(userUID, user_problem_df, model_path):

    config, model, dataset, _, _, test_data = load_data_and_model(model_path)
    prediction = predict_for_all_item(
                userUID, dataset, test_data, model, config
            )

    batch_pred_list = dataset.id2token(
                        dataset.iid_field, prediction.indices.data[0].cpu().numpy()
                    )
    
    print('prediction:', prediction)
    print('predicted_probs:', batch_pred_list)
                    
    return list(batch_pred_list)


    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    # interaction = {'user_id':torch.tensor([1]).to(device)}
    # score = model.full_sort_predict(interaction)
    # rating_pred = score.cpu().data.numpy().copy()
    # # rating_pred = score.unsqueeze(0).cpu().data.numpy().copy()
    # batch_user_index = interaction['user_id'].cpu().numpy()
    # rating_pred[matrix[batch_user_index].toarray() > 0] = 0
    # ind = np.argpartition(rating_pred, -10)[:, -10:]
    
    # arr_ind = rating_pred[np.arange(len(rating_pred))[:, None], ind]

    # arr_ind_argsort = np.argsort(arr_ind)[np.arange(len(rating_pred)), ::-1]

    # batch_pred_list = ind[
    #     np.arange(len(rating_pred))[:, None], arr_ind_argsort
    # ]
        
    # # 예측값 저장
    # if pred_list is None:
    #     pred_list = batch_pred_list
    #     user_list = batch_user_index
    # else:
    #     pred_list = np.append(pred_list, batch_pred_list, axis=0)
    #     user_list = np.append(user_list, batch_user_index, axis=0)

    # now = datetime.now()
    # result = defaultdict(list)
    # for user, pred in zip(user_list, pred_list):
    #     for item in pred:
    #         result[user_id2token[user]].append(item_id2token[item])

    # with open(f'/opt/ml/한국사작업/모델예축값/test_ease_{now.strftime("%Y-%m-%d %H:%M:%S")}.json','w',encoding="utf-8") as f:
    #     json.dump(result,f,ensure_ascii=False)

    # print('inference done!')
    

    
    
    



