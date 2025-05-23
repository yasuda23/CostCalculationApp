import tkinter as tk
from excel_utils import save_material

def show_material_input(root, show_top, header, footer):
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
    header("材料登録")

    label_frame = tk.Frame(root)
    label_frame.pack(pady=2)
    tk.Label(label_frame, text="材料名", width=20, anchor="w").pack(side=tk.LEFT, padx=2)
    tk.Label(label_frame, text="量（ml, g）", width=12, anchor="w").pack(side=tk.LEFT, padx=2)
    tk.Label(label_frame, text="価格（円）", width=12, anchor="w").pack(side=tk.LEFT, padx=2)
    tk.Label(label_frame, text="税（％）", width=12, anchor="w").pack(side=tk.LEFT, padx=2)

    entry_frame = tk.Frame(root)
    entry_frame.pack(pady=5)
    entry_rows = []

    def add_row():
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
        entry_rows.append(row)

    add_row()

    plus_btn = tk.Button(root, text="+", font=("Arial", 14, "bold"), width=3, command=add_row)
    plus_btn.pack(pady=10)

    msg_var = tk.StringVar()
    msg_label = tk.Label(root, textvariable=msg_var, fg="red", font=("Arial", 12, "bold"))
    msg_label.pack(pady=10)

    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=20)

    def register():
        registered = []
        for row in entry_rows:
            name = row['name'].get()
            amount = row['amount'].get()
            price = row['price'].get()
            tax = row['tax'].get()
            if name and amount and price and tax:
                save_material(name, amount, price, tax)
                registered.append(name)
                row['total'].config(state='normal')
                row['total'].delete(0, tk.END)
                row['total'].insert(0, calc_total(price, tax))
                row['total'].config(state='readonly')
        if registered:
            msg_var.set(f'"{', '.join(registered)}"をExcelへ登録しました')
        else:
            msg_var.set("")

    tk.Button(btn_frame, text="戻る", width=10, command=show_top).pack(side=tk.LEFT, padx=10)
    tk.Button(btn_frame, text="登録", width=10, command=register).pack(side=tk.LEFT, padx=10)

    footer() 