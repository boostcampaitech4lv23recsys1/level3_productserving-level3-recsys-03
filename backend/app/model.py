import pandas as pd
# Import TfIdfVectorizer from scikit-learn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

def load_data():
    data = pd.read_csv('./data_basic.csv')

    tfidf = TfidfVectorizer() #Tfidf 벡터화
    tfidf_matrix = tfidf.fit_transform(data['keyword']) # 해설내용  sparse - matrix 생성
    tfidf_matrix.shape

    cos_sim = linear_kernel(tfidf_matrix, tfidf_matrix) # cos 유사도 구하기
    idx = pd.Series(data.index, index=data['assessmentItemID']).drop_duplicates() # 문제 인덱스
    return idx, cos_sim, data

def tfidf_recommender(id, idx, cos_sim, data):
    assessmentID_idx = idx[id]
    sim_score = list(enumerate(cos_sim[assessmentID_idx]))
    sim_score = sorted(sim_score, key=lambda x: x[1], reverse = True)
    sim_score = sim_score[1:11] # 자기 제외하고 유사도 높은 순으로 Top-10 추천
    res_idx = [i[0]  for i in sim_score]

    return list(data['assessmentItemID'].iloc[res_idx])


