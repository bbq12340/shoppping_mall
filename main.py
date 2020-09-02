import tkinter as tk
from tkinter import messagebox


root = tk.Tk()
root.title('쇼핑몰 크롤러')
root.geometry("400x100")

#var
ssg = tk.StringVar()
coupang = tk.StringVar()

#function

#label
ssg_label = tk.Label(root, text="신세계몰")
ssg_label.grid(row=0, column=0)

coupang_label = tk.Label(root, text="쿠팡")
coupang_label.grid(row=1, column=0)

#entry
ssg_entry = tk.Entry(root, width=45, textvariable=coupang)
ssg_entry.grid(row=0, column=1)

coupang_entry = tk.Entry(root, width=45, textvariable=coupang)
coupang_entry.grid(row=1, column=1)


#button
search_btn = tk.Button(root, text='검색', height=1, width=7)
search_btn.grid(row=2, column=1, pady=15, columnspan=2)

root.mainloop()