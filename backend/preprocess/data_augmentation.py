import pandas as pd
# Import TfIdfVectorizer from scikit-learn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

from tqdm import tqdm
import time


def to_adv(df):
    for idx, row in df.iterrows():
        i = row['assessmentItemID']
        if '_' in i[-2:]:
            i = i[:-2] + i[-1:].zfill(2)
            # i[-1:]
            # i = i.replace(i[-2:], i[-1:].zfill(2))
            # print(i)
        i = i.replace('_' , "")
        i = i.replace('deep', 'advanced')
        df.loc[idx, 'assessmentItemID'] = i

    return df


def to_basic(df):
    for idx, row in df.iterrows():
        i = row['assessmentItemID']
        if '_' in i[-2:]:
            i = i[:-2] + i[-1:].zfill(2)
            # i[-1:]
            # i = i.replace(i[-2:], i[-1:].zfill(2))
            # print(i)
        i = i.replace('_' , "")
        df.loc[idx, 'assessmentItemID'] = i

    return df

def get_idx(df):
    idx = pd.Series(df.index, index=df['assessmentItemID']).drop_duplicates() # 문제 인덱스
    return idx


def cal_sim(df):
    tfidf = TfidfVectorizer() #Tfidf 벡터화
    tfidf_matrix = tfidf.fit_transform(df['keyword'])
    cos_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
    
    return cos_sim

def tfidf_recommender(id, df, top_n : int):
    assessmentID_idx = get_idx(df)[id]
    sim_score = list(enumerate(cal_sim(df)[assessmentID_idx]))
    sim_score = sorted(sim_score, key=lambda x: x[1], reverse = True)
    sim_score = sim_score[1:(top_n + 1)] # 자기 제외하고 유사도 높은 순으로 Top-10 추천
    res_idx = [i[0]  for i in sim_score]
    tmp = pd.DataFrame(df['assessmentItemID'].iloc[res_idx])
    tmp = tmp['assessmentItemID'].values.tolist()
    return tmp

def duplicate_data(idx, df, rec):
    tmp1 = df[df['problemCode']==idx].reset_index(drop=True)
    dup = pd.DataFrame({
        'solvedAt' : tmp1['solvedAt'][0],
        'testMode' : tmp1['testMode'][0],
        'timetaken' : tmp1['timetaken'][0],
        'selected' : tmp1['selected'][0],
        'problemCode' : rec,
        'userUID' : tmp1['userUID'][0],
        'isCorrect' : tmp1['isCorrect'][0]
    }, index = [0])
    return dup

def main():
    basic = pd.read_csv('./data/data_basic.csv')
    deep = pd.read_csv('./data/data_deep.csv')

    basic = to_basic(basic)
    deep = to_adv(deep)

    user_idx = df['userUID'].unique()
    
    # data augementaion

    print("start preprocessing")
    for user in tqdm(user_idx):
        tmp = df[df['userUID'] == user]
        solved_idx = tmp['problemCode'].unique()
        for solved in solved_idx:
            if 'basic' in solved:
                rec_list = tfidf_recommender(solved, basic, 2)
                for i in rec_list:
                    if i in solved_idx:
                        continue
                    df = pd.concat([df,duplicate_data(solved, tmp, i) ])

            else:
                rec_list = tfidf_recommender(solved, deep, 2)
                for i in rec_list:
                    if i in solved_idx:
                        continue
                    df = pd.concat([df,duplicate_data(solved, tmp, i) ])



if __name__ == "__main__":
    main()