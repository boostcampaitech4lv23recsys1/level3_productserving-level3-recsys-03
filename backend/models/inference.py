import numpy as np
import torch
import pickle

from scipy.sparse import csr_matrix


def inference_main(user_problem_lst, model_path):
    # model 불러오기
    # model = torch.load(model_path)

    with open(model_path,'rb') as f:
        model_dict = pickle.load(f)
    
    user_problem_lst = list(map((lambda x : model_dict['token2id'][x]),user_problem_lst))
    user_problem_arr = np.zeros(len(model_dict['token2id']))

    for i in user_problem_lst:
        user_problem_arr[i] = 1
        
    interaction = csr_matrix(user_problem_arr) 
    r = interaction @ model_dict["B"]
    score = torch.from_numpy(r.flatten())
    
    rating_pred = score.unsqueeze(0).cpu().data.numpy().copy()
    rating_pred[(user_problem_arr>0).reshape(1,-1)] = 0
    ind = np.argpartition(rating_pred, -5)[:, -5:]
    
    arr_ind = rating_pred[np.arange(len(rating_pred))[:, None], ind]
    arr_ind_argsort = np.argsort(arr_ind)[np.arange(len(rating_pred)), ::-1]

    batch_pred_list = list(ind[
        np.arange(len(rating_pred))[:, None], arr_ind_argsort
    ][0])
    batch_pred_list = list(map((lambda x : model_dict['id2token'][x]),batch_pred_list))
    print('good')
    return batch_pred_list   