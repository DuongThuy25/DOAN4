from utils.db_connection import get_db_connection
from typing import Optional, Dict, List

def get_user_info_by_id(user_id: int) -> Optional[Dict]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT user_id, username, phone_number, email
        FROM Users
        WHERE user_id = ?
    """, (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"user_id": row[0], "username": row[1], "phone_number": row[2], "email": row[3]}
    return None



def clear_orders_by_user_id(user_id: int, only_pending: bool = True, ui_status: str = None):

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # nếu có UI status, map sang DB status
        db_status = None
        if ui_status:
            db_status = STATUS_MAP.get(ui_status.lower(), ui_status.lower())

        if only_pending:
            status_condition = "AND LOWER(status)=?" if db_status is None else "AND LOWER(status)=?"
            params = (user_id, db_status if db_status else "pending")
        else:
            status_condition = ""
            params = (user_id,) if db_status is None else (user_id, db_status)

        # xóa Payments
        cur.execute(f"""
            DELETE FROM Payments 
            WHERE order_id IN (
                SELECT order_id FROM Orders WHERE user_id=? {status_condition}
            )
        """, params)

        # xóa OrderDetails
        cur.execute(f"""
            DELETE FROM OrderDetails
            WHERE order_id IN (
                SELECT order_id FROM Orders WHERE user_id=? {status_condition}
            )
        """, params)

        # xóa Orders
        cur.execute(f"""
            DELETE FROM Orders
            WHERE user_id=? {status_condition}
        """, params)

        conn.commit()
        print(f"[DEBUG] Cleared orders for user_id={user_id}, only_pending={only_pending}, ui_status={ui_status}")
    except Exception as ex:
        conn.rollback()
        print(f"[ERROR] clear_orders_by_user_id failed: {ex}")
        raise
    finally:
        conn.close()

def get_order_details_by_order_id(order_id: int) -> List[Dict]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.product_name, od.quantity, od.price
        FROM OrderDetails od
        JOIN Products p ON od.product_id = p.product_id
        WHERE od.order_id = ?
    """, (order_id,))
    rows = cursor.fetchall()
    conn.close()
    results = []
    for r in rows:
        price_val = int("".join(ch for ch in str(r[2] or "") if ch.isdigit())) if r[2] else 0
        results.append({"name": r[0], "qty": int(r[1]), "price": price_val})
    return sorted(results, key=lambda x: x["name"])

def get_latest_order_from_db(user_id: int) -> Optional[Dict]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT TOP 1 order_id, order_date, total_amount, status
        FROM Orders
        WHERE user_id = ?
        ORDER BY order_id DESC
    """, (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"order_id": str(row[0]), "order_date": str(row[1]), "total_amount": str(row[2]), "status": row[3]}
    return None
