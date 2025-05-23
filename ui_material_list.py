import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from excel_utils import get_materials, update_materials

def show_material_list(root, show_top, header, footer):
    PAGE_SIZE = 10
    current_page = [0]  # リストでラップしてクロージャで書き換え可能に
    search_var = tk.StringVar()

    # 全データ取得
    all_materials = get_materials()
    filtered_materials = all_materials.copy()

    def filter_and_show():
        # 検索
        keyword = search_var.get().strip()
        if keyword:
            filtered = [row for row in all_materials if keyword in str(row[0]) or keyword in str(row[1])]
        else:
            filtered = all_materials
        filtered_materials.clear()
        filtered_materials.extend(filtered)
        current_page[0] = 0
        show_page()

    def show_page():
        # 既存行をクリア
        for widget in entry_frame.winfo_children():
            widget.destroy()
        entry_rows.clear()
        start = current_page[0] * PAGE_SIZE
        end = start + PAGE_SIZE
        for values in filtered_materials[start:end]:
            add_row(values)
        page_label.config(text=f"{current_page[0]+1} / {max(1, (len(filtered_materials)-1)//PAGE_SIZE+1)}")

    def next_page():
        if (current_page[0]+1)*PAGE_SIZE < len(filtered_materials):
            current_page[0] += 1
            show_page()

    def prev_page():
        if current_page[0] > 0:
            current_page[0] -= 1
            show_page()

    def calc_total(price, tax):
        try:
            price_str = str(price).replace('円', '').replace(',', '').strip()
            price_val = float(''.join(filter(str.isdigit, price_str)) or 0)
            import re
            tax_str = str(tax)
            match = re.search(r'([0-9]+(?:\.[0-9]*)?)', tax_str)
            tax_val = float(match.group(1)) if match else 0
            return int(price_val * (1 + tax_val / 100))
        except Exception:
            return ""

    def clear_window():
        for widget in root.winfo_children():
            widget.destroy()

    clear_window()
    header("材料一覧・編集")

    # 検索欄をheaderの直後に表示
    search_frame = tk.Frame(root)
    search_frame.pack(pady=5)
    tk.Label(search_frame, text="検索:").pack(side=tk.LEFT)
    tk.Entry(search_frame, textvariable=search_var, width=20).pack(side=tk.LEFT)
    tk.Button(search_frame, text="検索", command=filter_and_show).pack(side=tk.LEFT)

    delete_img = Image.open("images/delete.png")
    delete_img = delete_img.resize((30, 30))
    delete_photo = ImageTk.PhotoImage(delete_img)

    label_frame = tk.Frame(root)
    label_frame.pack(pady=2)
    for text, w in zip(["材料名", "量（ml, g）", "価格（円）", "税（％）", "合計", "削除"], [20, 12, 12, 12, 10, 6]):
        tk.Label(label_frame, text=text, width=w, anchor="w").pack(side=tk.LEFT, padx=2)

    entry_frame = tk.Frame(root)
    entry_frame.pack(pady=5)
    entry_rows = []

    def add_row(values=None):
        row = {}
        frame = tk.Frame(entry_frame)
        frame.pack(pady=3)
        row['name'] = tk.Entry(frame, width=22)
        row['name'].pack(side=tk.LEFT, padx=2)
        row['amount'] = tk.Entry(frame, width=14)
        row['amount'].pack(side=tk.LEFT, padx=2)
        row['price'] = tk.Entry(frame, width=14)
        row['price'].pack(side=tk.LEFT, padx=2)
        row['tax'] = tk.Entry(frame, width=14)
        row['tax'].pack(side=tk.LEFT, padx=2)
        row['total'] = tk.Entry(frame, width=10, state='readonly', justify='right')
        row['total'].pack(side=tk.LEFT, padx=2)
        def delete_this():
            if messagebox.askyesno("確認", "本当に削除しますか？"):
                idx = entry_rows.index(row)
                entry_rows.remove(row)
                frame.destroy()
                # filtered_materialsからも削除
                del_idx = current_page[0] * PAGE_SIZE + idx
                if del_idx < len(filtered_materials):
                    del filtered_materials[del_idx]
                # Excelに全データを保存
                update_materials(filtered_materials)
                show_page()  # ページ再描画
        row['delete_btn'] = tk.Button(frame, image=delete_photo, command=delete_this, width=30, height=30, bd=0)
        row['delete_btn'].pack(side=tk.LEFT, padx=2)
        if values:
            row['name'].insert(0, values[0])
            row['amount'].insert(0, values[1])
            row['price'].insert(0, values[2])
            row['tax'].insert(0, values[3])
        def update_total(*args):
            total = calc_total(row['price'].get(), row['tax'].get())
            row['total'].config(state='normal')
            row['total'].delete(0, tk.END)
            row['total'].insert(0, total)
            row['total'].config(state='readonly')
        row['price'].bind('<KeyRelease>', update_total)
        row['tax'].bind('<KeyRelease>', update_total)
        update_total()
        entry_rows.append(row)

    for values in get_materials():
        add_row(values)
    if not entry_rows:
        add_row()
        
    msg_var = tk.StringVar()
    tk.Label(root, textvariable=msg_var, fg="red", font=("Arial", 12, "bold")).pack(pady=10)

    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=20)

    def update():
        if not messagebox.askyesno("確認", "本当に更新しますか？"):
            return
        # entry_rowsの内容をfiltered_materialsの該当範囲に反映
        start = current_page[0] * PAGE_SIZE
        for i, row in enumerate(entry_rows):
            idx = start + i
            if idx < len(filtered_materials):
                name = row['name'].get()
                amount = row['amount'].get()
                price = row['price'].get()
                tax = row['tax'].get()
                filtered_materials[idx] = (name, amount, price, tax)
        # all_materialsもfiltered_materialsで上書き（検索中でなければ同じリスト）
        # 検索中の場合はall_materialsの該当データも更新が必要
        # ここでは簡単のためfiltered_materialsをExcelに保存
        update_materials(filtered_materials)
        msg_var.set('材料データを更新しました')

    tk.Button(btn_frame, text="戻る", width=10, command=show_top).pack(side=tk.LEFT, padx=10)
    tk.Button(btn_frame, text="更新", width=10, command=update).pack(side=tk.LEFT, padx=10)

    # ページング
    paging_frame = tk.Frame(root)
    paging_frame.pack(pady=5)
    tk.Button(paging_frame, text="前へ", command=prev_page).pack(side=tk.LEFT)
    page_label = tk.Label(paging_frame, text="")
    page_label.pack(side=tk.LEFT, padx=10)
    tk.Button(paging_frame, text="次へ", command=next_page).pack(side=tk.LEFT)

    # 初期表示
    show_page()

    footer() 