import tkinter as tk
from tkinter import messagebox
import csv
import pandas as pd

from ssg import extract_ssg
from coupang import extract_coupang

root = tk.Tk()
root.title('쇼핑몰 크롤러')
root.geometry("400x150")

#var
ssg = tk.StringVar()
coupang = tk.StringVar()
file_name = tk.StringVar()
checkbox = tk.IntVar()

#function
def extract_shopping_mall():
    if checkbox.get() == 0:
        if ssg.get().find("www.ssg.com/") != -1:
            with open('source/ssg.csv', 'w', encoding='utf-8') as f:
                csv_writer = csv.writer(f, delimiter=',')
                csv_writer.writerow(['상품명', '가격', '평점', '리뷰','작성일', '링크'])
            extract_ssg(ssg.get())
            df = pd.read_csv('source/ssg.csv', encoding='utf-8')
            df = df.drop_duplicates(subset=['상품명', '리뷰', '작성일'])
            df.to_excel(f"{file_name.get()}-신세계몰.xlsx", encoding='utf-8')
        else:
            print('신세계몰 사이트의 정확한 주소를 확인해주세요.')
            pass
        if coupang.get().find("www.coupang.com/") != -1:
            with open('source/coupang.csv' ,'w', encoding='utf-8') as f:
                csv_writer = csv.writer(f, delimiter=',')
                csv_writer.writerow(['상품명', '가격', '평점', '리뷰', '조사', '작성일', '링크'])
            extract_coupang(coupang.get())
            df = pd.read_csv('source/coupang.csv', encoding='utf-8')
            df = df.drop_duplicates(subset=['상품명', '리뷰', '작성일'])
            df.to_excel(f"{file_name.get()}-쿠팡.xlsx", encoding='utf-8')
        else:
            print('쿠팡 사이트의 정확한 주소를 확인해주세요.')
            pass
    else:
        if ssg.get().find("www.ssg.com/") != -1:
            extract_ssg(ssg.get())
            df = pd.read_csv('source/ssg.csv', encoding='utf-8')
            df = df.drop_duplicates(subset=['상품명', '리뷰', '작성일'])
            df.to_excel(f"{file_name.get()}-신세계몰.xlsx", encoding='utf-8')
        elif coupang.get().find("www.coupang.com/") != -1:
            extract_coupang(coupang.get())
            df = pd.read_csv('source/coupang.csv', encoding='utf-8')
            df = df.drop_duplicates(subset=['상품명', '리뷰', '작성일'])
            df.to_excel(f"{file_name.get()}-쿠팡.xlsx", encoding='utf-8')
    messagebox.showinfo('info', '크롤링 완료')

#label
ssg_label = tk.Label(root, text="신세계몰")
ssg_label.grid(row=0, column=0)

coupang_label = tk.Label(root, text="쿠팡")
coupang_label.grid(row=1, column=0)

file_name_label = tk.Label(root, text="파일명")
file_name_label.grid(row=2, column=0)

#entry
ssg_entry = tk.Entry(root, width=45, textvariable=ssg)
ssg_entry.grid(row=0, column=1)

coupang_entry = tk.Entry(root, width=45, textvariable=coupang)
coupang_entry.grid(row=1, column=1)

file_name_entry = tk.Entry(root, width=15, textvariable=file_name)
file_name_entry.grid(row=2, column=1)

#checkbox
c = tk.Checkbutton(root, text='수정모드', variable=checkbox)
c.grid(row=3, column=1, pady=15, columnspan=2)


#button
search_btn = tk.Button(root, text='검색', height=1, width=7, command=extract_shopping_mall)
search_btn.grid(row=4, column=1, pady=5, columnspan=2)

root.mainloop()