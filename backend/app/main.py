from fastapi import FastAPI, UploadFile, File
from fastapi.param_functions import Depends
from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from typing import List, Union, Optional, Dict, Any

from datetime import datetime
from app.firebase_db import load_database, get_user_solved, get_user_solved_seq, get_dataframe, get_full_problemCode, get_tfidf_dataset
from collections import defaultdict

import requests
import json
import random
from app.model import load_data, tfidf_recommender
from my_inference import inference_main, inference_seq
from starlette.middleware.cors import CORSMiddleware

import os


origins = [
    "*"
]

app = FastAPI(title='Project title',
            description='Description of your project',
            openapi_url='/api/openapi.json')

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


db = load_database()
idx_basic, cos_sim_basic, data_basic, idx_advanced, cos_sim_advanced, data_advanced = load_data()
basic_lst, advanced_lst = get_full_problemCode(db)

@app.get("/")
def hello_world():
    return {"길동국사 backend"}

    
class solved_data(BaseModel):
    rec_lst : list
    # selected_count : int
    
    
class Database(BaseModel):
    isCorrect : bool
    problemCode : str
    selected : int
    solvedAt : str
    testMode : bool
    timetaken : int
    userUID : UUID

class userID(BaseModel):
    userUID : str


@app.get("/db/{user_id}/{level}", description="ex) user_id = userUID, level = full or advanced or basic    full : 난이도 구분 없이 최근 문제 풀이 데이터 100개 가져오기 (문제 풀이 데이터가 100개 이하일 경우 전체 문제풀이 가져오기) ")
async def get_solved(user_id: str,level:str):
    problemCode_dict = get_user_solved(db,user_id,level)
    if not problemCode_dict:
        return {f"{user_id}가 틀린 문제는 없습니다."}
    return problemCode_dict


@app.get("/model/{level}/{userUID}", description="난이도와 유저를 입력하면 추천 리스트를 가져옵니다.")
async def get_model_output(level:str,userUID:str):
    random.seed() # 랜덤시드를 풀어줌으로서 고정되는 문제 해결
    model_lst = ['tfidf', 'ease', 'sasrec']
    model_name = random.sample(model_lst, 1)[0]
    # solved_lst = get_user_solved(db,userUID,False)


    if level == 'basic': 
        solved_lst = get_tfidf_dataset(db, userUID, level)   

        if not solved_lst:
            return {f"{userUID}가 푼 문제는 없습니다."}

        else:
            lst = []
            for problem in solved_lst:
                lst.extend(random.sample(tfidf_recommender(problem, idx_basic, cos_sim_basic, data_basic, idx_advanced, cos_sim_advanced, data_advanced),1))
        
        n = 5 if len(solved_lst)>=5 else len(solved_lst)
        lst = random.sample(lst,n)
        rec_dict = {"tfidf":{}}
        rec_dict["tfidf"]['recommend'] = lst
        rec_dict["tfidf"]['random'] = random.sample(basic_lst,10-len(lst))
        return rec_dict

    else:
        if model_name == "tfidf": 
            solved_lst = get_tfidf_dataset(db, userUID, level)   

            if not solved_lst:
                return {f"{userUID}가 푼 문제는 없습니다."}
            else:
                lst = []
                for problem in solved_lst:
                    lst.extend(random.sample(tfidf_recommender(problem, idx_basic, cos_sim_basic, data_basic, idx_advanced, cos_sim_advanced, data_advanced),1))
            
            n = 5 if len(solved_lst)>=5 else len(solved_lst)
            lst = random.sample(lst,n)
            rec_dict = {"tfidf":{}}
            rec_dict["tfidf"]['recommend'] = lst
            rec_dict["tfidf"]['random'] = random.sample(advanced_lst,10-len(lst))
            return rec_dict
        
        elif model_name == "ease":
            model_path = os.getcwd()+'/saved/EASE-Feb-03-2023_05-57-16.pth'
            user_problem_lst = get_user_solved(db, userUID, level, False)
            
            result = inference_main(userUID, user_problem_lst, model_path)
            
            rec_dict = {model_name:{}}
            rec_dict[model_name]['recommend'] = result
            rec_dict[model_name]['random'] = random.sample(advanced_lst,10-len(result))
            return rec_dict
        
        elif model_name == "sasrec":
            try:
                model_path = os.getcwd()+'/saved/SASRec-Feb-03-2023_09-21-56.pth'
                user_df = get_user_solved_seq(db, userUID, level)

                result = inference_seq(userUID, user_df, model_path)

                rec_dict = {model_name:{}}
                rec_dict[model_name]['recommend'] = result
                rec_dict[model_name]['random'] = random.sample(advanced_lst,10-len(result))
                return rec_dict
            except:
                return {f"{userUID}의 데이터가 충분하지 않습니다. sasrec error."}

    

"""
기본 문제 추천 : tfidf
심화 문제 추천 : tfidf <- 최근에 틀린 문제로 랜덤 샘플
                model <- 최근에 푼 문제 100개를 inference해서 리턴

model 별로 구현하면 되겠다!!
"""





# @app.post("/model", description="해당 유저에 맞는 추천 결과를 가져옵니다.")
# async def get_model_output(data:userID):
#     with open('/opt/ml/한국사작업/모델예축값/모델예축값_2023-01-30 12:43:29.json','r',encoding='utf-8') as f:
#         pred = json.load(f)
#         return pred[data.userUID]



# @app.post("/tfidf", description="유저가 최근 틀린 문제 20개와 유사한 문제를 가져옵니다.")
# async def make_order(data:userID):
#     incorrect_answer_lst = get_user_solved(db,data.userUID)

#     if not incorrect_answer_lst:
#         return {f"{data.userUID}가 틀린 문제는 없습니다."}
#     else:
#         lst = []
#         for problem in incorrect_answer_lst:
#             lst.extend(random.sample(tfidf_recommender(problem, idx, cos_sim, sim_data),1))
        
#         rec_dict = {}
#         if len(lst) < 5:
#             rec_dict['recommend'] = lst
#             rec_dict['random'] = random.sample(problem_lst,10-len(lst))
#         else:
#             rec_dict['recommend'] = random.sample(lst,5)
#             rec_dict['random'] = random.sample(problem_lst,5)

#         return rec_dict