import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from excel_utils import initialize_excel
from ui_material_input import show_material_input
from ui_material_list import show_material_list
from ui_recipe_input import show_recipe_input
from ui_recipe_list import show_recipe_list

# 上部帯
def header(root, text):
    top_frame = tk.Frame(root, bg="#bcd2ee", height=80)
    top_frame.pack(fill=tk.X)
    tk.Label(top_frame, text=text, font=("Arial", 18, "bold"), bg="#bcd2ee").pack(pady=20)
 
# 下部帯   
def footer(root):
    bottom_frame = tk.Frame(root, bg="#bcd2ee", height=80)
    bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)
    

# トップ画面
def show_top():
    clear_window()
    # 上部帯
    header(root, "ご使用される機能を選択してください")

    # 中央の機能選択エリア
    center_frame = tk.Frame(root)
    center_frame.pack(expand=True, pady=20)

    # ボタンとラベルを配置
    btn_info = [
        ("材料登録", lambda: show_material_input(root, show_top, header, footer)),
        ("材料一覧・編集", lambda: show_material_list(root, show_top, header, footer)),
        ("レシピ登録", lambda: show_recipe_input(root, show_top, header, footer)),
        ("レシピ一覧・編集", lambda: show_recipe_list(root, show_top, header, footer)),
    ]
    for i, (text, cmd) in enumerate(btn_info):
        row, col = divmod(i, 2)
        cell = tk.Frame(center_frame, padx=50, pady=30)
        cell.grid(row=row, column=col)
        tk.Button(cell, text=text, width=20, height=4, command=cmd, bg="#d3d3d3", relief="raised", borderwidth=2).pack()

    # 下部帯
    footer(root)

# ウィンドウ初期化
def clear_window():
    for widget in root.winfo_children():
        widget.destroy()

# アプリ起動処理
initialize_excel()
root = tk.Tk()
root.title("ドリンク原価計算アプリ")
root.geometry("1100x750")
show_top()
root.mainloop()
