import pandas as pd
# Import TfIdfVectorizer from scikit-learn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

from tqdm import tqdm
import time
from ..app.firebase_db import load_database, get_user_solved, get_user_solved_seq, get_dataframe, get_full_problemCode, get_problem_similar


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

    db = load_database()
    df = get_dataframe(db)
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



if __name__ == "__main__":
    main()