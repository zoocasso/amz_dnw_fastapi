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
app.mount("/static",StaticFiles(directory=Path(__file__).parent.parent.absolute() / "static"),name="static",)

## 템플릿 구성을 위해 Jinja2 활용
templates = Jinja2Templates(directory="templates")


class Item(BaseModel):
  selectedData: str

@app.post("/amz_crawl")
async def create_item(item: Item):
    row_list = json.loads(item.selectedData)
    print(item)
    for i in row_list:
        print(i['url'])
        
    for row in row_list:
        amz_crawling.crawling().crawl_amz(row['url'])
        amz_modelling.modelling().model_amz(row['url'])
    return "아마존 크롤링 완료"

@app.post("/dnw_crawl")
async def create_item(item: Item):
    row_list = json.loads(item.selectedData)

    for i in row_list:
        print(i['url'])

    for row in row_list:
        dnw_crawling.crawling().crawl_dnw(row['url'])
        dnw_modelling.modelling().model_dnw(row['url'])
    return "다나와 크롤링 완료"

## 메인페이지
@app.get("/")
async def root(request:Request):
    amz_crawl_list = search_model.search_amz_crawl_list()
    dnw_crawl_list = search_model.search_dnw_crawl_list()
    return templates.TemplateResponse("index.html", {"request":request, "amz_list":amz_crawl_list, "dnw_list":dnw_crawl_list})

@app.get('/amz_crawl_list')
async def amz_crawl_list(request:Request):
    amz_crawl_list = search_model.search_amz_crawl_list()
    return templates.TemplateResponse("amz_crawl_list.html", {"request":request, "inputList":amz_crawl_list})

@app.get('/dnw_crawl_list')
async def dnw_crawl_list(request:Request):
    dnw_crawl_list = search_model.search_dnw_crawl_list()
    return templates.TemplateResponse("dnw_crawl_list.html", {"request":request, "inputList":dnw_crawl_list})

@app.get("/search")
async def search(request:Request):
    return templates.TemplateResponse("searching.html", {"request":request})

@app.get('/search_model4_amz')
async def search_amz(request:Request, url:str):
    amz_list = search_model.model4().search_amz(url)
    return templates.TemplateResponse("search_model4_amz.html", {"request":request, "inputList":amz_list})

@app.get('/search_model4_dnw')
async def search_dnw(request:Request, pcategory:str):
    dnw_list = search_model.model4().search_dnw(pcategory)
    return templates.TemplateResponse("search_model4_dnw.html", {"request":request, "inputList":dnw_list})

@app.get('/search_model4_data_amz')
async def search_model4_data_amz(request:Request, url:str, cluster:str):
    amz_data_list = search_model.model4().search_amz_data(url,cluster)
    return templates.TemplateResponse('search_model4_data_amz.html', {"request":request, "inputList":amz_data_list})

@app.get('/search_model4_data_dnw')
def search_model4_data_dnw(request:Request, pcategory:str, cluster:str):
    dnw_data_list = search_model.model4().search_dnw_data(pcategory,cluster)
    return templates.TemplateResponse('search_model4_data_dnw.html', {"request":request, "inputList":dnw_data_list})

@app.get("/crawling")
async def crawling(request:Request):
    return templates.TemplateResponse("crawling.html", {"request":request})

@app.get("/crawl_amz")
async def crawl_amz(request:Request, url:str):
    amz_crawling.crawling().crawl_amz(url)
    amz_modelling.modelling().model_amz(url)
    return templates.TemplateResponse("home.html", {"request":request})

@app.get("/crawl_dnw")
async def crawl_dnw(request:Request, pcategory:str):
    dnw_crawling.crawling().crawl_dnw(pcategory)
    dnw_modelling.modelling().model_dnw(pcategory)
    return templates.TemplateResponse("home.html", {"request":request})

uvicorn.run(app, host = '127.0.0.1', port = 8001)