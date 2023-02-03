import pandas as pd
# Import TfIdfVectorizer from scikit-learn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel


def load_data():
    data_advanced = pd.read_csv('/opt/ml/한국사작업/scrap_deep/data_advanced.csv')
    data_basic = pd.read_csv('/opt/ml/한국사작업/scrap_basic/data_basic.csv')
    tfidf_advanced = TfidfVectorizer() #Tfidf 벡터화
    tfidf_basic = TfidfVectorizer()
    tfidf_matrix_advanced = tfidf_advanced.fit_transform(data_advanced['keyword']) # 해설내용  sparse - matrix 생성
    tfidf_matrix_basic = tfidf_basic.fit_transform(data_basic['keyword'])

    cos_sim_advanced = linear_kernel(tfidf_matrix_advanced, tfidf_matrix_advanced) # cos 유사도 구하기
    idx_advanced = pd.Series(data_advanced.index, index=data_advanced['assessmentItemID']).drop_duplicates() # 문제 인덱스

    cos_sim_basic = linear_kernel(tfidf_matrix_basic, tfidf_matrix_basic) # cos 유사도 구하기
    idx_basic = pd.Series(data_basic.index, index=data_basic['assessmentItemID']).drop_duplicates() # 문제 인덱스    
    return idx_basic, cos_sim_basic, data_basic, idx_advanced, cos_sim_advanced, data_advanced


def tfidf_recommender(id, idx_basic, cos_sim_basic, data_basic, idx_advanced, cos_sim_advanced, data_advanced):
    if id[0] == "a":
        assessmentID_idx = idx_advanced[id]
        sim_score = list(enumerate(cos_sim_advanced[assessmentID_idx]))
        sim_score = sorted(sim_score, key=lambda x: x[1], reverse = True)
        sim_score = sim_score[1:6] # 자기 제외하고 유사도 높은 순으로 Top-10 추천
        res_idx = [i[0]  for i in sim_score]
        return list(data_advanced['assessmentItemID'].iloc[res_idx])

    else:
        assessmentID_idx = idx_basic[id]
        sim_score = list(enumerate(cos_sim_basic[assessmentID_idx]))
        sim_score = sorted(sim_score, key=lambda x: x[1], reverse = True)
        sim_score = sim_score[1:6] # 자기 제외하고 유사도 높은 순으로 Top-10 추천
        res_idx = [i[0]  for i in sim_score]
        return list(data_basic['assessmentItemID'].iloc[res_idx])


