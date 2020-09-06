import tkinter as tk
from tkinter import messagebox
import csv
import pandas as pd

from ssg import extract_ssg
from coupang import extract_coupang

root = tk.Tk()
root.title('쇼핑몰 크롤러')
root.geometry("400x100")

#var
ssg = tk.StringVar()
coupang = tk.StringVar()
file_name = tk.StringVar()

#function
def extract_shopping_mall():
    with open('coupang.csv', 'w', encoding='utf-8') as f:
        csv_writer = csv.writer(f, delimiter=',')
        csv_writer.writerow(['상품명', '가격', '평점', '리뷰','작성일', '링크'])
    with open('ssg.csv' ,'w', encoding='utf-8') as f:
        csv_writer = csv.writer(f, delimiter=',')
        csv_writer.writerow(['상품명', '가격', '평점', '리뷰','작성일', '링크'])

    ssg_df = extract_ssg(ssg.get())
    ssg_df.to_excel(f"{file_name.get()}-신세계몰.xlsx", encoding='utf-8')
    coupang_df = extract_coupang(coupang.get())
    coupang_df.to_excel(f"{file_name.get()}-쿠팡.xlsx", encoding='utf-8')
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


#button
search_btn = tk.Button(root, text='검색', height=1, width=7, command=extract_shopping_mall)
search_btn.grid(row=3, column=1, pady=15, columnspan=2)

root.mainloop()