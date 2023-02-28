import pymysql

def search_amz_crawl_list():
    db = pymysql.connect(host='139.150.82.178', user='root', db='kisti_crawl', password='vision9551', charset='utf8')
    curs = db.cursor(pymysql.cursors.DictCursor)

    sql = "select level1,level2,level3,level4,url from amz_category"

    curs.execute(sql)

    rows = curs.fetchall()
    
    db.commit()
    db.close()
    return rows

def search_dnw_crawl_list():
    db = pymysql.connect(host='139.150.82.178', user='root', db='kisti_crawl', password='vision9551', charset='utf8')
    curs = db.cursor(pymysql.cursors.DictCursor)

    sql = "select level1,level2,level3,level4,url,pcategory from dnw_category"

    curs.execute(sql)

    rows = curs.fetchall()
      
    db.commit()
    db.close()
    return rows

class model4:
    def __init__(self):
        pass

    def search_amz_data(self,url,cluster):
        db = pymysql.connect(host='139.150.82.178', user='root', db='kisti_crawl', password='vision9551', charset='utf8')
        curs = db.cursor(pymysql.cursors.DictCursor)

        sql = f"select * from amz_model4_data where url = '{url}' and cluster = '{cluster}'"

        curs.execute(sql)

        rows = curs.fetchall()
        
        db.commit()
        db.close()
        return rows
    
    def search_dnw_data(self,pcategory,cluster):
        db = pymysql.connect(host='139.150.82.178', user='root', db='kisti_crawl', password='vision9551', charset='utf8')
        curs = db.cursor(pymysql.cursors.DictCursor)

        sql = f"select *from dnw_model4_data where pcategory = {pcategory} and cluster = '{cluster}'"

        curs.execute(sql)

        rows = curs.fetchall()
        
        db.commit()
        db.close()
        return rows

    def search_amz(self,url):
        db = pymysql.connect(host='139.150.82.178', user='root', db='kisti_crawl', password='vision9551', charset='utf8')
        curs = db.cursor(pymysql.cursors.DictCursor)
        
        sql = f"select * from amz_model4 where url = '{url}'";
        curs.execute(sql)
        
        rows = curs.fetchall()

        db.commit()
        db.close()
        return rows
    
    def search_dnw(self,pcategory):
        db = pymysql.connect(host='139.150.82.178', user='root', db='kisti_crawl', password='vision9551', charset='utf8')
        curs = db.cursor(pymysql.cursors.DictCursor)
        
        sql = f"select * from dnw_model4 where pcategory like '{pcategory}'";
        curs.execute(sql)
        
        rows = curs.fetchall()
        
        db.commit()
        db.close()
        return rows