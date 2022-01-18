import __main__
import pandas as pd
import urllib, re, os, shutil
from datetime import datetime
import scrapy
from scrapy import Selector

def get_organic_results(extract_keyword, response):

    output_csv = 'spiders/output'

    #get link
    # //*[@id="rso"]/div[@class="g"]
    # //*[@id="rso"]/div[@class="hlcw0c"]
    position = 1
    div_obj = {}
    div_obj['Position'] = []
    div_obj['Keyword'] = []
    div_obj['Titles'] = []
    div_obj['Links'] = []
    results_in_page = response.xpath('//*[@id="rso"]/div[@class="g"]')
    #print(results_in_page)

    for index, result_in_page in enumerate(results_in_page):
    #for organic_result in result_in_page:
        #print(type(organic_result))

        # posizione
        div_obj['Position'].append(position)
        position += 1

        # keyword
        div_obj['Keyword'].append(extract_keyword)

        # title snippet
        title_snippet = result_in_page.xpath('.//h3/text()').get()
        
        div_obj['Titles'].append(title_snippet)

        # link snippet
        link_snippet = result_in_page.xpath('.//a/@href').get()
        div_obj['Links'].append(link_snippet)

    print(div_obj)
    
    
    #write to csv
    div_obj_df = pd.DataFrame(div_obj, index=None)
    #now = datetime.now()
    dt_string = datetime.now().strftime("%Y%m%d-%H")
    div_obj_df.to_csv(f'{output_csv}/{dt_string}_organic_result.csv', mode='a', header=False, index=False, encoding='UTF-8', sep='\t')