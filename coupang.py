import requests
from bs4 import BeautifulSoup

user_agent = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'
    }

r = requests.get('https://www.coupang.com/np/search?q=%ED%81%AC%EB%A6%BC%EB%B9%B5&brand=&offerCondition=&filter=&availableDeliveryFilter=&filterType=&isPriceRange=false&priceRange=&minPrice=&maxPrice=&page=1&trcid=&traid=&filterSetByUser=true&channel=user&backgroundColor=&component=&rating=0&sorter=scoreDesc&listSize=72', headers=user_agent)
soup = BeautifulSoup(r.text, 'html.parser')
product_link = soup.select('.search-product-link')
for link in product_link:
    print(link['href'])
