import pandas as pd
import os
from sqlalchemy import create_engine
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


def load_database():
    KEY_PATH = os.getcwd()+'/key/'
    private_ket = KEY_PATH + os.listdir(KEY_PATH)[0]
    cred = credentials.Certificate(private_ket)
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    return db

## 데이터베이스 연결
def pg_load_database():
    host = "****"
    dbname = "****"
    user = "****"
    password = "****"
    port=5432
    db = create_engine(f"postgresql://{user}:{password}@{host}:{port}/{dbname}")
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

## log 데이터 불러오기
def pg_get_dataframe(db):
    df = pd.read_sql("select * from log", db)
    return df


# firebase 버전 - 해당 유저가 최근에 푼 문제 100개 리턴 
def get_user_solved(db, user_id, level, n=100, full = True):
    df = get_dataframe(db)
    df = df.sort_values(['userUID','solvedAt'])
    df = df.drop_duplicates(subset=['userUID','problemCode'],
                                keep='last')
    sample_df = df[df.userUID == user_id] # 해당 유저가 최근에 푼 문제 

    if level == "advanced": 
        sample_df = sample_df[sample_df.problemCode.apply(lambda x: True if x[0] == 'a' else False)]
    elif level == "basic":
        sample_df = sample_df[sample_df.problemCode.apply(lambda x: True if x[0] == 'b' else False)]
    else:
        pass

    if len(sample_df) >= n:
        sample_df = sample_df.iloc[-n:,:]

    if not full:
        sample_df = sample_df[sample_df.isCorrect == False]
    
    return list(sample_df.problemCode.values)

# postgresql db 버전 - 해당 유저가 최근에 푼 문제 n개 리턴 (n개 중 틀린 것만 가져오기 가능 )
def pg_get_user_solved(db, user_id, level, n = 100, full = True):
    if level == 'advanced':
        sub_q = "AND LEFT(\"problemCode\",1) = \'a\'"
    elif level == 'basic':
        sub_q = "AND LEFT(\"problemCode\",1) = \'b\'"
    else:
        sub_q = ""

    if not full:
        sub_q += "AND \"isCorrect\" = false"

    q = f'''SELECT t2."problemCode"
            FROM (
                SELECT *
                FROM (
                    SELECT ROW_NUMBER() OVER (PARTITION BY "userUID","problemCode" ORDER BY "solvedAt" DESC) as idx,* 
                    FROM log WHERE "userUID" = \'{user_id}\' {sub_q} 
                    ORDER BY "solvedAt" DESC
                ) as t1
                WHERE t1.idx = 1
                LIMIT {n}
            ) as t2
            ORDER BY t2."solvedAt"
    '''
    df =pd.read_sql(q,db)
    return list(df.problemCode.values)


# 전체 문제 리스트 가져오기
def get_full_problemCode(db):
    advanced_q = '''SELECT "problemCode" 
        FROM problems
        WHERE LEFT(\"problemCode\",1) = \'a\'
        '''
    basic_q = '''SELECT "problemCode" 
        FROM problems
        WHERE LEFT(\"problemCode\",1) = \'b\'
        '''
    return list(pd.read_sql(basic_q,db).problemCode.values), list(pd.read_sql(advanced_q,db).problemCode.values)


# 유사 문제 5개 가져오기
def get_problem_similar(db,problemCode):
    q = f"select * from problems where \"problemCode\" = \'{problemCode}\'"
    return pd.read_sql(q,db).similar[0]



