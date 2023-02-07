import sqlalchemy
import pandas as pd
from sqlalchemy import create_engine
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


## 데이터베이스 연결
def load_database():
    host="ls-9c67b50f3b1170eaac8f789675e5ef3b638eeb6f.cnzorxtg2img.ap-northeast-2.rds.amazonaws.com"
    dbname="gildong-database"
    user="dbmasteruser"
    password="fiveguys!!!"
    port=5432
    db = create_engine(f"postgresql://{user}:{password}@{host}:{port}/{dbname}")
    return db


## log 데이터 불러오기
def get_dataframe(db):
    df = pd.read_sql("select * from log", db)
    return df
    

# 해당 유저가 최근에 푼 문제 n개 리턴 (n개 중 틀린 것만 가져오기 가능 )
def get_user_solved(db, user_id, level, n = 100, full = True):
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



## sequence data 
def get_user_solved_seq(db, user_id, level):
    df = get_dataframe(db)
    df = df.loc[:, ['userUID', 'problemCode', 'isCorrect', 'solvedAt']]
    df['isCorrect'] = df['isCorrect'].apply(int)
    df = df.drop_duplicates(subset=['userUID','problemCode'],
                                keep='last')
    
    sample_df = df[df.userUID == user_id] 

    if level == "advanced": 
        sample_df = sample_df[sample_df.problemCode.apply(lambda x: True if x[0] == 'a' else False)]
    elif level == "basic":
        sample_df = sample_df[sample_df.problemCode.apply(lambda x: True if x[0] == 'b' else False)]
    else:
        pass

    sample_df = sample_df.rename(columns={'userUID':'user_id',
                    'problemCode':'item_id',
                    'isCorrect':'rating',
                    'solvedAt':'timestamp'
                    })
    # 0 - 1 switching
    sample_df['rating'] = sample_df['rating'].apply(lambda x: 0 if x==1 else 1)

    return sample_df


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