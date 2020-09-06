# -*- coding: utf-8 -*- 
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException, NoSuchElementException, JavascriptException
from bs4 import BeautifulSoup
import math, time, csv, json
import pandas as pd


def scrape_product_page(browser, product_link):
    product_df = pd.read_csv('coupang.csv', encoding='utf-8')
    product_link = "https://www.coupang.com"+product_link
    try:
        browser.get(product_link)
    except TimeoutException:
        time.sleep(3)
        browser.refresh()
    time.sleep(0.5)
    browser.execute_script("document.getElementsByName('review')[0].click();")
    time.sleep(1)
    html = browser.execute_script('return document.body.outerHTML')
    soup = BeautifulSoup(html, 'html.parser')
    title = soup.find('h2', {'class': 'prod-buy-header__title'}).text
    print(f'\n현재 크롤링 중인 상품: {title}')
    price = soup.find('span', {'class': 'total-price'}).find('strong').text
    review_count = soup.find('div', {'class': 'sdp-review__average__total-star__info-count'})
    #리뷰가 없는 경우
    if review_count == None:
        print('리뷰 수: 0')
        rate = None
        review = None
        date = None
        row = [title, price, rate, review, date, product_link]
        with open('coupang.csv', 'a+', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile, delimiter=',')
            csv_writer.writerow(row)
    #리뷰가 있는 경우
    else:
        review_count = int(review_count.text.replace(',',''))
        print(f'리뷰 수: {review_count}')
        while len(product_df.index) < review_count:
            time.sleep(0.5)
            html = browser.execute_script('return document.body.outerHTML')
            soup = BeautifulSoup(html, 'html.parser')
            tr = soup.find_all('article', {'class': 'sdp-review__article__list js_reviewArticleReviewList'})
            for r in tr:
                rate = r.find('div', {'class': 'js_reviewArticleRatingValue'})['data-rating']
                date = r.find('div', {'class': 'sdp-review__article__list__info__product-info__reg-date'}).text.replace('.','-')
                review = r.find('div', {'class': 'js_reviewArticleContent'})
                if review:
                    review = review.text.replace('\n', ' ')
                else:
                    review = None
                row = [title, price, rate, review, date, product_link]
                with open('coupang.csv', 'a+', encoding='utf-8') as csvfile:
                    csv_writer = csv.writer(csvfile, delimiter=',')
                    csv_writer.writerow(row)
                product_df = pd.read_csv('coupang.csv', encoding='utf-8')
                product_df = product_df[product_df['상품명'] == title]
                if len(product_df.index) == review_count:
                    break
            #리뷰 다음 페이지 클릭
            try:
                browser.execute_script("document.querySelector('.sdp-review__article__page__num--active').nextElementSibling.click();")
            except JavascriptException:
                pass
    return

def scrape_current_page(browser, PRODUCTS):
    product_list_indexes_json = browser.find_element_by_id('productList').get_attribute('data-products')
    product_list_indexes = json.loads(product_list_indexes_json)['indexes']
    html = browser.execute_script('return document.body.outerHTML')
    soup = BeautifulSoup(html, 'html.parser')
    for index in product_list_indexes:
        product_link = soup.find('a', {'data-product-id': index})['href']
        PRODUCTS.append(product_link)
    return PRODUCTS

def pagination(browser, LIMITED_ITEMS):
    print("------------------------------------------------------------\n\n 쿠팡 스크롤링 중....\n\n")
    product_list_by_id = By.ID, 'productList'
    wait = WebDriverWait(browser, 30)
    wait.until(EC.presence_of_element_located(product_list_by_id))
    item_count = browser.find_element_by_class_name('hit-count').find_elements_by_tag_name('strong')[-1].get_attribute('innerText')
    item_count = int(item_count.replace(',',''))
    print(f"총 아이템 수: {item_count}")
    #각 상품 크롤링하는 작업
    if item_count >= LIMITED_ITEMS:
        print(f'크롤링할 총 상품 수: {LIMITED_ITEMS}')
        PRODUCTS= []
        while len(PRODUCTS) < LIMITED_ITEMS:
            wait.until(EC.presence_of_element_located(product_list_by_id))
            PRODUCTS = scrape_current_page(browser, PRODUCTS)
            #다음페이지 클릭
            next_btn = browser.find_element_by_class_name('btn-next')
            next_btn.click()
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
            wait.until(EC.presence_of_element_located(product_list_by_id))
            PRODUCTS = scrape_current_page(browser, PRODUCTS)
            #다음페이지 클릭
            next_btn = browser.find_element_by_class_name('btn-next')
            next_btn.click()
            if len(PRODUCTS) == item_count:
                break
        #각 상품 링크를 리스트로 정리완료
        #각 상품 링크로 들어가 크롤링 시작
        for p in PRODUCTS:
            scrape_product_page(browser, p)

def open_browser(url):
    #options = Options()
    #options.add_argument('--headless')
    #options.add_argument('--disable-gpu')  
    browser = webdriver.Chrome(ChromeDriverManager().install())
    browser.get(url)
    return browser


def extract_coupang(url):
    LIMITED_ITEMS = 1000
    browser = open_browser(url)
    pagination(browser, LIMITED_ITEMS)
    browser.quit()    
    df = pd.read_csv('coupang.csv', encoding='utf-8', index_col=0)
    return df
