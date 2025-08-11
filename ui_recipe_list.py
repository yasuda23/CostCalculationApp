import tkinter as tk
from tkinter import messagebox
# TODO: Excelからレシピデータを読み込む関数をインポート
from excel_utils import get_recipes, delete_recipe # レシピデータ読み込みのためにインポート
from PIL import Image, ImageTk

def show_recipe_list(root, show_top, header, footer):
    def clear_window():
        for widget in root.winfo_children():
            widget.destroy()

    clear_window()
    header(root, "レシピ一覧")

    # ヘッダーラベル
    header_frame = tk.Frame(root)
    header_frame.pack(pady=5)
    tk.Label(header_frame, text="レシピ名", width=30, anchor="w").pack(side=tk.LEFT, padx=5)
    tk.Label(header_frame, text="原価", width=15, anchor="w").pack(side=tk.LEFT, padx=5)
    tk.Label(header_frame, text="編集", width=8, anchor="center").pack(side=tk.LEFT, padx=5)
    tk.Label(header_frame, text="削除", width=8, anchor="center").pack(side=tk.LEFT, padx=5)

    # レシピリスト表示フレーム
    recipe_list_frame = tk.Frame(root)
    recipe_list_frame.pack(pady=5)

    # TODO: Excelから読み込んだレシピデータを表示するロジックを追加
    # 仮のデータ表示（実際はExcelから取得）
    recipes = get_recipes() # Excelからレシピデータを取得

    if not recipes:
        tk.Label(recipe_list_frame, text="登録されているレシピはありません", fg="gray").pack()

    # アイコン画像の読み込み
    try:
        edit_img_orig = Image.open("images/edit.png") # 編集アイコン
        edit_img = edit_img_orig.resize((20, 20))
        edit_photo = ImageTk.PhotoImage(edit_img)

        delete_img_orig = Image.open("images/delete.png") # 削除アイコン
        delete_img = delete_img_orig.resize((20, 20))
        delete_photo = ImageTk.PhotoImage(delete_img)
    except Exception:
        edit_photo = None
        delete_photo = None

    for recipe in recipes:
        recipe_name = recipe['name']
        cost = recipe['total_cost']
        row_frame = tk.Frame(recipe_list_frame)
        row_frame.pack(pady=2)

        # レシピ名表示
        tk.Label(row_frame, text=recipe_name, width=30, anchor="w").pack(side=tk.LEFT, padx=5)

        # 原価表示
        tk.Label(row_frame, text=f"{cost}", width=15, anchor="w").pack(side=tk.LEFT, padx=5)

        # 編集ボタン (画像またはテキスト)
        if edit_photo:
            edit_btn = tk.Button(row_frame, image=edit_photo, command=lambda r=recipe: edit_this_recipe(r), width=20, height=20, bd=0)
            edit_btn.image = edit_photo # 画像が解放されないように参照を保持
        else:
            edit_btn = tk.Button(row_frame, text="⚙", command=lambda r=recipe: edit_this_recipe(r), width=8)
        edit_btn.pack(side=tk.LEFT, padx=5)

        # 編集ボタンのコマンド
        def edit_this_recipe(recipe):
            from ui_recipe_edit import show_recipe_edit
            show_recipe_edit(root, show_top, header, footer, recipe)

        # 削除ボタン (画像またはテキスト)
        if delete_photo:
            delete_btn = tk.Button(row_frame, image=delete_photo, command=lambda rn=recipe_name, rf=row_frame: delete_this_recipe(rn, rf), width=20, height=20, bd=0)
            delete_btn.image = delete_photo # 画像が解放されないように参照を保持
        else:
            delete_btn = tk.Button(row_frame, text="✕", fg="red", command=lambda rn=recipe_name, rf=row_frame: delete_this_recipe(rn, rf), width=8)
        delete_btn.pack(side=tk.LEFT, padx=5)

        # 削除ボタンのコマンド
        def delete_this_recipe(recipe_name, row_frame):
            if messagebox.askyesno("確認", f"レシピ '{recipe_name}' を本当に削除しますか？"):
                from excel_utils import delete_recipe as delete_recipe_from_excel
                if delete_recipe_from_excel(recipe_name):
                    messagebox.showinfo("完了", f"レシピ '{recipe_name}' を削除しました")
                    row_frame.destroy() # 画面上の行を削除
                    # 画面全体を再描画 (Excelの変更を反映)
                    show_recipe_list(root, show_top, header, footer) # レシピ一覧画面を再表示
                else:
                    messagebox.showwarning("警告", f"レシピ '{recipe_name}' が見つかりませんでした")

    # 戻るボタン
    back_btn_frame = tk.Frame(root)
    back_btn_frame.pack(pady=20)
    tk.Button(back_btn_frame, text="戻る", width=10, command=show_top).pack()

    footer(root) 