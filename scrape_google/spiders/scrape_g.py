import os, random, sqlite3, urllib
import scrapy
from scrapy import Selector
import pandas as pd
from datetime import datetime
from urllib.parse import urlencode
from os import path
from pandas import DataFrame
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import selenium.common.exceptions as exception
from scrape_google.organic_results import get_organic_results


load_dotenv()

def create_db_and_folder():
    output_html = os.environ.get("output_html")
    teporary_file = os.environ.get("teporary_file")
    #input_data = os.environ.get("input_data")
    #file_kw = input_data+os.environ.get("kw_file")
    file_kw = os.environ.get("kw_file")

    #creazione Cartelle
    config_file = 'config_file'
    if not os.path.exists(output_html):
        os.makedirs(output_html)
    # if not os.path.exists(output_screenshot):
    #     os.makedirs(output_screenshot)
    if not os.path.exists(teporary_file):
        os.makedirs(teporary_file)
    test_proxy = 'spiders/output_html/test_proxy.txt'

    #
    # File
    #file_kw = input_data+'/keywords.txt'
    file_proxies = os.environ.get("file_proxies")
    db_name_keyword = os.environ.get("db_name_keyword")
    db_name_proxy = os.environ.get("db_name_proxy")

    #
    # Creazione dataframe proxy
    dataframe = pd.read_csv(file_proxies, encoding='utf-8', header=None)
    #timestr = time.strftime('%Y-%m-%d %H:%M:%S')
    timestr_now = str(datetime.now())
    #print(timestr_now)
    timestr = datetime.fromisoformat(timestr_now).timestamp()
    #print(timestr)
    dataframe['TIME'] = timestr
    dataframe.columns = ['PROXY','TIME']
    #print(dataframe)

    #
    # Creazione DB da Dataframe PROXY
    check_db = path.exists(db_name_proxy)
    #print(check_db)
    if check_db == False:
        conn = sqlite3.connect(db_name_proxy,detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        c = conn.cursor()
        c.execute('CREATE TABLE PROXY_LIST (PROXY text, TIME timestamp)')
        conn.commit()
        df = DataFrame(dataframe, columns= ['PROXY','TIME'])
        df.to_sql('PROXY_LIST', conn, if_exists='replace', index = True)
        c.execute('''  
        SELECT * FROM PROXY_LIST
                ''')
        # for row in c.fetchall():
        #     print(row)
        del df
        del dataframe
        conn.close()
    else:
        print('DB già presente PROXY')

    #
    # Creazione dataframe keyword
    dataframe = pd.read_csv(file_kw, encoding='utf-8', sep=';', header=None)
    dataframe['CHECKING'] = 0
    dataframe['SUM'] = 0
    dataframe.columns = ['KEYWORDS','CHECKING','SUM']
    #print(dataframe)

    #
    # Creazione DB da Dataframe KEYWORD
    check_db = path.exists(db_name_keyword)
    #print(check_db)
    if check_db == False:
        conn = sqlite3.connect(db_name_keyword)
        c = conn.cursor()
        c.execute('CREATE TABLE KEYWORDS_LIST (KEYWORDS text, CHECKING number, SUM number)')
        conn.commit()
        df = DataFrame(dataframe, columns= ['KEYWORDS', 'CHECKING', 'SUM'])
        df.to_sql('KEYWORDS_LIST', conn, if_exists='replace', index = True)
        c.execute('''  
        SELECT * FROM KEYWORDS_LIST
                ''')
        #for row in c.fetchall():
        #    print(row)
        del df
        del dataframe
        conn.close()
    else:
        print('DB già presente KEYWORDS')
#create_db_and_folder()

def select_proxy(db_name_proxy):
    conn = sqlite3.connect(db_name_proxy)
    c = conn.cursor()
    data=pd.read_sql_query("SELECT PROXY FROM PROXY_LIST WHERE TIME = ( SELECT MIN(TIME) FROM PROXY_LIST);",conn)
    #print(type(data['PROXY'].iat[0]))
    global proxy
    proxy = (data['PROXY'].iat[0])
    #print(f'---------------------Request IP is {proxy}')
    timestr_now = str(datetime.now())
    #print(timestr_now)
    #global timestr
    timestr = datetime.fromisoformat(timestr_now).timestamp()
    #print(timestr)
    c.execute("Update PROXY_LIST set TIME = ? where PROXY = ?",(timestr,proxy))
    conn.commit()
    c.execute("Update PROXY_LIST set TIME = ? where PROXY = ?",(timestr,proxy,))
    conn.commit()
    #print('pausa 1 sec')
    conn.close()
    return proxy


def select_keyword(db_name_keyword):
    #print('-------------------------')
    conn = sqlite3.connect(db_name_keyword)
    c = conn.cursor()
    data = pd.read_sql_query("SELECT KEYWORDS FROM KEYWORDS_LIST WHERE SUM <> 2 AND CHECKING = 0 LIMIT 1;",conn)
    #print(type(data['KEYWORDS'].iat[0]))
    global keyword
    keyword = (data['KEYWORDS'].iat[0])
    c.execute("Update KEYWORDS_LIST set CHECKING = 1 where KEYWORDS = ?",(keyword,))
    conn.commit()
    conn.close()
    num = random.randint(1,2)
    #print(f'pausa {num} sec')
    return keyword

def select_new_keyword(keyword):
    #print(keyword)
    #global new_keyword
    new_keyword = urllib.parse.quote_plus(keyword)
    #print(new_keyword)
    return new_keyword

create_db_and_folder()
db_name_proxy = os.environ.get("db_name_proxy")
db_name_keyword = os.environ.get("db_name_keyword")

# Variabili
uule = os.environ.get("uule")
hl = os.environ.get("hl")
gl = os.environ.get("gl")
domain_search = os.environ.get("domain_search")
urls_to_scrape = []
num_random_process = random.randint(10,10)
for _ in range(num_random_process):
    keyword = select_keyword(db_name_keyword)
    new_keyword = select_new_keyword(keyword)
    url = f'https://{domain_search}search?q={new_keyword}&oq={new_keyword}&hl={hl}&gl={gl}&uule={uule}&sourceid=chrome&ie=UTF-8'
    urls_to_scrape.append(url)

print(urls_to_scrape)
# scraper
class ScrapeGSpider(scrapy.Spider):

    name = 'scrape_g'
    #allowed_domains = ['google.it']
    #Select Keyword e Proxy
    
    proxy = select_proxy(db_name_proxy)
    print(urls_to_scrape)
    

    def start_requests(self):
        for url in urls_to_scrape:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):

        # get title of a page
        title = response.css('title::text').get()
        extract_keyword = title.strip().split('-')[0]
        extract_keyword = extract_keyword.rstrip()
        print(extract_keyword)

        # save HTML file
        with open(f'spiders/output_html/{extract_keyword}.html', 'wb') as html_file:
            html_file.write(response.body)

        get_organic_results(extract_keyword, response)




