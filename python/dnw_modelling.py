import dnw_load_db_data
from dnw_load_db_data import maketable
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler
from sqlalchemy import create_engine
from collections import Counter
import re

Separator = "$$"
separator = " ~ "

# dataframe에서 db로 저장
db_address = 'mysql+pymysql://root:vision9551@172.30.1.51/kisti_crawl'
db_conn = create_engine(db_address)
conn = db_conn.connect()
price_range_list = list()

# dunn index
def delta(ck, cl):
    values = np.ones([len(ck), len(cl)])*10000
    
    for i in range(0, len(ck)):
        for j in range(0, len(cl)):
            values[i, j] = np.linalg.norm(ck[i]-cl[j])
            
    return np.min(values)
    
def big_delta(ci):
    values = np.zeros([len(ci), len(ci)])
    
    for i in range(0, len(ci)):
        for j in range(0, len(ci)):
            values[i, j] = np.linalg.norm(ci[i]-ci[j])
            
    return np.max(values)
    
def dunn(k_list):
    """ Dunn index [CVI]
    
    Parameters
    ----------
    k_list : list of np.arrays
        A list containing a numpy array for each cluster |c| = number of clusters
        c[K] is np.array([N, p]) (N : number of samples in cluster K, p : sample dimension)
    """
    deltas = np.ones([len(k_list), len(k_list)])*1000000
    big_deltas = np.zeros([len(k_list), 1])
    l_range = list(range(0, len(k_list)))
    
    for k in l_range:
        for l in (l_range[0:k]+l_range[k+1:]):
            deltas[k, l] = delta(k_list[k], k_list[l])
        
        big_deltas[k] = big_delta(k_list[k])

    di = np.min(deltas)/np.max(big_deltas)
    return di

def make_cluster_table(df):
    df = df[:70]

    # 2차원(가격X가격) 설정 및 데이터정규화
    price = pd.DataFrame(df,columns = ['product_price', 'product_price'])

    scaler = MinMaxScaler()
    data_scale = scaler.fit_transform(price)

    # dunn index 계산(최대 가격 클러스터 수를 5로 설정)
    dunn_list = []
    for i in range(2, 6) :
        clus = []
        np.random.seed(100)
        kmeans = KMeans(n_clusters = i)
        y_pred = kmeans.fit_predict(data_scale)
        price['labels'] = kmeans.labels_
        
        for j in range(i) :
            clus.append(price[price['labels'] == j].values)
        dunn_list.append(dunn(clus))

    k = np.argmax(dunn_list) + 1
    # print(f'최적 클러스터 수 : {k}개')

     # K-means 클러스터링
    model = KMeans(n_clusters=k, random_state=10)
    model.fit(data_scale)
    df['cluster'] = model.fit_predict(data_scale)

    # 가격 범위
    for j in range(k):
        cluster_price = df.loc[df['cluster'] == j, 'product_price']
        price_range_list.append(f"{min(cluster_price)};{max(cluster_price)}")    
    return df

def quality_table(cluster_product_info_merge_brand_name, pcategory,cluster_quality):
    # dnw_cluster_dataframe
    cluster_product_info = cluster_product_info_merge_brand_name
    # print(cluster_product_info)
    
    # quality title list를 가져오는 부분
    quality_title_pcategory = maketable(pcategory)
    quality_title_list = quality_title_pcategory.quality_title(cluster_quality)
    # print(quality_title_list)

    # quality title과 content를 dict로 가져오는 부분
    content_list = quality_title_pcategory.quality_content(quality_title_list,cluster_quality)
    # print(content_list)

    # quality title마다 dataframe을 만들어서 cluster_product_info에 merge하는 부분
    quality_index = 1
    for quality_title in quality_title_list:
        # print(quality_title)
        quality_title_content_list = list()
        for content in content_list:
            # print(quality_title)
            if quality_title == content["title"]:
                quality_title_content_list.append(content)
        quality_df = pd.DataFrame(quality_title_content_list)
        quality_df.rename(columns = {'title':f'title_{quality_index}','content':f'content_{quality_index}'},inplace=True)
        quality_index += 1
        # print(quality_df)

        cluster_product_info = pd.merge(left = cluster_product_info , right = quality_df, how = "left", on = "pcode")
        # print(cluster_product_info)
    return cluster_product_info

