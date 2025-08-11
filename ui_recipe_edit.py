import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from excel_utils import get_materials, get_material_unit_cost, update_recipe # get_materials, get_material_unit_cost, update_recipe をインポート
from PIL import Image, ImageTk
import os # 画像ファイル存在チェックのためにインポート

def show_recipe_edit(root, show_top, header, footer, recipe_data): # 編集するレシピデータを受け取る
    def clear_window():
        for widget in root.winfo_children():
            widget.destroy()

    clear_window()
    header(root, "レシピ編集")

    # レシピ名入力 (編集可能)
    recipe_name_frame = tk.Frame(root)
    recipe_name_frame.pack(pady=10)
    tk.Label(recipe_name_frame, text="レシピ名:", width=10, anchor="w").pack(side=tk.LEFT)
    recipe_name_entry = tk.Entry(recipe_name_frame, width=30)
    recipe_name_entry.pack(side=tk.LEFT, padx=5)
    recipe_name_entry.insert(0, recipe_data.get('name', '')) # 既存のレシピ名を表示

    # 材料リストのヘッダー
    material_header_frame = tk.Frame(root)
    material_header_frame.pack(pady=5)
    # ヘッダーの幅とパディングを調整し、材料行と揃える
    tk.Label(material_header_frame, text="材料名", width=25, anchor="w").pack(side=tk.LEFT, padx=5)
    tk.Label(material_header_frame, text="量 (ml, g)", width=10, anchor="w").pack(side=tk.LEFT, padx=5)
    tk.Label(material_header_frame, text="材料原価", width=10, anchor="w").pack(side=tk.LEFT, padx=5)
    tk.Label(material_header_frame, text="削除", width=5, anchor="center").pack(side=tk.LEFT, padx=5)

    # 材料入力行を保持し、スクロール可能にするフレーム
    canvas = tk.Canvas(root)
    scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    # CanvasとScrollbarを一つのフレームに入れて配置
    # fill="both", expand=True で縦横に拡張させる
    scroll_area_frame = tk.Frame(root)
    scroll_area_frame.pack(pady=5, fill="both", expand=True)

    # canvas.pack(side="bottom", fill="both", expand=True)
    canvas.pack(side="top", expand=True)

    # 材料入力行を保持するフレーム (この中に材料行を追加)
    material_rows_frame = scrollable_frame

    # 材料行を保持するリスト
    material_rows = []
    
    # Excelから材料名リストを取得（新規行のプルダウン用）
    all_material_names = [mat[0] for mat in get_materials()] 

    # 合計金額を更新する関数
    def update_total_cost():
        total = 0
        for row in material_rows:
            try:
                # 材料原価は表示用Entryから取得
                cost = float(row['cost_display'].get() or 0)
                total += cost
            except ValueError:
                pass # 数値変換できない場合はスキップ
        # 合計金額表示Entryを更新
        total_cost_display.config(state='normal')
        total_cost_display.delete(0, tk.END)
        total_cost_display.insert(0, f"{total:.2f}") # 合計金額を表示
        total_cost_display.config(state='readonly')

    # 材料原価を計算・更新する関数 (既存行用 - 材料名は固定)
    def update_material_cost_existing(row):
        material_name = row['material_name'] # 辞書に保存された材料名を使用
        amount_str = row['amount_entry'].get()
        cost = 0
        if material_name and amount_str:
            try:
                amount = float(amount_str)
                unit_cost = get_material_unit_cost(material_name)
                cost = amount * unit_cost
            except (ValueError, TypeError): # 数値変換エラーやNoneTypeの場合
                cost = 0
            except Exception as e:
                print(f"Error calculating unit cost for {material_name}: {e}") # デバッグ用
                cost = 0

        row['cost_display'].config(state='normal')
        row['cost_display'].delete(0, tk.END)
        row['cost_display'].insert(0, f"{cost:.2f}")
        row['cost_display'].config(state='readonly')
        update_total_cost() # 合計金額を更新

    # 材料原価を計算・更新する関数 (新規行用 - 材料名はプルダウンから取得)
    def update_material_cost_new(row):
        material_name = row['material_var'].get()
        amount_str = row['amount_entry'].get()
        cost = 0
        # 「材料を選択」以外の有効な材料名と量が入力されているか確認
        if material_name and material_name != "材料を選択" and amount_str:
            try:
                amount = float(amount_str)
                unit_cost = get_material_unit_cost(material_name)
                cost = amount * unit_cost
            except (ValueError, TypeError): # 数値変換エラーやNoneTypeの場合
                cost = 0
            except Exception as e:
                print(f"Error calculating unit cost for {material_name}: {e}") # デバッグ用
                cost = 0

        row['cost_display'].config(state='normal')
        row['cost_display'].delete(0, tk.END)
        row['cost_display'].insert(0, f"{cost:.2f}")
        row['cost_display'].config(state='readonly')
        update_total_cost() # 合計金額を更新

    # 材料行を削除する関数
    def remove_material_row(row_frame, row_data):
        row_frame.destroy()
        material_rows.remove(row_data)
        update_total_cost() # 合計金額を再計算

    # 既存の材料行を追加する関数 (編集画面用)
    def add_existing_material_row(material):
        row_frame = tk.Frame(material_rows_frame)
        row_frame.pack(pady=2)

        # 材料名表示 (Label)
        tk.Label(row_frame, text=material.get('name', ''), width=25, anchor="w").pack(side=tk.LEFT, padx=5)

        # 量入力 (Entry) - 既存の量があれば表示
        amount_entry = tk.Entry(row_frame, width=10)
        amount_entry.pack(side=tk.LEFT, padx=5)
        amount_entry.insert(0, material.get('amount', ''))

        # 材料原価表示 (Entry) - 既存の原価があれば表示 (readonly)
        cost_display = tk.Entry(row_frame, width=10, state='readonly')
        cost_display.pack(side=tk.LEFT, padx=5)
        # 初期表示時に保存されている原価を表示（計算は量変更時のみ）
        initial_cost = material.get('cost', 0)
        cost_display.config(state='normal')
        cost_display.delete(0, tk.END)
        cost_display.insert(0, f"{float(initial_cost):.2f}" if initial_cost else "0.00")
        cost_display.config(state='readonly')

        # 削除ボタン (画像またはテキスト)
        delete_btn_image = None # 画像オブジェクトを保持する変数
        try:
            # 画像ファイルが存在するか確認
            if os.path.exists("images/delete.png"):
                delete_img_orig = Image.open("images/delete.png") # 削除アイコン
                delete_img = delete_img_orig.resize((20, 20))
                delete_btn_image = ImageTk.PhotoImage(delete_img)
                # widthとheightは画像サイズに合わせるかbd=0にする
                delete_btn = tk.Button(row_frame, image=delete_btn_image, command=lambda: remove_material_row(row_frame, new_row), width=20, height=20, bd=0)
                delete_btn.image = delete_btn_image # 画像が解放されないように参照を保持
            else:
                 # 画像ファイルがない場合はテキストボタンで代替
                delete_btn = tk.Button(row_frame, text="✕", fg="red", command=lambda: remove_material_row(row_frame, new_row), width=5) # 幅を調整
        except Exception as e:
            print(f"Error loading delete image: {e}") # 画像読み込みエラーを表示
            # 画像読み込み失敗時もテキストボタンで代替
            delete_btn = tk.Button(row_frame, text="✕", fg="red", command=lambda: remove_material_row(row_frame, new_row), width=5)
        delete_btn.pack(side=tk.LEFT, padx=5)

        # rowデータにウィジェットと材料名を保存
        new_row = {
            'frame': row_frame,
            'material_name': material.get('name', ''), # 既存行は材料名固定
            'amount_entry': amount_entry,
            'cost_display': cost_display
        }
        material_rows.append(new_row)

        # 量入力の変更を監視して原価と合計を更新
        amount_entry.bind('<KeyRelease>', lambda event=None: update_material_cost_existing(new_row))

        # 初期表示時の合計金額計算はループの後に行う

    # 新しい材料行を追加する関数 (プルダウン付き)
    def add_new_material_row():
        row_frame = tk.Frame(material_rows_frame)
        row_frame.pack(pady=2)

        # 材料選択 (プルダウン)
        material_var = tk.StringVar()
        # プルダウンの幅を調整し、材料名Labelと揃える
        material_combobox = ttk.Combobox(row_frame, textvariable=material_var, values=all_material_names, width=25)
        material_combobox.pack(side=tk.LEFT, padx=5)
        material_combobox.set("材料を選択") # 初期表示

        # 量入力 (Entry)
        amount_entry = tk.Entry(row_frame, width=10)
        amount_entry.pack(side=tk.LEFT, padx=5)

        # 材料原価表示 (Entry) - readonly
        cost_display = tk.Entry(row_frame, width=10, state='readonly')
        cost_display.pack(side=tk.LEFT, padx=5)

        # 削除ボタン (画像またはテキスト)
        delete_btn_image = None # 画像オブジェクトを保持する変数
        try:
             # 画像ファイルが存在するか確認
            if os.path.exists("images/delete.png"):
                delete_img_orig = Image.open("images/delete.png") # 削除アイコン
                delete_img = delete_img_orig.resize((20, 20))
                delete_btn_image = ImageTk.PhotoImage(delete_img)
                delete_btn = tk.Button(row_frame, image=delete_btn_image, command=lambda: remove_material_row(row_frame, new_row), width=20, height=20, bd=0)
                delete_btn.image = delete_btn_image # 画像が解放されないように参照を保持
            else:
                # 画像ファイルがない場合はテキストボタンで代替
                delete_btn = tk.Button(row_frame, text="✕", fg="red", command=lambda: remove_material_row(row_frame, new_row), width=5) # 幅を調整
        except Exception as e:
            print(f"Error loading delete image: {e}") # 画像読み込みエラーを表示
            # 画像読み込み失敗時もテキストボタンで代替
            delete_btn = tk.Button(row_frame, text="✕", fg="red", command=lambda: remove_material_row(row_frame, new_row), width=5)
        delete_btn.pack(side=tk.LEFT, padx=5)

        # rowデータにウィジェットとStringVar、新規行フラグを保存
        new_row = {
            'frame': row_frame,
            'material_var': material_var, # 新規行はStringVarで材料名を管理
            'amount_entry': amount_entry,
            'cost_display': cost_display,
            'is_new': True # 新規追加された行であることを示すフラグ
        }
        material_rows.append(new_row)

        # 材料選択と量入力の変更を監視して原価と合計を更新
        material_combobox.bind('<<ComboboxSelected>>', lambda event=None: update_material_cost_new(new_row))
        amount_entry.bind('<KeyRelease>', lambda event=None: update_material_cost_new(new_row))

    # 合計金額表示を材料行の処理の前に定義（NameError回避）
    total_cost_frame = tk.Frame(root)
    total_cost_frame.pack(pady=(0, 10))
    tk.Label(total_cost_frame, text="合計金額 (原価):", anchor="e").pack(side=tk.LEFT, padx=(0, 5))
    total_cost_display = tk.Entry(total_cost_frame, width=15, state='readonly') # 幅を調整
    total_cost_display.pack(side=tk.LEFT)

    # 既存のレシピに含まれる材料を表示
    for material in recipe_data.get('materials', []):
        add_existing_material_row(material)

    # 初期表示時の合計金額を計算
    update_total_cost()

    # 行追加ボタン
    add_row_btn_frame = tk.Frame(root) # "+"ボタン用のフレーム
    add_row_btn_frame.pack(pady=10)
    add_row_btn = tk.Button(add_row_btn_frame, text="+", font=("Arial", 14, "bold"), command=add_new_material_row)
    add_row_btn.pack()

    # ボタンフレーム
    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=20)

    # 更新ボタンのコマンド
    def update_recipe_command():
        # 更新確認ダイアログを表示
        confirm = messagebox.askyesno("確認", "本当にこのレシピを更新しますか？")

        # 「いいえ」が選択された場合、処理を中断
        if not confirm:
            return

        name = recipe_name_entry.get()
        if not name:
            messagebox.showwarning("警告", "レシピ名を入力してください")
            return

        materials_to_save = []
        for row in material_rows:
            material_name = ""
            amount = row['amount_entry'].get()
            cost = row['cost_display'].get()
            
            # 行の種類によって材料名の取得方法を変える
            if 'is_new' in row and row['is_new']:
                 material_name = row['material_var'].get()
            else:
                 material_name = row['material_name'] # 既存行は辞書に保存した名前

            # 材料名が選択/入力されており、量が入力されていれば保存対象とする
            if material_name and material_name != "材料を選択" and amount:
                 # 保存用にfloatに変換できるかチェック
                 try:
                     float(amount)
                     materials_to_save.append({'material_name': material_name, 'amount': amount})
                 except ValueError:
                     messagebox.showwarning("警告", f"材料 '{material_name}' の量が無効です。")
                     return # 無効なデータがあれば保存しない

        if not materials_to_save:
            messagebox.showwarning("警告", "材料を一つ以上追加して入力してください")
            return

        try:
            total_cost = float(total_cost_display.get())
        except ValueError:
            total_cost = 0 # 合計金額が数値でない場合は0とする

        try:
            # update_recipe 関数を呼び出し、古いレシピ名、新しいレシピ名、材料リスト、合計原価を渡す
            # recipe_data['name'] には編集前の元のレシピ名が入っている想定
            update_recipe(recipe_data.get('name', ''), name, materials_to_save, total_cost)
            msg_var.set(f'レシピ "{name}" を更新しました')
            # 更新成功後、レシピ一覧画面に戻る
            show_top()
        except Exception as e:
            messagebox.showerror("更新エラー", f"レシピの更新中にエラーが発生しました:\n{e}")
            msg_var.set(f'レシピ "{name}" の更新に失敗しました')

    # ボタン定義
    tk.Button(btn_frame, text="戻る", width=10, command=show_top).pack(side=tk.LEFT, padx=10)
    tk.Button(btn_frame, text="更新", width=10, command=update_recipe_command).pack(side=tk.LEFT, padx=10)

    # メッセージ表示
    msg_var = tk.StringVar()
    msg_label = tk.Label(root, textvariable=msg_var, fg="red", font=("Arial", 12, "bold"))
    msg_label.pack(pady=10)

    footer(root) 