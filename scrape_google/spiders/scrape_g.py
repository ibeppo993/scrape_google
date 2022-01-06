# https://github.com/TeamHG-Memex/scrapy-rotating-proxies#usage

import scrapy
from scrapy import Selector
import urllib, re, os, shutil
from datetime import datetime
import pandas as pd

from scrape_google.organic_results import get_organic_results
from scrape_google.prepare_scraper import create_folder, read_keywords

# creazione cartella output
output_folder = 'spiders/output'
create_folder(output_folder)

# creazione lista keyword
keywords_from_file = 'spiders/kw_list.txt'
kw_list = read_keywords(keywords_from_file)
print(kw_list)

# creazione lista url per lo scraping
domain_search = 'www.google.it'
hl = 'IT'
gl = 'it'
uule = 'w+CAIQICIFSXRhbHk'

urls_to_scrape = []
for keyword in kw_list:
    new_keyword = urllib.parse.quote_plus(keyword)
    print(f'{keyword} - {new_keyword}')
    new_url = f'https://{domain_search}/search?q={new_keyword}&oq={new_keyword}&hl={hl}&gl={gl}&uule={uule}&sourceid=chrome&ie=UTF-8'
    print(new_keyword)
    urls_to_scrape.append(new_url)

print(urls_to_scrape)
print(type(urls_to_scrape))


# scraper
class ScrapeGSpider(scrapy.Spider):

    name = 'scrape_g'
    #allowed_domains = ['google.it']
    start_urls = urls_to_scrape

    def parse(self, response):

        # get title of a page
        title = response.css('title::text').get()
        extract_keyword = title.strip().split('-')[0]
        extract_keyword = extract_keyword.rstrip()
        print(extract_keyword)

        # save HTML file
        with open(f'{output_folder}/{extract_keyword}.html', 'wb') as html_file:
            html_file.write(response.body)

        
        
        get_organic_results(extract_keyword, response)