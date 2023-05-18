import config

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
from datetime import datetime
import pymysql
import time
import os
import re

mydb = pymysql.connect(host=config.DATABASE_CONFIG['host'],
                       user=config.DATABASE_CONFIG['user'],
                       password=config.DATABASE_CONFIG['password'],
                       database=config.DATABASE_CONFIG['dbname'],
                       cursorclass=pymysql.cursors.DictCursor)
# 커서 생성
cursor = mydb.cursor()

def checkDictValue_str(dict,key):
    value = dict.get(key)
    if value == None:
        return ""
    else:
        return str(dict[key]).replace("\\","|").replace("'","`").replace('"',"`").replace("‎","")

def checkDictValue_int(dict,key):
    value = dict.get(key)
    if value == None:
        return 0
    else:
        return dict[key]

def insert_db(url,asin,product_order,product_info,product_detail,product_feature,feature_rating,review_keyword,body_content):
    cursor.execute(f"select * from amz_category where url like '{url}'")
    rows = cursor.fetchall()
    level_list = list()
    for row in rows:
        level_list.append(row[1])
        level_list.append(row[2])
        level_list.append(row[3])
        level_list.append(row[4])
    
    create_date = str(datetime.now()).split(' ')[0].strip()
    
    index_1 = 1
    for key in product_detail:
        product_detail_dict = dict()
        product_detail_dict["product_key"] = asin
        product_detail_dict["product_idx"] = index_1
        product_detail_dict["create_date"] = create_date
        product_detail_dict["title"] = key
        product_detail_dict["content"] = product_detail[key]
        # print(product_detail)
        cursor.execute(f"""INSERT INTO `amz_product_detail` (url,product_key,product_idx,create_date,detail_table_key,detail_table_value) VALUES("{url}","{checkDictValue_str(product_detail,"ASIN")}","{checkDictValue_str(product_detail_dict,"product_idx")}","{create_date}","{key}","{checkDictValue_str(product_detail,key)}")""")
        mydb.commit()
        index_1 += 1

    index_2 = 1
    for key in feature_rating:
        feature_rating_dict = dict()
        feature_rating_dict["product_key"] = asin
        feature_rating_dict["product_idx"] = index_2
        feature_rating_dict["create_date"] = create_date
        feature_rating_dict["title"] = key
        feature_rating_dict["rating"] = feature_rating[key]
        # print(feature_rating_dict)
        cursor.execute(f"""INSERT INTO `amz_feature_rating` (url,product_key,product_idx,create_date,feature_title,feature_rating) VALUES("{url}","{checkDictValue_str(product_detail,"ASIN")}",{checkDictValue_int(feature_rating_dict,"product_idx")},"{create_date}","{checkDictValue_str(feature_rating_dict,"title")}","{checkDictValue_int(feature_rating_dict,"rating")}")""")
        mydb.commit()
        index_2 += 1

    index_3 = 1
    for key in product_feature:
        product_feature_dict = dict()
        product_feature_dict["product_key"] = asin
        product_feature_dict["product_idx"] = index_3
        product_feature_dict["create_date"] = create_date
        product_feature_dict["content"] = product_feature[key]
        # print(product_feature_dict)
        cursor.execute(f"""INSERT INTO `amz_product_feature` (url,product_key,product_idx,create_date,feature_list_content) VALUES("{url}","{checkDictValue_str(product_detail,"ASIN")}",{checkDictValue_int(product_feature_dict,"product_idx")},"{create_date}","{checkDictValue_str(product_feature_dict,"content")}")""")
        mydb.commit()
        index_3 += 1


    product_info_dict = dict()
    product_info_dict = product_info
    product_info_dict["product_key"] = asin
    product_info_dict["product_order"] =product_order
    product_info_dict["create_date"] = create_date
    # print(product_info_dict)
    cursor.execute(f"""INSERT INTO `amz_product_info` (url,product_key,product_idx,create_date,level1,level2,level3,level4,product_name,product_price,review_score,review_number,5star,4star,3star,2star,1star) VALUES("{url}","{checkDictValue_str(product_detail,"ASIN")}","{checkDictValue_str(product_info_dict,"product_order")}","{create_date}","{level_list[0]}","{level_list[1]}","{level_list[2]}","{level_list[3]}","{checkDictValue_str(product_info_dict,"Product_name")}",{checkDictValue_int(product_info_dict,"Product_price")},{checkDictValue_int(product_info_dict,"totalRatingStar")},{checkDictValue_int(product_info_dict,"totalReviewCount")},{checkDictValue_int(product_info_dict,"star5")},{checkDictValue_int(product_info_dict,"star4")},{checkDictValue_int(product_info_dict,"star3")},{checkDictValue_int(product_info_dict,"star2")},{checkDictValue_int(product_info_dict,"star1")})""")
    mydb.commit()

    index_4 = 1
    for key in review_keyword:
        review_keyword_dict = dict()
        review_keyword_dict["product_key"] = asin
        review_keyword_dict["product_idx"] = index_4
        review_keyword_dict["create_date"] = create_date
        review_keyword_dict["content"] = review_keyword[key]
        # print(review_keyword_dict)
        cursor.execute(f"""INSERT INTO `amz_review_keyword` (url,product_key,product_idx,create_date,keyword) VALUES("{url}","{checkDictValue_str(product_detail,"ASIN")}",{checkDictValue_int(review_keyword_dict,"product_idx")},"{create_date}","{checkDictValue_str(review_keyword,key)}")""")
        mydb.commit()
        index_4 += 1

    body_content_dict = dict()
    body_content_dict["product_key"] = asin
    body_content_dict["content"] = body_content
    body_content_dict["create_date"] = create_date
    # print(body_content_dict["content"])
    cursor.execute(f"""INSERT INTO `amz_body_content` (url,product_key,create_date,body_content) VALUES("{url}","{checkDictValue_str(product_detail,"ASIN")}","{create_date}","{checkDictValue_str(body_content_dict,"content")}")""")
    mydb.commit()
    
