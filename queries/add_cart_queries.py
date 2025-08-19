from utils.db_connection import get_db_connection
from typing import List, Dict

def get_user_id_by_username(username: str) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM Users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    if row:
        print(f"[DEBUG] User '{username}' có user_id = {row.user_id}")
        return row.user_id
    else:
        raise ValueError(f"Không tìm thấy user: {username}")

def query_cart_items_by_user(user_id: int) -> List[Dict]:
    conn = get_db_connection()
    cursor = conn.cursor()

    sql = """
    SELECT
        p.product_name AS name,
        (p.price * c.quantity) AS price,
        c.quantity AS qty
    FROM Cart c
    JOIN Products p ON c.product_id = p.product_id
    WHERE c.user_id = ?
    ORDER BY p.product_name
    """
    cursor.execute(sql, (user_id,))
    results = [
        {"name": row.name, "price": int(row.price), "qty": row.qty}
        for row in cursor.fetchall()
    ]
    conn.close()
    print(f"[DEBUG] DB cart items for user_id={user_id}: {results}")
    return results

def clear_cart_by_user_id(user_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Cart WHERE user_id = ?", (user_id,))
    conn.commit()
    cursor.close()
    conn.close()
    print(f"[DEBUG] Đã clear giỏ hàng cho user_id={user_id}")
