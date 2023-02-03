import pandas as pd
import requests
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

def load_database():

    private_ket = '/opt/ml/backend/key/gildong-k-history-firebase-adminsdk-i7q1c-f7652da7b0.json'
    cred = credentials.Certificate(private_ket)
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    return db

def get_dataframe(db):
    users_ref = db.collection(u'logs').document(u'solved')
    users_ref2 = db.collection(u'logs2').document(u'solved')
    # docs = users_ref.stream()
    lst = users_ref.get().to_dict()['solved']
    lst2 = users_ref2.get().to_dict()['solved']
    df = pd.DataFrame(lst) #유저 로그 정보가 담긴 데이터프레임
    df2 = pd.DataFrame(lst2)
    df = pd.concat([df,df2]).reset_index(drop=True)
    return df
    

# 해당 유저가 최근에 푼 문제 100개 리턴 
def get_user_solved(db, user_id, level, full = True):
    df = get_dataframe(db)
    df = df.drop_duplicates(subset=['userUID','problemCode'],
                                keep='last')
    sample_df = df[df.userUID == user_id] # 해당 유저가 최근에 푼 문제

    if level == "advanced": 
        sample_df = sample_df[sample_df.problemCode.apply(lambda x: True if x[0] == 'a' else False)]
    elif level == "basic":
        sample_df = sample_df[sample_df.problemCode.apply(lambda x: True if x[0] == 'b' else False)]
    else:
        pass
    
    if not full:
        sample_df = sample_df[sample_df.isCorrect == False]

    # 해당 유저가 최근 푼 문제 100개 리턴 
    # 100개 미만이면 푼 만큼 리턴 
    if len(sample_df) < 100:
        return list(sample_df.problemCode.values)
        # return {'problemCode' : list(sample_df.problemCode.values), "isCorrect" : list(sample_df.isCorrect.values)}  # df에서 dict로 바꾸어줌 
    else: 
        return list(sample_df.problemCode[-100:].values)
        # return {'problemCode' : list(sample_df.problemCode[-100:].values), "isCorrect" : list(sample_df.isCorrect[-100:].values)}


# def get_user_advanced_solved(db, user_id, iscorrect = True):
#     df = get_advanced_dataset(db)

#     if iscorrect:
#         sample_df = df[df.userUID == user_id] # 해당 유저가 최근에 푼 문제 전체
#         # 해당 유저가 최근 푼 문제 100개 리턴 
#         # 100개 미만이면 푼 만큼 리턴 
#         if len(sample_df) < 20:
#             return list(sample_df.problemCode.values)   
#         else: 
#             return list(sample_df.problemCode[-20:].values)

#     else:
#         sample_df = df[(df.userUID == user_id)&(df.isCorrect == False)] # 해당 유저가 최근에 틀린 문제제

#         # 해당 유저가 최근 푼 문제 100개 리턴 
#         # 100개 미만이면 푼 만큼 리턴 
#         if len(sample_df) < 100:
#             return list(sample_df.problemCode.values)   
#         else: 
#             return list(sample_df.problemCode[-100:].values)


# 심화 문제 풀이 데이터를 가져옵니다.
def get_tfidf_dataset(db, user_id, level):
    df = get_dataframe(db)
    df = df.drop_duplicates(subset=['userUID','problemCode'],
                                keep='last')
    sample_df = df[(df.userUID == user_id)&(df.isCorrect == False)] # 해당 유저가 최근에 틀린 문제
    if level == "advanced": 
        sample_df = sample_df[sample_df.problemCode.apply(lambda x: True if x[0] == 'a' else False)]
    else:
        sample_df = sample_df[sample_df.problemCode.apply(lambda x: True if x[0] == 'b' else False)]

    # 해당 유저가 최근 틀린 문제 20개 리턴 
    # 20개 미만이면 틀린 만큼 리턴 
    if len(sample_df) < 20:
        return list(sample_df.problemCode.values)   
    else: 
        return list(sample_df.problemCode[-20:].values)


def get_model_dataset(db, user_id, level):
    df = get_dataframe(db)
    df = df.drop_duplicates(subset=['userUID','problemCode'],
                                keep='last')
    df = df[df.problemCode.apply(lambda x: True if x[0] == 'a' else False)]
    return df


def get_full_problemCode(db):
    users_ref = db.collection(u'problems')
    docs = users_ref.stream()
    advanced_lst = []
    basic_lst = []
    for i in docs:
        if i.id != "기본4701":
            if i.id[0] == 'a':
                advanced_lst.append(i.id)
            else:
                basic_lst.append(i.id) 
    return basic_lst, advanced_lst