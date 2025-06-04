# utils/excel_handler.py
import os
from openpyxl import Workbook, load_workbook
from datetime import datetime
from openpyxl import Workbook, load_workbook
from openpyxl.utils import get_column_letter
import os

def append_to_excel(file_path, sender_name, department, machine, timestamp, image_path=None):
    if os.path.exists(file_path):
        wb = load_workbook(file_path)
        ws = wb.active
    else:
        wb = Workbook()
        ws = wb.active
        ws.append(["Người gửi", "Bộ phận", "Máy", "Thời gian", "Ảnh"])

    row = [sender_name, department, machine, timestamp, image_path or ""]
    ws.append(row)
    wb.save(file_path)


def write_to_excel(file_path, user_id, department, machine, image_path):
    if not os.path.exists(file_path):
        wb = Workbook()
        ws = wb.active
        ws.append(["User ID", "Department", "Machine", "Date", "Image Path"])
    else:
        wb = load_workbook(file_path)
        ws = wb.active

    ws.append([
        user_id,
        department,
        machine,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        image_path
    ])

    wb.save(file_path)