# https://github.com/TeamHG-Memex/scrapy-rotating-proxies#usage

# import scrapy
# from scrapy import Selector
# import urllib, re, os, shutil
# from datetime import datetime
# import pandas as pd
# from urllib.parse import urlencode

# from scrape_google.organic_results import get_organic_results
# from scrape_google.prepare_scraper import create_folder, read_keywords

# # creazione cartella output
# output_folder = 'spiders/output'
# create_folder(output_folder)

# # creazione lista keyword
# keywords_from_file = 'spiders/kw_list.txt'
# kw_list = read_keywords(keywords_from_file)
# print(kw_list)


# # creazione lista url per lo scraping
# domain_search = 'www.google.it'
# hl = 'IT'
# gl = 'it'
# uule = 'w+CAIQICIFSXRhbHk'

# urls_to_scrape = []
# for keyword in kw_list:
#     new_keyword = urllib.parse.quote_plus(keyword)
#     print(f'{keyword} - {new_keyword}')
#     new_url = f'https://{domain_search}/search?q={new_keyword}&oq={new_keyword}&hl={hl}&gl={gl}&uule={uule}&sourceid=chrome&ie=UTF-8'
#     print(new_keyword)
#     urls_to_scrape.append(new_url)

# print(urls_to_scrape)
# print(type(urls_to_scrape))


# # scraper
# class ScrapeGSpider(scrapy.Spider):

#     name = 'scrape_g'
#     #allowed_domains = ['google.it']
#     start_urls = urls_to_scrape

#     def start_requests(self):
#         for url in urls_to_scrape:
#             yield scrapy.Request(url=url, callback=self.parse)

#     def parse(self, response):

#         # get title of a page
#         title = response.css('title::text').get()
#         extract_keyword = title.strip().split('-')[0]
#         extract_keyword = extract_keyword.rstrip()
#         print(extract_keyword)

#         # save HTML file
#         with open(f'{output_folder}/{extract_keyword}.html', 'wb') as html_file:
#             html_file.write(response.body)

        
        
#         get_organic_results(extract_keyword, response)