# 폴더 생성 함수
def createFolder(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

# RatingStar
def getRatingStar(product_info, soup):
    ratingStar_html = soup.select_one("span[data-hook='rating-out-of-text']")
    ratingStar = ratingStar_html.get_text().split(' ')[0].strip()
    product_info["totalRatingStar"] = float(ratingStar)

# ReviewCount
def getReviewCount(product_info, soup):
    totalReviewCount_html = soup.select_one("div[data-hook='total-review-count'] span")
    totalReviewCount_str = totalReviewCount_html.get_text().strip()
    totalReviewCount_number = re.sub(r'[^0-9]', '', totalReviewCount_str)
    product_info["totalReviewCount"] = int(totalReviewCount_number)

# EachStarPercent
def getEachStarPercent(product_info, soup):
    eachStarPercent_list = list()
    eachStarPercent_html = soup.select("table#histogramTable tbody tr td.a-text-right span.a-size-base a")
    for eachStarPercent_str in eachStarPercent_html:
        eachStarPercent_list.append(eachStarPercent_str.get_text().strip())
    star_index = 5
    for eachStarPercent_str in eachStarPercent_list:
        eachStarPercent_number = re.sub(r'[^0-9]', '', eachStarPercent_str)
        product_info[f'star{star_index}']= int(eachStarPercent_number)
        star_index -= 1

# "Product Description" / "From the manufacturer"
def getDescription_text(soup):
    global body_content
    try:
        description_text = soup.select("div.aplus-v2.desktop.celwidget div.celwidget.aplus-module")
        for list_index in description_text:
            body_content.append(list_index.get_text().strip().replace("  ","").replace("\n",""))
    except:
        pass
    try:
        description_text_2 = soup.select_one("div#productDescription")
        body_content.append(description_text_2.get_text().strip().replace("  ","").replace("\n",""))
    except:
        pass

    body_content = list(filter(None, body_content))

# Category
def getCategory(product_info, soup):
    index = 1
    categories_str = soup.select("a.a-color-tertiary")
    for category in categories_str:
        product_info[f'Level_{index}'] = category.get_text().strip().replace("'","`")
        index += 1

#  Name & Price
def getNameAndPrice(product_info, soup):
    productName_str = soup.select_one("span#productTitle").get_text().strip().replace("'","`")
    product_info["Product_name"] = productName_str
    try:
        productPrice = soup.select_one("span.a-offscreen").get_text().strip().lstrip("$")
        product_info["Product_price"] = float(productPrice)
    except:
        product_info["Product_price"] = "null"

# Featurebullets
def getFeaturebullets(product_feature, soup):
    featurePage = soup.select_one("div#feature-bullets ul.a-unordered-list.a-vertical")
    featurePage_elements = featurePage.select("li > span")
    index = 1
    for feature in featurePage_elements:
        product_feature[f'Feature_{index}'] = feature.get_text().strip().replace("'","`")
        index += 1

# AttrRatingStar
def getAttrRatingStar(feature_rating, soup):
    attrRatingTable = soup.select_one("div#cr-dp-summarization-attributes").find_all("div",{"data-hook":"cr-summarization-attribute"})
    for attrRatingList in attrRatingTable:
        attrRatingTitle = attrRatingList.select_one("span.a-size-base.a-color-base").get_text().strip().replace("'","`")
        attrRatingScore = attrRatingList.select_one("span.a-size-base.a-color-tertiary").get_text().strip()
        feature_rating[attrRatingTitle] = float(attrRatingScore)

# ReviewKeyword
def getReviewKeyword(review_keyword, soup):
    reviewKeywords = soup.select_one("div#cr-lighthut-1-")
    reviewKeyword_html = reviewKeywords.select("span.cr-lighthouse-term")
    index = 1
    for reviewKeyword_str in reviewKeyword_html:
        reviewKeyword = reviewKeyword_str.get_text().strip()
        review_keyword[f"ReviewKeyword_{index}"] = reviewKeyword
        index += 1

# DetailList  
def getDetailList(product_detail, soup):
    detailListSource = soup.select("div#detailBullets_feature_div span.a-list-item span")
    detailTableDict_key_list = list()
    detailTableDict_value_list = list()
    for spanList in detailListSource:
        if detailListSource.index(spanList) % 2 == 0:
            detailTableDict_key_list.append(spanList.get_text().replace("  ","").replace("\n","").replace(":","").replace("‏","").replace("‎","").strip())
        else:
            detailTableDict_value_list.append(spanList.get_text().replace("  ","").replace("\n","").strip())
    for key, value in zip(detailTableDict_key_list, detailTableDict_value_list):
        product_detail[key]=value

# DetailTable
def getDetailTable(product_detail, soup):
    detailTableSource = soup.select("div.a-row.a-spacing-top-base div.a-column.a-span6 table tbody tr")
    for index in detailTableSource:
        title = index.select_one("th").get_text().strip().replace("'","`")
        description = index.select_one("td").get_text().replace("  ","").replace("\n","").strip().replace("'","`")
        product_detail[title] = description
  
# def goToReviewPage(reviewDict, soup):
#     # 페이지 도달 (Selenium)
#     reviewpage = soup.select_one("div#reviews-medley-footer a")["href"]
#     driver.get(URL_ADDRESS+reviewpage)
#     time.sleep(2)
    
#     # BeautifulSoup
#     pageSource = driver.page_source
#     soup = BeautifulSoup(pageSource, 'html.parser')

#     # ReviewText
#     reviewer_list = soup.select("div#cm_cr-review_list div.a-section.review.aok-relative div.a-row.a-spacing-none div.a-section.celwidget")
    
#     index = 1
#     for reviewer in reviewer_list:
#         Rating = reviewer.select_one("span.a-icon-alt").get_text().split(' ')[0].strip()
#         Date = reviewer.select_one("span.a-size-base.a-color-secondary.review-date").get_text().strip('Reviewed in the United States on').strip()
#         Text = reviewer.select_one("span.review-text.review-text-content span").get_text().strip()
#         Rating_number = re.sub(r'[^0-9]', '', Rating)
#         reviewDict[f"Rating_{index}"] = float(Rating_number)
#         reviewDict[f"Date_{index}"] = Date
#         try:
#             Helpful = reviewer.select_one("span.cr-vote span.a-size-base.a-color-tertiary.cr-vote-text").get_text().strip('people found this helpful').strip()
#             Helpful_number = re.sub(r'[^0-9]', '', Helpful)
#             reviewDict[f"Helpful_{index}"] = int(Helpful_number)
#         except:
#             pass
#         reviewDict[f"Text_{index}"] = Text
#         index += 1

# 상품 정보페이지로 넘어가는 함수
def goToDetailPage(driver, product_detail, product_feature, product_info, reviewDict, feature_rating,review_keyword,body_content,url,asin,product_order):
    # 사이트 스크롤해서 html 불러오기
    for i in [10,5,10/3,10/4,2,10/6,10/7,10/8,10/9,1]: # 페이지 10등분
        driver.execute_script(f"window.scrollTo(0,document.body.scrollHeight/{i})")
        time.sleep(1)

    # BeautifulSoup
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    try:
        # Category
        getCategory(product_info, soup)
    except:
        # print(1)
        pass
    try:
        # Name & Price
        getNameAndPrice(product_info, soup)
    except:
        # print(2)
        pass  
    try:
        # DetailTable
        getDetailList(product_detail, soup)
    except:
        # print(3)
        pass
    try:
        # DetailTableSource
        getDetailTable(product_detail, soup)
    except:
        # print(4)
        pass
    try:
        # Featurebullets
        getFeaturebullets(product_feature, soup)
    except:
        # print(5)
        pass
    try:
        # AttrRatingStar
        getAttrRatingStar(feature_rating, soup)
    except:
        # print(6)
        pass
    try:
        # ReviewKeyword
        getReviewKeyword(review_keyword, soup)
    except:
        # print(7)
        pass
    try:
        # RatingStar
        getRatingStar(product_info, soup)
    except:
        # print(8)
        pass
    try:
        # ReviewCount
        getReviewCount(product_info, soup)
    except:
        # print(9)
        pass
    try:    
        # EachStarPercent
        getEachStarPercent(product_info, soup)
    except:
        # print(10)
        pass
    try:
        # "Product Description" / "From the manufacturer"
        getDescription_text(soup)
    except:
        # print(11)
        pass

    insert_db(url,asin,product_order,product_info,product_detail,product_feature,feature_rating,review_keyword,body_content)

class crawling:
    def __init__(self):
        pass
    def crawl_amz(self,url):
        options = Options()
        driver = webdriver.Firefox(options=options,executable_path=".\geckodriver.exe")

        # ziasin_code (Selenium)
        URL_ADDRESS = "https://www.amazon.com/"
        driver.get(URL_ADDRESS)
        time.sleep(1)
        driver.find_element("id","nav-global-location-popover-link").click()
        time.sleep(1)

        driver.find_element("id","GLUXZipUpdateInput").send_keys("98101")
        driver.find_element("id","GLUXZipUpdate").click()
        time.sleep(1)

        error_list = list()
        asin_list = list()
        product_order = 1
        
        URL_SUFFIX = url.split("https://www.amazon.com/")[1]
        # amazon서버 불러오기
        driver.get(URL_ADDRESS + URL_SUFFIX)
        while(True):
            # 사이트 스크롤해서 html 불러오기
            for i in [10,5,10/3,10/4,2,10/6,10/7,10/7,10/8,10/8]:
                driver.execute_script(f"window.scrollTo(0,document.body.scrollHeight/{i})")
                time.sleep(0.5)
            # Selenium && BeautifulSoup
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')

            # 상품을 지정하는 div를 list형식으로 저장
            contents = soup.select("div.zg-grid-general-faceout")

            # 상품의 URL_suffix와 상품의 고유 key값을 dict로 묶어서 list로 저장
            content_URLkey_list = list()
            for index in contents:
                content_URLkey_dict = dict()
                asin_list.append(index.select_one("div.p13n-sc-uncoverable-faceout").attrs["id"].strip())
                
            # 다음페이지로 넘기는 함수
            nextPageURL = soup.select_one("li.a-last a")
            if nextPageURL != None:
                URL = URL_ADDRESS + str(nextPageURL.attrs["href"].strip())
                driver.get(URL)
            else:
                print("[COMPLETE]")
                break

        for asin in asin_list:
            URL_SUFFIX = "/dp/"+ asin
            # amazon서버 불러오기
            driver.get(URL_ADDRESS + URL_SUFFIX)
            
            product_detail = dict()
            product_feature =dict()
            product_info = dict()
            reviewDict = dict()
            feature_rating = dict()
            review_keyword = dict()
            body_content = list()
            try:
                goToDetailPage(driver, product_detail, product_feature, product_info, reviewDict,feature_rating,review_keyword,body_content,url,asin,product_order)
                product_order += 1
            except:
                error_list.append(url)
        print(error_list)
        driver.close()