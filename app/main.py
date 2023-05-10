import uvicorn
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import search_model
import amz_crawling
import amz_modelling
import dnw_crawling
import dnw_modelling
from pathlib import Path
from pydantic import BaseModel
import json

## fastapi 인스턴스 저장
app = FastAPI()

## static 폴더 mounting작업
app.mount("/static",StaticFiles(directory=Path(__file__).parent.parent.absolute() / "static"),name="static")

## 템플릿 구성을 위해 Jinja2 활용
templates = Jinja2Templates(directory="templates")

class row_basemodel(BaseModel):
  selectedData: str

class keyword_basemodel(BaseModel):
  keyword: str

@app.post("/amz_keyword")
async def create_item(keyword_basemodel:keyword_basemodel):
    amz_crawl_list = search_model.search_amz_keyword(keyword_basemodel.keyword)
    return amz_crawl_list

@app.post("/dnw_keyword")
async def create_item(keyword_basemodel:keyword_basemodel):
    dnw_crawl_list = search_model.search_dnw_keyword(keyword_basemodel.keyword)
    return dnw_crawl_list

@app.post("/amz_crawl")
async def create_item(row_basemodel: row_basemodel):
    row_list = json.loads(row_basemodel.selectedData)
    for row in row_list:
        print(row['url'])
        amz_crawling.crawling().crawl_amz(row['url'])
        amz_modelling.modelling().model_amz(row['url'])
    return "아마존 크롤링 완료"

@app.post("/dnw_crawl")
async def create_item(row_basemodel: row_basemodel):
    row_list = json.loads(row_basemodel.selectedData)
    for row in row_list:
        print(row['pcategory'])
        dnw_crawling.crawling().crawl_dnw(row['pcategory'])
        dnw_modelling.modelling().model_dnw(row['pcategory'])
    return "다나와 크롤링 완료"

## 메인페이지
@app.get("/")
async def root(request:Request):
    amz_crawl_list = search_model.search_amz_crawl_list()
    dnw_crawl_list = search_model.search_dnw_crawl_list()
    return templates.TemplateResponse("index.html", {"request":request, "amz_crawl_list":amz_crawl_list, "dnw_crawl_list":dnw_crawl_list})

# @app.get("/amz_keyword")
# async def amz_keyword(request:Request, keyword:str):
#     return templates.TemplateResponse("model4_amz.html", {"request":request, "keyword":keyword})

@app.get('/model4_amz')
async def model4_amz(request:Request, url:str):
    amz_list = search_model.model4().search_amz(url)
    return templates.TemplateResponse("model4_amz.html", {"request":request, "input_list":amz_list})

@app.get('/model4_dnw')
async def model4_dnw(request:Request, pcategory:str):
    dnw_list = search_model.model4().search_dnw(pcategory)
    return templates.TemplateResponse("model4_dnw.html", {"request":request, "input_list":dnw_list})

@app.get('/model4_amz_data')
async def model4_amz_data(request:Request, url:str, cluster:str):
    amz_data_list = search_model.model4().search_amz_data(url,cluster)
    return templates.TemplateResponse('model4_amz_data.html', {"request":request, "input_list":amz_data_list})

@app.get('/model4_dnw_data')
def model4_dnw_data(request:Request, pcategory:str, cluster:str):
    dnw_data_list = search_model.model4().search_dnw_data(pcategory,cluster)
    return templates.TemplateResponse('model4_dnw_data.html', {"request":request, "input_list":dnw_data_list})

uvicorn.run(app, host = '127.0.0.1', port = 8000)