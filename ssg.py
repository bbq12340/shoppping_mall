# -*- coding: utf-8 -*- 
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException, WebDriverException, JavascriptException
from bs4 import BeautifulSoup
import math, time, csv
import pandas as pd

def scrape_product_page(browser, product_link):
    product_df = pd.read_csv('ssg.csv', encoding='utf-8') 
    product_link = "http://www.ssg.com"+product_link
    try:
        browser.get(product_link)
    except TimeoutException:
        time.sleep(3)
        browser.refresh()
    browser.execute_script('window.scrollTo(0, document.body.scrollHeight);')
    time.sleep(1)
    html = browser.execute_script('return document.body.outerHTML')
    soup = BeautifulSoup(html, 'html.parser')
    title = soup.find('h2', {'class': 'cdtl_info_tit'}).text
    print(f'\n현재 크롤링 중인 상품: {title}')
    price = soup.find('span', {'class': 'cdtl_new_price'}).text.replace('\n','').replace('원','').replace('최적가', '')
    review_count = int(soup.find('div', {'class': 'cdtl_cmt_titarea'}).find('em').text.replace(',',''))
    #리뷰가 없는 경우
    if review_count == 0:
        print('리뷰 수: 0')
        rate = None
        review = None
        date = None
        row = [title, price, rate, review, date, product_link]
        with open('ssg.csv', 'a+', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile, delimiter=',')
            csv_writer.writerow(row)
    #리뷰가 있는 경우
    else:
        print(f'리뷰 수: {review_count}')
        while len(product_df.index) < review_count:
            time.sleep(0.5)
            html = browser.execute_script('return document.body.outerHTML')
            soup = BeautifulSoup(html, 'html.parser')
            review_table = soup.find('tbody',{'id':'cdtl_cmt_tbody'})
            tr = review_table.find_all('tr')[0::2]
            for r in tr:
                rate = r.find('td', {'class': 'star'}).find('em').text
                review = r.find('div', {'class': 'cdtl_cmt_tx'})
                if review:
                    review = review.text.replace('\n','')
                else:
                    review = None
                date = r.find('td', {'class': 'date'}).text.replace(' ','')
                row = [title, price, rate, review, date, product_link]
                with open('ssg.csv', 'a+', encoding='utf-8') as csvfile:
                    csv_writer = csv.writer(csvfile, delimiter=',')
                    csv_writer.writerow(row)
<<<<<<< HEAD
                product_df = pd.read_csv('ssg.csv', encoding='utf-8')
                product_df = product_df[product_df['상품명'] == title]
=======
>>>>>>> 3ecc937d58415cb2dde92d3a74e8d36e8e1300c2
                if len(product_df.index) == review_count:
                    break
            #리뷰 다음 페이지 클릭
            try:
                browser.execute_script("document.getElementById('comment_navi_area').getElementsByTagName('strong')[0].nextElementSibling.click();")
            except JavascriptException:
                pass
            
    return

def scrape_current_page(browser, PRODUCTS):
    html = browser.execute_script('return document.body.outerHTML')
    soup = BeautifulSoup(html, 'html.parser')
    thumb_list = soup.find('ul', {'class': 'cunit_thmb_lst'})
    products = thumb_list.find_all('li')
    for product in products:
        product_link = product.find('a')['href']
        PRODUCTS.append(product_link)
    return PRODUCTS

def pagination(browser, LIMITED_ITEMS):
    print("------------------------------------------------------------\n\n 신세계몰 스크롤링 중....\n\n")
    url = browser.current_url #다음페이지에 들어가기 위해 필요
    thumb_list_by_class = By.CLASS_NAME, 'cunit_thmb_lst'
    wait = WebDriverWait(browser, 30)
    wait.until(EC.presence_of_element_located(thumb_list_by_class))
    item_count = browser.find_element_by_id('area_itemCount').find_element_by_tag_name('em').get_attribute('innerText').replace(',','') #검색 결과 총 아이템 갯수
    item_count = int(item_count)
    print(f"총 아이템 수: {item_count}")
    #각 상품 크롤링하는 작업
    if item_count >= LIMITED_ITEMS:
        print(f'크롤링할 총 상품 수: {LIMITED_ITEMS}')
        PRODUCTS= []
        while len(PRODUCTS) < LIMITED_ITEMS:
            wait.until(EC.presence_of_element_located(thumb_list_by_class))
            PRODUCTS = scrape_current_page(browser, PRODUCTS)
            #다음페이지 클릭
            current_page = browser.find_element_by_class_name('com_paginate').find_element_by_tag_name('strong').get_attribute('innerText')
            next_page = int(current_page)+1
            browser.get(f"{url}&page={next_page}")
            if len(PRODUCTS) == LIMITED_ITEMS:
                break
        PRODUCTS = PRODUCTS[:LIMITED_ITEMS] 
        #각 상품 링크를 리스트로 정리완료
        #각 상품 링크로 들어가 크롤링 시작
        for p in PRODUCTS:
            scrape_product_page(browser, p)
        
    else:
        print(f'크롤링할 총 상품 수: {item_count}')
        PRODUCTS= []
        while len(PRODUCTS) < item_count:
            wait.until(EC.presence_of_element_located(thumb_list_by_class))
            PRODUCTS = scrape_current_page(browser, PRODUCTS)
            #다음페이지 클릭
            current_page = browser.find_element_by_class_name('com_paginate').find_element_by_tag_name('strong').get_attribute('innerText')
            next_page = int(current_page)+1
            browser.get(f"{url}&page={next_page}")
            if len(PRODUCTS) == item_count:
                break 
        #각 상품 링크를 리스트로 정리완료
        #각 상품 링크로 들어가 크롤링 시작
        for p in PRODUCTS:
            scrape_product_page(browser, p)

    return 
        
        
def open_browser(url):
    #options = Options()
    #options.add_argument('--headless')
    #options.add_argument('--disable-gpu')  
    browser = webdriver.Chrome(ChromeDriverManager().install())
    browser.get(url)
    return browser

def extract_ssg(url):
    LIMITED_ITEMS = 1000
    browser = open_browser(url)
    pagination(browser, LIMITED_ITEMS)
    browser.quit()
    df = pd.read_csv('ssg.csv', encoding='utf-8', index_col=0) 
    return df