import os
import pandas as pd

def write_test_results_excel(data_list, filename="test_results.xlsx", sheet_name="Test Results"):
    report_dir = "report"
    file_path = os.path.join(report_dir, filename)
    os.makedirs(report_dir, exist_ok=True)

    df = pd.DataFrame(data_list)
    df.to_excel(file_path, index=False, sheet_name=sheet_name)
