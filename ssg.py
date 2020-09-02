# -*- coding: utf-8 -*- 
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException, WebDriverException
import requests
from bs4 import BeautifulSoup

def extract_ssg(url):
    LIMITED_ITEMS = 1000
    browser = open_browser(url)
    pagination(browser, LIMITED_ITEMS)

def scrape_product_page(product_link):
    product_link = "http://www.sgg.com"+product_link
    print(product_link)

def scrape_current_page(soup):
    products = soup.find_all('div', {'class': 'thmb'})
    for product in products[:page_requested_order]:
        product_link = product.find('a')['href']
        scrape_product_page(product_link)

def pagination(browser, LIMITED_ITEMS):
    thumb_list = By.CLASS_NAME, 'cunit_thmb_lst'
    page_requested_order_by_xpath = '//ul[@class="tmpl_viewtype"]/li[2]/div/div/a/span'
    wait = WebDriverWait(browser, 30)
    wait.until(EC.presence_of_element_located(thumb_list))
    page_requested_order = browser.find_element_by_xpath(page_requested_order_by_xpath).get_attribute('innerText') #한 페이지에 있는 아이템 갯수
    page_requested_order = int(page_requested_order[:-2])
    html = browser.execute_script('return document.body.outerHTML')
    soup = BeautifulSoup(html, 'html.parser')
    item_count = soup.find('div', {'id': 'area_itemCount'}).find('em').text.replace(',','') #검색 결과 총 아이템 갯수
    item_count = int(item_count)
    print(f"총 아이템 수: {item_count}")
    

def open_browser(url):
    #options = Options()
    #options.add_argument('--headless')
    #options.add_argument('--disable-gpu')  
    browser = webdriver.Chrome(ChromeDriverManager().install())
    browser.get(url)
    return browser

extract_ssg('http://www.ssg.com/search.ssg?target=all&query=%ED%8B%B0%EC%85%94%EC%B8%A0')