def needs_table(cluster_product_info_merge_brand_name,pcategory,cluster_needs):
    # dnw_cluster_dataframe
    cluster_product_info = cluster_product_info_merge_brand_name
    # print(cluster_product_info)

    #cluster의 수
    cluster_range = len(cluster_product_info.drop_duplicates(['cluster']))
    # print(cluster_range)

    # needs title list를 가져오는 부분
    needs_title_pcategory = maketable(pcategory)
    needs_title_list = needs_title_pcategory.needs_title(cluster_range,cluster_needs)
    # print(needs_title_list)

    # 내부 list 형식을 join을 통해 text로 변경한뒤 다시 저장하는 부분 (df 형식에 맞게 정제작업)
    needs_title_list_2 = list()
    for i in range(cluster_range):
        needs_title_dict = dict()
        needs_title_dict['cluster'] = needs_title_list[i]['cluster']
        needs_title_dict['needs_title_list'] = f"{Separator}".join(needs_title_list[i]['needs_title_list'])
        needs_title_list_2.append(needs_title_dict)
    # print(needs_title_list_2)

    needs_df = pd.DataFrame(needs_title_list_2)
    cluster_product_info = pd.merge(left = cluster_product_info , right = needs_df, how = "left", on = "cluster")
    return cluster_product_info


except_list =list()


