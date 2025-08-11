import tkinter as tk
from tkinter import ttk # Comboboxのためにttkをインポート
from tkinter import messagebox
from excel_utils import get_materials, get_material_unit_cost, save_recipe as save_recipe_to_excel # 材料リスト取得と単価取得のためにインポート

is_saving = False # 登録処理中フラグ

def show_recipe_input(root, show_top, header, footer):
    def clear_window():
        for widget in root.winfo_children():
            widget.destroy()

    clear_window()
    header(root, "レシピ登録")

    # レシピ名入力
    recipe_name_frame = tk.Frame(root)
    recipe_name_frame.pack(pady=10)
    tk.Label(recipe_name_frame, text="レシピ名:", width=15, anchor="w").pack(side=tk.LEFT)
    recipe_name_entry = tk.Entry(recipe_name_frame, width=40)
    recipe_name_entry.pack(side=tk.LEFT)

    # 材料リストのヘッダー
    material_header_frame = tk.Frame(root)
    material_header_frame.pack(pady=5)
    tk.Label(material_header_frame, text="材料選択", width=20, anchor="w").pack(side=tk.LEFT, padx=5)
    tk.Label(material_header_frame, text="量 (ml, g)", width=12, anchor="w").pack(side=tk.LEFT, padx=5)
    tk.Label(material_header_frame, text="材料原価", width=12, anchor="w").pack(side=tk.LEFT, padx=5)

    # 材料入力行を保持するフレーム
    material_rows_frame = tk.Frame(root)
    material_rows_frame.pack(pady=5)

    # 材料行を追加する関数
    material_rows = [] # 各材料行のエントリーとコンボボックスを保持
    material_options = [mat[0] for mat in get_materials()] # Excelから材料名を取得

    def update_total_cost():
        total = 0
        for row in material_rows:
            try:
                cost = float(row['cost_display'].get() or 0) # 材料原価を取得
                total += cost
            except ValueError:
                pass # 数値変換できない場合はスキップ
        total_cost_display.config(state='normal')
        total_cost_display.delete(0, tk.END)
        total_cost_display.insert(0, f"{total:.2f}") # 合計金額を表示
        total_cost_display.config(state='readonly')

    def update_material_cost(row):
        material_name = row['material_var'].get()
        amount_str = row['amount_entry'].get()
        cost = 0
        if material_name != "材料を選択" and amount_str:
            try:
                amount = float(amount_str)
                unit_cost = get_material_unit_cost(material_name)
                cost = amount * unit_cost
            except ValueError:
                pass # 量が数値でない場合は計算しない
        row['cost_display'].config(state='normal')
        row['cost_display'].delete(0, tk.END)
        row['cost_display'].insert(0, f"{cost:.2f}")
        row['cost_display'].config(state='readonly')
        update_total_cost() # 合計金額を更新

    def add_material_row():
        row_frame = tk.Frame(material_rows_frame)
        row_frame.pack(pady=2)

        # 材料選択 (プルダウン)
        material_var = tk.StringVar()
        material_combobox = ttk.Combobox(row_frame, textvariable=material_var, values=material_options, width=20)
        material_combobox.pack(side=tk.LEFT, padx=5)
        material_combobox.set("材料を選択") # 初期表示

        # 量入力
        amount_entry = tk.Entry(row_frame, width=15)
        amount_entry.pack(side=tk.LEFT, padx=5)

        # 材料原価表示 (計算結果)
        cost_display = tk.Entry(row_frame, width=15, state='readonly')
        cost_display.pack(side=tk.LEFT, padx=5)

        # 削除ボタン (後で画像に置き換える)
        delete_btn = tk.Button(row_frame, text="×", fg="red", command=lambda: remove_material_row(row_frame, new_row))
        delete_btn.pack(side=tk.LEFT, padx=5)

        new_row = {'frame': row_frame, 'material_var': material_var, 'amount_entry': amount_entry, 'cost_display': cost_display}
        material_rows.append(new_row)

        # 材料選択と量入力の変更を監視
        material_combobox.bind('<<ComboboxSelected>>', lambda event=None: update_material_cost(new_row))
        amount_entry.bind('<KeyRelease>', lambda event=None: update_material_cost(new_row))

    def remove_material_row(row_frame, row_data):
        row_frame.destroy()
        material_rows.remove(row_data)
        update_total_cost()

    # 最初の材料行を追加
    add_material_row()

    # 行追加ボタン
    add_row_btn = tk.Button(root, text="+", font=("Arial", 14, "bold"), command=add_material_row)
    add_row_btn.pack(pady=10)

    # 合計金額表示
    total_cost_frame = tk.Frame(root)
    total_cost_frame.pack(pady=10)
    tk.Label(total_cost_frame, text="合計金額 (原価):", width=20, anchor="e").pack(side=tk.LEFT)
    total_cost_display = tk.Entry(total_cost_frame, width=20, state='readonly')
    total_cost_display.pack(side=tk.LEFT)

    # ボタンフレーム
    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=20)

    def save_recipe():
        global is_saving
        if is_saving:
            return # 登録処理中の場合は何もしない

        # 登録ボタンを無効化
        register_btn.config(state='disabled')
        is_saving = True # 登録処理開始

        # 登録確認ダイアログを表示
        confirm = messagebox.askyesno("確認", "本当にこのレシピを登録しますか？")

        # 「いいえ」が選択された場合、処理を中断
        if not confirm:
            register_btn.config(state='normal') # ボタンを再度有効化
            is_saving = False # フラグを戻す
            return

        # レシピ名、材料、量、合計原価をExcelに保存
        recipe_name = recipe_name_entry.get()
        if not recipe_name:
            messagebox.showwarning("警告", "レシピ名を入力してください")
            # ボタンとフラグを戻す
            register_btn.config(state='normal')
            is_saving = False
            return

        materials_to_save = []
        for row in material_rows:
            material_name = row['material_var'].get()
            amount = row['amount_entry'].get()
            if material_name != "材料を選択" and amount:
                materials_to_save.append({'material_name': material_name, 'amount': amount})

        if not materials_to_save:
            messagebox.showwarning("警告", "材料を一つ以上追加して入力してください")
            # ボタンとフラグを戻す
            register_btn.config(state='normal')
            is_saving = False
            return

        try:
            total_cost = float(total_cost_display.get())
        except ValueError:
            total_cost = 0

        try:
            save_recipe_to_excel(recipe_name, materials_to_save, total_cost)
            msg_var.set(f'レシピ "{recipe_name}" をExcelへ登録しました')

            # 登録成功後、入力フィールドをクリア
            recipe_name_entry.delete(0, tk.END)
            # 既存の材料行をすべて削除
            for row_data in material_rows:
                row_data['frame'].destroy()
            material_rows.clear() # リストもクリア
            # 新しい空の材料行を一つ追加
            add_material_row()

            # 合計金額表示をクリア
            total_cost_display.config(state='normal')
            total_cost_display.delete(0, tk.END)
            total_cost_display.config(state='readonly')

            # ボタンとフラグを戻す
            register_btn.config(state='normal')
            is_saving = False

            # 必要であれば、ここで show_top() を呼び出してトップ画面に戻る
            # show_top()

        except Exception as e:
            # 登録失敗時
            messagebox.showerror("登録エラー", f"レシピの登録中にエラーが発生しました:\n{e}")
            msg_var.set(f'レシピ "{recipe_name}" の登録に失敗しました')
            # 登録ボタンを再度有効化
            register_btn.config(state='normal')
            is_saving = False # 登録処理終了

    tk.Button(btn_frame, text="戻る", width=10, command=show_top).pack(side=tk.LEFT, padx=10)
    # 定義済みの登録ボタンにコマンドを設定し配置
    register_btn = tk.Button(btn_frame, text="登録", width=10, command=save_recipe)
    register_btn.pack(side=tk.LEFT, padx=10)

    # メッセージ表示
    msg_var = tk.StringVar()
    msg_label = tk.Label(root, textvariable=msg_var, fg="red", font=("Arial", 12, "bold"))
    msg_label.pack(pady=10)

    footer(root)
