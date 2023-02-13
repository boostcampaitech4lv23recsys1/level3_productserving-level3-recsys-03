import pandas as pd
import sys
sys.path.append('/opt/ml/level3_productserving-level3-recsys-03/backend')

from tqdm import tqdm
from app.firebase_db import get_problem_similar


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

def preprocess(df, db):

    user_idx = df['userUID'].unique()
    
    # data augementaion
    print("start augmentation")

    for user in tqdm(user_idx):
        tmp = df[df['userUID'] == user]
        solved_idx = tmp['problemCode'].unique()
        for solved in solved_idx:
            rec_list = get_problem_similar(db, solved)[:2]  # Top-2개 복제
            for i in rec_list:
                if i in solved_idx:
                    continue
                df = pd.concat([df,duplicate_data(solved, tmp, i) ])
    print("Done!")

    return df

def df_split(df):
    df = df.reset_index(drop=True)
    df = df.sort_values(['userUID','solvedAt'],ascending=False)

    df_split = pd.DataFrame()
    q = 0
    for u in df.userUID.unique():
        sample_df = df[df.userUID == u].reset_index(drop=True)

        n = sample_df.shape[0]
        for i in range(int(n/100)+1):
            q += 1
            s = "split_user_"+str(q)
            a = sample_df.loc[100*i:100*(i+1),:]
            a.loc[:,'userUID'] = s
            df_split = pd.concat([df_split,a]) 

    return df_split

