import openpyxl
from openpyxl.styles import Font
import os

EXCEL_FILE = "recipe.xlsx"

def initialize_excel():
    if not os.path.exists(EXCEL_FILE):
        wb = openpyxl.Workbook()
        sheet = wb.active
        sheet.title = "材料"
        sheet["A1"] = "材料名"
        sheet["B1"] = "量"
        sheet["C1"] = "価格"
        sheet["D1"] = "税率"
        bold_font = Font(bold=True)
        for col in ["A1", "B1", "C1", "D1"]:
            sheet[col].font = bold_font
        wb.create_sheet("レシピ")
        wb.save(EXCEL_FILE)

def save_material(name, amount, price, tax):
    wb = openpyxl.load_workbook(EXCEL_FILE)
    sheet = wb["材料"]
    sheet.append([name, amount, price, tax])
    wb.save(EXCEL_FILE)

def get_materials():
    wb = openpyxl.load_workbook(EXCEL_FILE)
    sheet = wb["材料"]
    return list(sheet.iter_rows(min_row=2, values_only=True))

def update_materials(data):
    wb = openpyxl.load_workbook(EXCEL_FILE)
    sheet = wb["材料"]
    sheet.delete_rows(2, sheet.max_row)
    for row in data:
        sheet.append(row)
    wb.save(EXCEL_FILE) 