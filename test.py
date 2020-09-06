from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd

product_df = pd.read_csv('ssg.csv', encoding='utf-8')
print(product_df.columns)
df = product_df[product_df['상품명'] == '[삼립] 정통 크림빵3 원산지: 상세설명참조']
print(len(df.index))