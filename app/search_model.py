import config

import pymysql

def search_amz_crawl_list():
    mydb = pymysql.connect(host=config.DATABASE_CONFIG['host'],
                       user=config.DATABASE_CONFIG['user'],
                       password=config.DATABASE_CONFIG['password'],
                       database=config.DATABASE_CONFIG['dbname'],
                       cursorclass=pymysql.cursors.DictCursor)
    cursor = mydb.cursor()

    sql = "select level1,level2,level3,level4,url from TB_AMZ_CATEGORY;"

    cursor.execute(sql)

    rows = cursor.fetchall()
    
    mydb.commit()
    mydb.close()
    return rows

def search_dnw_crawl_list():
    mydb = pymysql.connect(host=config.DATABASE_CONFIG['host'],
                       user=config.DATABASE_CONFIG['user'],
                       password=config.DATABASE_CONFIG['password'],
                       database=config.DATABASE_CONFIG['dbname'],
                       cursorclass=pymysql.cursors.DictCursor)
    cursor = mydb.cursor()

    sql = "select level1,level2,level3,level4,pcategory from TB_DNW_CATEGORY;"

    cursor.execute(sql)

    rows = cursor.fetchall()
      
    mydb.commit()
    mydb.close()
    return rows

def search_amz_keyword(keyword):
    mydb = pymysql.connect(host=config.DATABASE_CONFIG['host'],
                       user=config.DATABASE_CONFIG['user'],
                       password=config.DATABASE_CONFIG['password'],
                       database=config.DATABASE_CONFIG['dbname'],
                       cursorclass=pymysql.cursors.DictCursor)
    cursor = mydb.cursor()

    sql = f"select level1,level2,level3,level4,url from TB_AMZ_CATEGORY where level1 like '%{keyword}%' OR LEVEL2 LIKE '%{keyword}%' OR LEVEL3 LIKE '%{keyword}%' OR LEVEL4 LIKE '%{keyword}%';"
    cursor.execute(sql)

    rows = cursor.fetchall()
      
    mydb.commit()
    mydb.close()
    return rows


def search_dnw_keyword(keyword):
    mydb = pymysql.connect(host=config.DATABASE_CONFIG['host'],
                       user=config.DATABASE_CONFIG['user'],
                       password=config.DATABASE_CONFIG['password'],
                       database=config.DATABASE_CONFIG['dbname'],
                       cursorclass=pymysql.cursors.DictCursor)
    cursor = mydb.cursor()

    sql = f"select level1,level2,level3,level4,url,pcategory from TB_DNW_CATEGORY where level1 like '%{keyword}%' OR LEVEL2 LIKE '%{keyword}%' OR LEVEL3 LIKE '%{keyword}%' OR LEVEL4 LIKE '%{keyword}%';"
    cursor.execute(sql)

    rows = cursor.fetchall()

    mydb.commit()
    mydb.close()
    return rows

class model4:
    def __init__(self):
        pass

    def search_amz_data(self,url,cluster):
        mydb = pymysql.connect(host=config.DATABASE_CONFIG['host'],
                       user=config.DATABASE_CONFIG['user'],
                       password=config.DATABASE_CONFIG['password'],
                       database=config.DATABASE_CONFIG['dbname'],
                       cursorclass=pymysql.cursors.DictCursor)
        cursor = mydb.cursor()

        sql = f"select * from TB_AMZ_MODEL4_DATA where url = '{url}' and cluster = '{cluster}';"

        cursor.execute(sql)

        rows = cursor.fetchall()
        
        mydb.commit()
        mydb.close()
        return rows
    
    def search_dnw_data(self,pcategory,cluster):
        mydb = pymysql.connect(host=config.DATABASE_CONFIG['host'],
                       user=config.DATABASE_CONFIG['user'],
                       password=config.DATABASE_CONFIG['password'],
                       database=config.DATABASE_CONFIG['dbname'],
                       cursorclass=pymysql.cursors.DictCursor)
        cursor = mydb.cursor()

        sql = f"select *from TB_DNW_MODEL4_DATA where pcategory = {pcategory} and cluster = '{cluster}';"

        cursor.execute(sql)

        rows = cursor.fetchall()

        mydb.commit()
        mydb.close()
        return rows

    def search_amz(self,url):
        mydb = pymysql.connect(host=config.DATABASE_CONFIG['host'],
                       user=config.DATABASE_CONFIG['user'],
                       password=config.DATABASE_CONFIG['password'],
                       database=config.DATABASE_CONFIG['dbname'],
                       cursorclass=pymysql.cursors.DictCursor)
        cursor = mydb.cursor()

        sql = f"select * from TB_AMZ_MODEL4 where url = '{url}';"
        cursor.execute(sql)

        rows = cursor.fetchall()

        mydb.commit()
        mydb.close()
        return rows
    
    def search_dnw(self,pcategory):
        mydb = pymysql.connect(host=config.DATABASE_CONFIG['host'],
                       user=config.DATABASE_CONFIG['user'],
                       password=config.DATABASE_CONFIG['password'],
                       database=config.DATABASE_CONFIG['dbname'],
                       cursorclass=pymysql.cursors.DictCursor)
        cursor = mydb.cursor()

        sql = f"select * from TB_DNW_MODEL4 where pcategory like '{pcategory}';"
        cursor.execute(sql)

        rows = cursor.fetchall()

        mydb.commit()
        mydb.close()
        return rows