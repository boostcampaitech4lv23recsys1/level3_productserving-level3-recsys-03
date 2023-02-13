import numpy as np
import torch

from logging import getLogger
from recbole.data.interaction import Interaction
from recbole.data import (
    create_dataset,
    data_preparation
)
from recbole.utils import (
    init_logger,
    init_seed
)

def get_model(inp_model):

    '''
    이용하고자 하는 모델 패키지 정보 추가
    '''

    if inp_model == 'LightGCN':
        from recbole.model.general_recommender.lightgcn import LightGCN
        model = LightGCN

    if inp_model == 'SLIMElastic':
        from recbole.model.general_recommender.slimelastic import SLIMElastic
        model = SLIMElastic

    if inp_model == 'SASRec':
        from recbole.model.sequential_recommender.sasrec import SASRec
        model = SASRec

    if inp_model == 'BERT4Rec':
        from recbole.model.sequential_recommender.bert4rec import BERT4Rec
        model = BERT4Rec

    if inp_model == 'GRU4Rec':
        from recbole.model.sequential_recommender.gru4rec import GRU4Rec
        model = GRU4Rec

    if inp_model == 'DeepFM':
        from recbole.model.context_aware_recommender.deepfm import DeepFM
        model = DeepFM
        
    if inp_model == 'EASE':
        from models.ease import EASE
        model = EASE

    return model


def load_data_and_model_ih(model_file,inp_model):

    checkpoint = torch.load(model_file)
    config = checkpoint["config"]
    init_seed(config["seed"], config["reproducibility"])
    init_logger(config)
    logger = getLogger()
    logger.info(config)

    dataset = create_dataset(config)
    logger.info(dataset)
    train_data, valid_data, test_data = data_preparation(config, dataset)

    init_seed(config["seed"], config["reproducibility"])

    inp_model = get_model(inp_model)
    model = inp_model(config, train_data.dataset).to(config["device"])
    model.load_state_dict(checkpoint["state_dict"])
    model.load_other_parameter(checkpoint.get("other_parameter"))

    return config, model, dataset


# ref : https://www.kaggle.com/code/astrung/recbole-using-all-items-for-prediction/notebook
def add_last_item(old_interaction, last_item_id, max_len=50):
    new_seq_items = old_interaction['item_id_list'][-1]
    if old_interaction['item_length'][-1].item() < max_len:
        new_seq_items[old_interaction['item_length'][-1].item()] = last_item_id
    else:
        new_seq_items = torch.roll(new_seq_items, -1)
        new_seq_items[-1] = last_item_id

    # new_seq_items_ext = 
    return new_seq_items.view(1, len(new_seq_items))

def predict_for_all_item(external_user_id, dataset, test_data, model, config):
    model.eval()
    with torch.no_grad():
        uid_series = dataset.token2id(dataset.uid_field, [external_user_id])
        index = np.isin(dataset[dataset.uid_field].numpy(), uid_series)
        input_interaction = dataset[index]
        test = {
            'item_id_list': add_last_item(input_interaction, 
                                          input_interaction['item_id'][-1].item(), model.max_seq_length),
            'item_length': torch.tensor(
                [input_interaction['item_length'][-1].item() + 1
                 if input_interaction['item_length'][-1].item() < model.max_seq_length else model.max_seq_length])
        }
        new_inter = Interaction(test)
        new_inter = new_inter.to(config['device'])
        new_scores = model.full_sort_predict(new_inter)
        new_scores = new_scores.view(-1, test_data.dataset.item_num)
        # new_scores[:, 0] = -np.inf  # set scores of [pad] to -inf
        
        # 이미 푼 문제는 제외
        user_solved = test_data.dataset.inter_feat.item_id.cpu().numpy()
        for idx in user_solved: 
            new_scores[0, idx] = -np.inf

    return torch.topk(new_scores, 5)