class modelling:
    def __init__(self):
        pass
    
    def model_dnw(self, pcategory):
        print("hi")
        try:
            #product_info db불러오기 (df형태)
            product_info = dnw_load_db_data.dnw_product_info_dataframe(pcategory)

            #cluster계산하여 저장 (df형태)
            cluster_product_info = make_cluster_table(product_info)
            # print(cluster_product_info)

            #cluster별 price_range 계산하여 df로 저장하기
            cluster_price_range_list = list()
            for i in range(len(price_range_list)):
                cluster_price_range_dict = dict()
                cluster_price_range_dict['cluster'] = i
                cluster_price_range_dict['price_range'] = price_range_list[i]
                cluster_price_range_list.append(cluster_price_range_dict)
            cluster_price_range_df = pd.DataFrame(cluster_price_range_list)
            # print(cluster_price_range_df)


            product_detail = dnw_load_db_data.dnw_product_detail_dataframe(pcategory)
            product_detail_dict = product_detail.to_dict('record')
            brand_list = list()
            for i in product_detail_dict:
                if i["title"] == '제조회사':
                    brand_dict = dict()
                    brand_dict['pcode'] = i['pcode']
                    brand_dict['brand_name'] = i['content']
                    brand_list.append(brand_dict)
            brand_df = pd.DataFrame(brand_list)
            # print(brand_df)

            # # #cluster_product_info와 price_range의 merge 저장
            cluster_product_info = pd.merge(left = cluster_product_info , right = cluster_price_range_df, how = "left", on = "cluster")
            cluster_product_info_merge_brand_name = pd.merge(left = cluster_product_info , right = brand_df, how = "left", on = "pcode")
            # cluster_product_info_merge_brand_name.to_sql(name='dnw_cluster_tb',con=db_conn,if_exists='append',index=False)

            # #품질특성 merge하여 저장
            product_detail = dnw_load_db_data.dnw_product_detail_dataframe(pcategory)
            cluster_quality = pd.merge(left = cluster_product_info_merge_brand_name , right = product_detail, how = "left", on = "pcode")
            # cluster_quality.to_sql(name='dnw_cluster_quality_tb',con=db_conn,if_exists='append',index_label="idx",index=False)

            # #요구품질 merge하여 저장
            product_review_keyword = dnw_load_db_data.dnw_review_keyword_dataframe(pcategory)
            cluster_needs = pd.merge(left = cluster_product_info_merge_brand_name, right = product_review_keyword, how = 'left', on = 'pcode')
            # cluster_needs.to_sql(name='dnw_cluster_needs_tb',con=db_conn,if_exists='append',index_label="idx",index=False)
            





            quality_tb = quality_table(cluster_product_info_merge_brand_name,pcategory,cluster_quality)
            # print(quality_table)

            needs_tb = needs_table(cluster_product_info_merge_brand_name,pcategory,cluster_needs)
            needs_tb_to_merge =needs_tb.loc[:,['pcode','needs_title_list']]
            # print(needs_tb_to_merge)

            new_df = pd.merge(left = quality_tb , right = needs_tb_to_merge, how = "left", on = "pcode")
            new_df.to_sql(name='dnw_model4_data',con=db_conn,if_exists='append',index_label="idx",index=False)





            # 품질특성 title 추출
            quality_title_pcategory = maketable(pcategory)
            quality_title_list = quality_title_pcategory.quality_title(cluster_quality)
            # print(quality_title_list)

            dnw_product_info_df = pd.DataFrame(quality_tb,columns =['pcategory','product_idx','cluster','price_range','pcode','level1','level2','level3','level4','product_name','brand_name','product_price','title_1','content_1','title_2','content_2','title_3','content_3','title_4','content_4','title_5','content_5','title_6','content_6','title_7','content_7'])
            dnw_product_info_df = dnw_product_info_df.loc[:,['cluster','title_1','content_1','title_2','content_2','title_3','content_3','title_4','content_4','title_5','content_5','title_6','content_6','title_7','content_7']]
            # print(dnw_product_info_df)
            #클러스터링 길이를 추출하는 수학식
            cluster_length = len(dnw_product_info_df.drop_duplicates(["cluster"]))

            dnw_quality_df = pd.DataFrame({'pcategory' : pcategory ,'cluster' : list(range(cluster_length))})
            for num in range(len(quality_title_list)):
                tb_list = list()
                title_list = dnw_product_info_df.loc[:, [f'title_{num+1}']].values.tolist()
                title_list = sum(title_list,[])
                title_list = [i for i in title_list if i != None and pd.isnull(i)==False]
                title = title_list[0]
                #클러스터 수만큼 반복
                for cluster_index in range(cluster_length) :
                    content_list = dnw_product_info_df.loc[dnw_product_info_df['cluster'] == cluster_index, [f'content_{num+1}']].values.tolist()
                    content_list = sum(content_list,[])
                    content_list = [i for i in content_list if i != None and pd.isnull(i)==False]

                    content_list = ",".join(content_list)
                    numbers = re.findall(r'[0-9.]+', content_list)
                    content_list = content_list.split(",")

                    if len(content_list) == len(numbers):
                        """숫자로만 이루어진 경우 >> 최대최소값"""
                        s_range = [cluster_index,title,f"{min(content_list)}{separator}{max(content_list)}"]
                        tb_list.append(s_range)
                    else:
                        cnt = Counter(content_list)
                        s_range = [cluster_index,title,f"{list(cnt)[0]}"]
                        tb_list.append(s_range)
                        """문자가 있는 경우 >> 최빈값"""
                        
                content_df = pd.DataFrame(tb_list,columns = ['cluster',f'title{num+1}',f'content{num+1}'])
                dnw_quality_df = pd.merge(left = dnw_quality_df , right = content_df, how = "left", on = "cluster")
            # dnw_quality_df.to_sql(name='dnw_품질특성_결과',con=db_conn,if_exists='append',index=False)





            dnw_product_info_df = pd.DataFrame(needs_tb,columns =['pcategory','product_idx','cluster','price_range','pcode','level1','level2','level3','level4','product_name','brand_name','product_price',"needs_title_list"])
            dnw_product_info_df = dnw_product_info_df.loc[:,['product_idx','cluster',"needs_title_list"]]
            # print(dnw_product_info_df)
            #클러스터링 길이를 추출하는 수학식
            cluster_length = len(dnw_product_info_df.drop_duplicates(["cluster"]))

            #클러스터 수만큼 반복
            tb_list = list()
            for cluster_index in range(cluster_length) :
                content_list = dnw_product_info_df.loc[dnw_product_info_df['cluster'] == cluster_index, ['needs_title_list']].values.tolist()
                s_range = [pcategory,cluster_index,f'{separator}'.join(content_list[0][0].split(';'))]
                tb_list.append(s_range)

            dnw_needs_result_df = pd.DataFrame(tb_list,columns = ['pcategory','cluster','needs'])
            # dnw_needs_result_df.to_sql(name='dnw_요구품질_결과',con=db_conn,if_exists='append',index=False)

            new_df = pd.merge(left = dnw_quality_df , right = dnw_needs_result_df, how = "left", on = ["pcategory","cluster"])
            new_df.to_sql(name='dnw_model4',con=db_conn,if_exists='append',index_label="idx",index=False)


            print(except_list)
        except:
            except_list.append(pcategory)
            print(except_list)

# if __name__ == '__main__':
#     modelling().model_dnw("10339287")