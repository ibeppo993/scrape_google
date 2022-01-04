import __main__
import pandas as pd
import urllib, re, os, shutil
from datetime import datetime 

def get_organic_results(extract_keyword, response):
    #get link
    # //*[@id="rso"]/div[@class="g"]
    # //*[@id="rso"]/div[@class="hlcw0c"]
    position = 1
    div_obj = {}
    div_obj['Position'] = []
    div_obj['Keyword'] = []
    #div_obj['Titles'] = []
    #div_obj['Links'] = []
    result_in_page = response.xpath('//*[@id="rso"]/div[@class="g"]').getall()

    for organic_result in result_in_page:
        #print(type(organic_result))

        #poszione
        div_obj['Position'].append(position)
        position += 1

        #keyword
        div_obj['Keyword'].append(extract_keyword)




    print(div_obj)
    
    
    #write to csv
    div_obj_df = pd.DataFrame(div_obj, index=None)
    #now = datetime.now()
    dt_string = datetime.now().strftime("%Y%m%d-%H")
    div_obj_df.to_csv(f'output/{dt_string}_organic_result.csv', mode='a', header=False, index=False, encoding='UTF-8', sep='\t')