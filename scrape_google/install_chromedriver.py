from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager


option = webdriver.ChromeOptions()
#option.add_argument("--headless")

driver = webdriver.Chrome(ChromeDriverManager().install(),options=option)
driver.maximize_window()

url = 'https://example.com/'
driver.get(url)
