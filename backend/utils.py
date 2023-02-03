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
        from recbole.model.general_recommender.ease import EASE
        model = EASE


    return model