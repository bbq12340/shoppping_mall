# -*- coding: utf-8 -*- 
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException, NoSuchElementException, JavascriptException, UnexpectedAlertPresentException
from bs4 import BeautifulSoup
import math, time, csv, json
import pandas as pd


def scrape_product_page(browser, product_link):
    product_df = pd.read_csv('source/coupang.csv', encoding='utf-8')
    product_link = "https://www.coupang.com"+product_link
    try:
        browser.get(product_link)
    except TimeoutException:
        time.sleep(3)
        browser.refresh()
    time.sleep(1)
    try:
        browser.find_element_by_class_name('oos-label')
        print('일시품절된 상품입니다.')
    except NoSuchElementException:
        pass
    t = 0
    while t < 10:
        recommend_by_class_name = By.CLASS_NAME, 'recommend-widget-header'
        t=t+1
        if t >= 10:
            print('10번 새로고침 실패')
            with open('bug_url.txt', 'a') as f:
                    f.write(f'{product_link}\n')
            return
        try:
            WebDriverWait(browser, 30).until(EC.presence_of_element_located(recommend_by_class_name))
        except TimeoutException:
        #상품상세가 없는 경우도 있다.
            try:
                browser.find_element_by_class_name('prod-not-find-known__buy__info__txt')
                print('판매 중인 상품이 아닙니다.')
                return
            except NoSuchElementException:
                browser.refresh()
                time.sleep(3)
                continue
        html = browser.execute_script('return document.body.outerHTML')
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.find('h2', {'class': 'prod-buy-header__title'}).text
        print(f'\n현재 크롤링 중인 상품: {title}')
        try:
            price = soup.find('div', {'class': 'prod-major-price'}).find('strong').text
            review_count_backup = int(soup.find('span', {'class': 'count'}).text.split('개')[0].replace(',','')) #이름 가격 등이 적혀 있는 곳에도 상품평의 수가 적혀있다.
            break
        except AttributeError:
            browser.refresh()
            time.sleep(3)
            continue
    product_df = product_df[product_df['상품명'] == title] #source/coupang.csv 데이터 프레임 중 '상품명' 이 같은 열.
    #리뷰가 없는 경우
    if review_count_backup == 0:
        print('리뷰 수: 0')
        if len(product_df) == 1:
            return
        rate = None
        review = None
        survey = None
        date = None
        row = [title, price, rate, review, survey, date, product_link]
        with open('source/coupang.csv', 'a+', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile, delimiter=',')
            csv_writer.writerow(row)
    #리뷰가 있는 경우
    else:
        while True:
            try:
                browser.execute_script('window.scrollTo(0, document.body.scrollHeight);')
                browser.execute_script("document.getElementsByName('review')[0].click();")
                time.sleep(1)
                review_count = browser.find_element_by_class_name('product-tab-review-count').get_attribute('innerText')
                review_count = review_count.replace('(','').replace(')','').replace(',','')
                try:
                    review_count = int(review_count)
                except ValueError:
                    print('Value error occured. Trying again...')
                    browser.refresh()
                    time.sleep(3)
                    continue
                break
            except (NoSuchElementException, StaleElementReferenceException, JavascriptException):
                print('An error occured. Trying again...')
                browser.refresh()
                time.sleep(3)
                continue
            except UnexpectedAlertPresentException:
                print('Unexpected Alert has been occured.')
                alert = browser.switch_to_alert
                alert.accept()
                with open('bug_url.txt', 'a') as f:
                    f.write(f'{product_link}\n')
                return
        print(f'리뷰 수: {review_count_backup}')
        while len(product_df.index) < review_count_backup:
            time.sleep(1)
            html = browser.execute_script('return document.body.outerHTML')
            soup = BeautifulSoup(html, 'html.parser')
            no_review = soup.find('div', {'class': 'sdp-review__article__no-review--active'})
            if no_review:
                print('(재)리뷰 수: 0')
                rate = None
                review = None
                survey = None
                date = None
                row = [title, price, rate, review, survey, date, product_link]
                with open('source/coupang.csv', 'a+', encoding='utf-8') as csvfile:
                    csv_writer = csv.writer(csvfile, delimiter=',')
                    csv_writer.writerow(row)
                return
            tr = soup.find_all('article', {'class': 'sdp-review__article__list js_reviewArticleReviewList'})
            for r in tr:
                rate = r.find('div', {'class': 'js_reviewArticleRatingValue'})['data-rating']
                date = r.find('div', {'class': 'sdp-review__article__list__info__product-info__reg-date'}).text.replace('.','-')
                review = r.find('div', {'class': 'js_reviewArticleContent'})
                survey = r.find('div', {'class': 'sdp-review__article__list__survey'})
                if review:
                    review = review.text.replace('\n', ' ')
                    review = ' '.join(review.split())
                else:
                    review = None
                if survey:
                    survey = survey.text.replace('\n', ' ')
                    survey = ' '.join(survey.split())
                else:
                    survey = None
                row = [title, price, rate, review, survey, date, product_link]
                with open('source/coupang.csv', 'a+', encoding='utf-8') as csvfile:
                    csv_writer = csv.writer(csvfile, delimiter=',')
                    csv_writer.writerow(row)
                product_df = pd.read_csv('source/coupang.csv', encoding='utf-8')
                product_df = product_df[product_df['상품명'] == title]
                if len(product_df.index) == review_count_backup:
                    break
            #리뷰 다음 페이지 클릭
            try:
                browser.execute_script("document.querySelector('.sdp-review__article__page__num--active').nextElementSibling.click();")
            except JavascriptException:
                pass
    return

def scrape_current_page(browser, PRODUCTS):
    product_list_indexes_json = browser.find_element_by_class_name('search-product-list').get_attribute('data-products')
    product_list_indexes = json.loads(product_list_indexes_json)['indexes']
    html = browser.execute_script('return document.body.outerHTML')
    soup = BeautifulSoup(html, 'html.parser')
    for index in product_list_indexes:
        product_link = soup.find('a', {'data-product-id': index})['href']
        PRODUCTS.append(product_link)
    return PRODUCTS

def pagination(browser, LIMITED_ITEMS):
    print("------------------------------------------------------------\n\n 쿠팡 스크롤링 중....\n\n")
    product_list_by_class_name = By.CLASS_NAME, 'search-product-list'
    wait = WebDriverWait(browser, 30)
    try:
        wait.until(EC.visibility_of_element_located(product_list_by_class_name))
    except TimeoutException:
        pass
    item_count = browser.find_element_by_class_name('hit-count').find_elements_by_tag_name('strong')[-1].get_attribute('innerText')
    item_count = int(item_count.replace(',',''))
    print(f"총 아이템 수: {item_count}")
    #각 상품 크롤링하는 작업
    if item_count >= LIMITED_ITEMS:
        print(f'크롤링할 총 상품 수: {LIMITED_ITEMS}')
        PRODUCTS= []
        while len(PRODUCTS) < LIMITED_ITEMS:
            try:
                wait.until(EC.visibility_of_element_located(product_list_by_class_name))
            except TimeoutException:
                pass
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
            try:
                wait.until(EC.visibility_of_element_located(product_list_by_class_name))
            except TimeoutException:
                pass
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
    df = pd.read_csv('source/coupang.csv', encoding='utf-8', index_col=0)
    return df
