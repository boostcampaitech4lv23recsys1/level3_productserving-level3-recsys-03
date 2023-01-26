import pandas as pd
import requests
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

def load_database():

    private_ket = './key/gildong-k-history-firebase-adminsdk-i7q1c-f7652da7b0.json'
    cred = credentials.Certificate(private_ket)
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    return db

def get_dataframe(db):
    users_ref = db.collection(u'logs').document(u'solved')
    # docs = users_ref.stream()
    lst = users_ref.get().to_dict()['solved']
    df = pd.DataFrame(lst) #유저 로그 정보가 담긴 데이터프레임
    return df
    

# 해당 유저가 최근에 틀린 문제 5개 리턴 
def get_user_solved(db,user_id):
    users_ref = db.collection(u'logs').document(u'solved')
    # docs = users_ref.stream()
    lst = users_ref.get().to_dict()['solved']
    
    df = pd.DataFrame(lst) #유저 로그 정보가 담긴 데이터프레임
    sample_df = df[(df.userUID == user_id)&(df.isCorrect == False)] # 해당 유저가 틀린 문제

    # 해당 유저가 최근에 틀린 문제 5개 리턴 
    if len(sample_df) < 5:
        return sample_df[['problemCode']].to_dict('list')  # df에서 dict로 바꾸어줌 
    else: 
        return sample_df[-5:][['problemCode']].to_dict('list')

