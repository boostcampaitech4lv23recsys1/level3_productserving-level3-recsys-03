import os
import random

from fastapi import FastAPI
from app.firebase_db import load_database, pg_load_database, get_user_solved, get_full_problemCode, get_problem_similar
from starlette.middleware.cors import CORSMiddleware
from models.inference import inference_main


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
pg_db = pg_load_database()
basic_lst, advanced_lst = get_full_problemCode(pg_db)


@app.get("/")
def hello_world():
    return {"길동국사 backend"}


@app.get("/db/{user_id}/{level}", description="ex) user_id = userUID, level = full or advanced or basic    full : 난이도 구분 없이 최근 문제 풀이 데이터 100개 가져오기 (문제 풀이 데이터가 100개 이하일 경우 전체 문제풀이 가져오기) ")
async def get_solved(user_id: str,level:str):
    problemCode_dict = get_user_solved(db,user_id,level)
    if not problemCode_dict:
        return {f"{user_id}가 틀린 문제는 없습니다."}
    return problemCode_dict


@app.get("/model/{level}/{userUID}", description="난이도와 유저를 입력하면 추천 리스트를 가져옵니다.")
async def get_model_output(level:str,userUID:str):
    random.seed() # 랜덤시드를 풀어줌으로서 고정되는 문제 해결
    model_lst = ['ease_aug_split','ease_false']
    model_name = random.sample(model_lst, 1)[0]

    if level == 'basic': 
        solved_lst = get_user_solved(db, userUID, level, n = 20, full = False)   

        if not solved_lst:
            return {f"{userUID}가 푼 문제는 없습니다."}

        else:
            lst = []
            for problem in solved_lst:
                lst.extend(random.sample(get_problem_similar(pg_db,problem),1))
        
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
                    lst.extend(random.sample(get_problem_similar(pg_db,problem),1))
            
            n = 5 if len(solved_lst)>=5 else len(solved_lst)
            lst = random.sample(lst,n)
            rec_dict = {"tfidf":{}}
            rec_dict["tfidf"]['recommend'] = lst
            rec_dict["tfidf"]['random'] = random.sample(advanced_lst,10-len(lst))
            return rec_dict
        
        elif model_name == "ease":
            model_path = os.getcwd()+'/saved/EASE-Feb-03-2023_05-57-16.pth'
            user_problem_lst = get_user_solved(db, userUID, level, full = False)
            
            result = inference_main(userUID, user_problem_lst, model_path, model_name)
            random.seed()
            rec_dict = {model_name:{}}
            rec_dict[model_name]['recommend'] = result
            rec_dict[model_name]['random'] = random.sample(advanced_lst,10-len(result))
            return rec_dict
        
        elif model_name == "ease_aug_split":
            model_path = os.getcwd()+'/saved/ease_aug_split.pkl'
            user_problem_lst = get_user_solved(db, userUID, level, full = False)
            
            result = inference_main(user_problem_lst, model_path)
            random.seed()
            rec_dict = {model_name:{}}
            rec_dict[model_name]['recommend'] = result
            rec_dict[model_name]['random'] = random.sample(advanced_lst,10-len(result))
            print(model_name)
            return rec_dict

        elif model_name == 'ease_false':
            model_path = os.getcwd()+'/saved/ease_false.pkl'
            user_problem_lst = get_user_solved(db, userUID, level, full = False)
            
            result = inference_main(user_problem_lst, model_path)
            random.seed()
            rec_dict = {model_name:{}}
            rec_dict[model_name]['recommend'] = result
            rec_dict[model_name]['random'] = random.sample(advanced_lst,10-len(result))
            print(model_name)
            return rec_dict