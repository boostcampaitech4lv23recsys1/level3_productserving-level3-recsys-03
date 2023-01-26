from fastapi import FastAPI, UploadFile, File
from fastapi.param_functions import Depends
from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from typing import List, Union, Optional, Dict, Any

from datetime import datetime
from app.firebase_db import load_database, get_user_solved, get_dataframe

import requests
from app.model import load_data, tfidf_recommender

app = FastAPI()
db = load_database()
df = get_dataframe(db)


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



@app.get("/db/{user_id}", description="유저가 최근에 틀린 5문제를 가져옵니다")
async def get_solved(user_id: str):
    problemCode_dict = get_user_solved(db,user_id)
    if not problemCode_dict:
        return {f"{user_id}가 틀린 문제는 없습니다."}
    return problemCode_dict


@app.get('/df', description="유저 아이디를 리스트로 가져옵니다.")
async def get_user_lst():
    return list(df.userUID.unique())


@app.post("/db", description="문제 추천 결과를 가져옵니다.")
async def make_order(data:solved_data):
    idx, cos_sim, sim_data = load_data()
    lst = tfidf_recommender(data.rec_lst[0], idx, cos_sim, sim_data)
    return lst

