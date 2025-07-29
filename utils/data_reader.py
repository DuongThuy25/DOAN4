import os
import csv

def read_csv_data(file_name):
    # Lấy đường dẫn tuyệt đối đến thư mục gốc dự án
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(project_dir, file_name)

    with open(file_path, newline='', encoding='utf-8') as f:
        return list(csv.reader(f))[1:]  # Bỏ dòng header
