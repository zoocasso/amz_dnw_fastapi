import config

from operator import itemgetter
import pandas as pd
import pymysql

mydb = pymysql.connect(host=config.DATABASE_CONFIG['host'],
                       user=config.DATABASE_CONFIG['user'],
                       password=config.DATABASE_CONFIG['password'],
                       database=config.DATABASE_CONFIG['dbname'],
                       cursorclass=pymysql.cursors.DictCursor)
cursor = mydb.cursor()

### table을 dataframe으로 바꾸는 함수
def get_db_table_pcategory(tablename,pcategory):
    cursor.execute(f"""select * from {tablename} where pcategory = '{pcategory}' and create_date = (select max(create_date) from {tablename} where pcategory = '{pcategory}' group by pcategory)""")
    tb = cursor.fetchall()
    return tb
    
def dnw_product_info_dataframe(pcategory):
    dnw_product_info_tb = get_db_table_pcategory("dnw_product_info",pcategory)
    dnw_product_info_df = pd.DataFrame(dnw_product_info_tb,columns =["idx","pcategory","pcode","product_idx","create_date","level1","level2","level3","level4","level5","product_name","product_price","launch_date","brand_name","review_score","review_number","5star","4star","3star","2star","1star"])
    dnw_product_info_df = dnw_product_info_df.loc[:,["pcategory","product_idx","pcode","level1","level2","level3","level4","product_name","product_price"]]
    return dnw_product_info_df

def dnw_product_detail_dataframe(pcategory):
    dnw_product_detail_tb = get_db_table_pcategory("dnw_product_detail",pcategory)
    dnw_product_detail_df = pd.DataFrame(dnw_product_detail_tb,columns =["idx","pcategory","pcode","product_idx","create_date","title","content"])
    dnw_product_detail_df = dnw_product_detail_df.loc[:,["pcode","create_date","title","content"]]
    return dnw_product_detail_df

def dnw_review_keyword_dataframe(pcategory):
    dnw_review_keyword_tb = get_db_table_pcategory("dnw_review_keyword",pcategory)
    dnw_review_keyword_df = pd.DataFrame(dnw_review_keyword_tb,columns =["idx","pcategory","pcode","product_idx","create_date","keyword"])
    dnw_review_keyword_df = dnw_review_keyword_df.loc[:,["pcode","create_date","keyword"]]
    return dnw_review_keyword_df

class maketable:
    pcategory = ""
    def __init__(self, pcategory):
        self.pcategory = pcategory
    def quality_title(self,cluster_quality):

        #품질특성
        product_detail = cluster_quality.to_dict('record')
        # print(product_detail)
        
        #품질특성 타이틀만 추출
        quality_title_list = list()
        for i in range(len(product_detail)):
            try:
                quality_title_list.append(product_detail[i]["title"])
            except:
                pass
        # for i in quality_title_list:
        #     print(i)

        #품질특성 title 필터링 (불용어 처리)
        except_list = ["제조회사","제품분류","등록년월","적합성평가인증","안전확인인증","가능성인증","형태",None]
        quality_title_list = [i for i in quality_title_list if i not in except_list]
        # print(quality_title_list)

        #품질특성 타이틀별 counting을 dict로 만들기 (title, counting)
        quality_title_counting_list = list()
        for i in list(set(quality_title_list)):
            quality_title_counting_dict = dict()
            quality_title_counting_dict["title"] = i
            quality_title_counting_dict["counting"] = quality_title_list.count(i)
            quality_title_counting_list.append(quality_title_counting_dict)
        # for i in quality_title_counting_list:
        #     print(i)

        #품짍특성 타이틀 정렬
        quality_title_counting = sorted(quality_title_counting_list, key=itemgetter('counting'), reverse=True)
        # for i in quality_title_counting:
        #     print(i)

        # 품질특성 타이틀 counting 정렬 중 상위 5개 추출
        quality_title_top_7 = list()
        if len(quality_title_counting) < 7:
            max_quality_title = len(quality_title_counting)
        else:
            max_quality_title = 7
        for i in range(max_quality_title):
            quality_title_top_7.append(quality_title_counting[i]['title'])
        return quality_title_top_7

    def quality_content(self,quality_title_top_7,cluster_quality):

        #품질특성
        product_detail = cluster_quality.to_dict('record')
        # print(product_detail)

        #품질특성 타이틀과 내용 추출
        quality_title_and_content_list = list()
        for i in quality_title_top_7:
            for j in range(len(product_detail)):
                if product_detail[j]["title"] == i:
                    quality_title_and_content_dict = dict()
                    quality_title_and_content_dict["pcode"] = product_detail[j]["pcode"]
                    quality_title_and_content_dict["title"] = product_detail[j]["title"]
                    quality_title_and_content_dict["content"] = product_detail[j]["content"]
                    quality_title_and_content_list.append(quality_title_and_content_dict)
        return quality_title_and_content_list


    def needs_title(self,cluster_range,cluster_needs):
        cluster_needs_title_list = list()

        #요구특성
        cluster_review_keyword = cluster_needs
        
        for index in range(cluster_range):
            review_keyword = cluster_review_keyword.groupby('cluster').get_group(index)
            review_keyword = review_keyword.to_dict('records')
            # print(review_keyword)
            #요구품질 타이틀만 추출
            needs_title_list = list()
            for i in range(len(review_keyword)):
                try:
                    needs_title_list.append(review_keyword[i]["keyword"])
                except:
                    pass
            # for i in needs_title_list:
            #     print(i)

            # 요구품질 title 필터링 (불용어 처리)
            except_list = [None]
            needs_title_list = [i for i in needs_title_list if i not in except_list]
            # print(needs_title_list)

            #요구품질 타이틀별 counting을 dict로 만들기 (keyword, counting)
            needs_title_counting_list = list()
            for i in list(set(needs_title_list)):
                needs_title_counting_dict = dict()
                needs_title_counting_dict["title"] = i
                needs_title_counting_dict["counting"] = needs_title_list.count(i)
                needs_title_counting_list.append(needs_title_counting_dict)
            # for i in needs_title_counting_list:
            #     print(i)
            
            #요구품질 타이틀 정렬
            needs_title_counting_list = [i for i in needs_title_counting_list if i['title'] != None and pd.isnull(i['title'])==False]
            needs_title_counting = sorted(needs_title_counting_list, key=itemgetter('counting'), reverse=True)
            # for i in needs_title_counting:
            #     print(i)

            # 품질특성 타이틀 counting 정렬 중 상위 15개 추출
            needs_title_top_15 = list()
            if len(needs_title_counting)<15:
                max_quality_title = len(needs_title_counting)
            else:
                max_quality_title= 15
            for i in range(max_quality_title):
                needs_title_top_15.append(needs_title_counting[i]['title'])
            # print(needs_title_top_15)
            cluster_needs_title_dict = dict()
            cluster_needs_title_dict["cluster"] = index
            cluster_needs_title_dict["needs_title_list"] = needs_title_top_15
            cluster_needs_title_list.append(cluster_needs_title_dict)
        return cluster_needs_title_list