from utils.db_connection import get_db_connection

def query_products_by_keyword(keyword=None):
    conn = get_db_connection()
    cursor = conn.cursor()

    if keyword:
        sql = "SELECT product_name FROM Products WHERE product_name LIKE ?"
        cursor.execute(sql, (f"%{keyword}%",))
    else:
        sql = "SELECT product_name FROM Products"
        cursor.execute(sql)

    result = [row.product_name for row in cursor.fetchall()]
    conn.close()
    return result

