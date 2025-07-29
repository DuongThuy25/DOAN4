import pyodbc

def get_db_connection():
    return pyodbc.connect(
        r'DRIVER={ODBC Driver 17 for SQL Server};'
        r'SERVER=ADMIN-PC\DUONGTHUY;'
        r'DATABASE=Hatcafe_API;'
        r'Trusted_Connection=yes;'
    )
