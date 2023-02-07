from fastapi import FastAPI, UploadFile, File
from fastapi.param_functions import Depends
from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from typing import List, Union, Optional, Dict, Any

from datetime import datetime
from app.firebase_db import load_database, get_user_solved, get_user_solved_seq, get_dataframe, get_full_problemCode, get_problem_similar
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
basic_lst, advanced_lst = get_full_problemCode(db)

@app.get("/")
def hello_world():
    return {"길동국사 backend"}

    
class solved_data(BaseModel):
    rec_lst : list
    # selected_count : int
    

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
    model_lst = ['tfidf','EASE','SASRec']
    model_name = random.sample(model_lst, 1)[0]

    if level == 'basic': 
        solved_lst = get_user_solved(db, userUID, level, n = 20, full = False)   

        if not solved_lst:
            return {f"{userUID}가 푼 문제는 없습니다."}

        else:
            lst = []
            for problem in solved_lst:
                lst.extend(random.sample(get_problem_similar(db,problem),1))
        
        n = 5 if len(solved_lst)>=5 else len(solved_lst)
        lst = random.sample(lst,n)
        rec_dict = {"tfidf":{}}
        rec_dict["tfidf"]['recommend'] = lst
        rec_dict["tfidf"]['random'] = random.sample(basic_lst,10-len(lst))
        return rec_dict

    else:
        if model_name == "tfidf": 
            solved_lst = get_user_solved(db, userUID, level, n = 20, full = False)   

            if not solved_lst:
                return {f"{userUID}가 푼 문제는 없습니다."}
            else:
                lst = []
                for problem in solved_lst:
                    lst.extend(random.sample(get_problem_similar(db,problem),1))
            
            n = 5 if len(solved_lst)>=5 else len(solved_lst)
            lst = random.sample(lst,n)
            rec_dict = {"tfidf":{}}
            rec_dict["tfidf"]['recommend'] = lst
            rec_dict["tfidf"]['random'] = random.sample(advanced_lst,10-len(lst))
            return rec_dict
        
        elif model_name == "EASE":
            model_path = os.getcwd()+'/saved/EASE-Feb-03-2023_05-57-16.pth'
            user_problem_lst = get_user_solved(db, userUID, level, full = False)
            
            result = inference_main(userUID, user_problem_lst, model_path, model_name)
            random.seed()
            rec_dict = {model_name:{}}
            rec_dict[model_name]['recommend'] = result
            rec_dict[model_name]['random'] = random.sample(advanced_lst,10-len(result))
            return rec_dict
        
        elif model_name == "SASRec":
            try:
                model_path = os.getcwd()+'/saved/SASRec-Feb-03-2023_09-21-56.pth'
                user_df = get_user_solved_seq(db, userUID, level)

                result = inference_seq(userUID, user_df, model_path)
                random.seed()
                rec_dict = {model_name:{}}
                rec_dict[model_name]['recommend'] = result
                rec_dict[model_name]['random'] = random.sample(advanced_lst,10-len(result))
                return rec_dict
            except:
                return {f"{userUID}의 데이터가 충분하지 않습니다. sasrec error."}

   
