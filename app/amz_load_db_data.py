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
def get_db_table_url(tablename,url):
    cursor.execute(f"""select * from {tablename} where url = '{url}' and create_date = (select max(create_date) from {tablename} where url = '{url}' group by url)""")
    tb = cursor.fetchall()
    return tb

def amz_product_info_dataframe(url):
    amz_product_info_tb = get_db_table_url("TB_AMZ_PRODUCT_INFO",url)
    amz_product_info_df = pd.DataFrame(amz_product_info_tb,columns =["idx","url","product_key",'product_idx',"create_date","product_name","product_price","review_score","review_number","5star","4star","3star","2star","1star"])
    amz_product_info_df = amz_product_info_df.loc[:,['url',"product_key",'product_idx',"create_date","product_name","product_price"]]
    return amz_product_info_df

def amz_feature_rating_dataframe(url):
    dnw_product_detail_tb = get_db_table_url("TB_AMZ_FEATURE_RATING",url)
    dnw_product_detail_df = pd.DataFrame(dnw_product_detail_tb,columns =["idx","url","product_key","product_idx","create_date","feature_title","feature_rating"])
    dnw_product_detail_df = dnw_product_detail_df.loc[:,["product_key","product_idx","create_date","feature_title","feature_rating"]]
    return dnw_product_detail_df


class maketable:
    url = ""
    def __init__(self, url):
        self.url = url
    def quality_title(self,cluster_quality):

        #품질특성
        product_detail = cluster_quality.to_dict('records')
        # print(product_detail)
        
        #품질특성 타이틀만 추출
        quality_title_list = list()
        for i in range(len(product_detail)):
            try:
                quality_title_list.append(product_detail[i]["feature_title"])
            except:
                pass
        # for i in quality_title_list:
        #     print(i)

        #품질특성 feature_title 필터링 (불용어 처리)
        except_list = [None]
        quality_title_list = [i for i in quality_title_list if i != None and pd.isnull(i)==False]
        # print(quality_title_list)

        #품질특성 타이틀별 counting을 dict로 만들기 (feature_title, counting)
        quality_title_counting_list = list()
        for i in list(set(quality_title_list)):
            quality_title_counting_dict = dict()
            quality_title_counting_dict["feature_title"] = i
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
            quality_title_top_7.append(quality_title_counting[i]['feature_title'])
        return quality_title_top_7

    def quality_content(self,quality_title_top_7,cluster_quality):

        #품질특성
        product_detail = cluster_quality.to_dict('records')
        # print(product_detail)

        #품질특성 타이틀과 내용 추출
        quality_title_and_content_list = list()
        for i in quality_title_top_7:
            for j in range(len(product_detail)):
                if product_detail[j]["feature_title"] == i:
                    quality_title_and_content_dict = dict()
                    quality_title_and_content_dict["product_key"] = product_detail[j]["product_key"]
                    quality_title_and_content_dict["feature_title"] = product_detail[j]["feature_title"]
                    quality_title_and_content_dict["feature_rating"] = product_detail[j]["feature_rating"]
                    quality_title_and_content_list.append(quality_title_and_content_dict)
        
        return quality_title_and_content_list