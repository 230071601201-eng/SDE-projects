"""
controllers/order_controller.py - SQLite version
"""
from fastapi import HTTPException
from models.schemas import CreateOrderRequest
from config.database import get_db
import uuid, logging

logger = logging.getLogger(__name__)

def create_order(data: CreateOrderRequest, current_user: dict):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE id=? AND role='seller'", (str(data.seller_id),))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Seller not found")
        if str(data.seller_id) == current_user["id"]:
            raise HTTPException(status_code=400, detail="Cannot order from yourself")
        oid = str(uuid.uuid4())
        cur.execute(
            "INSERT INTO orders (id,customer_id,seller_id,amount,description) VALUES (?,?,?,?,?)",
            (oid, current_user["id"], str(data.seller_id), data.amount, data.description)
        )
        cur.execute("SELECT * FROM orders WHERE id=?", (oid,))
        return cur.fetchone()

def get_orders_for_user(current_user: dict):
    with get_db() as conn:
        cur = conn.cursor()
        if current_user["role"] == "customer":
            cur.execute("""
                SELECT o.*,u.name AS seller_name,u.email AS seller_email
                FROM orders o JOIN users u ON u.id=o.seller_id
                WHERE o.customer_id=? ORDER BY o.created_at DESC
            """, (current_user["id"],))
        else:
            cur.execute("""
                SELECT o.*,u.name AS customer_name,u.email AS customer_email
                FROM orders o JOIN users u ON u.id=o.customer_id
                WHERE o.seller_id=? ORDER BY o.created_at DESC
            """, (current_user["id"],))
        return cur.fetchall()

def get_order_by_id(order_id: str, current_user: dict):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT o.*,c.name AS customer_name,s.name AS seller_name
            FROM orders o JOIN users c ON c.id=o.customer_id JOIN users s ON s.id=o.seller_id
            WHERE o.id=?
        """, (order_id,))
        order = cur.fetchone()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if current_user["id"] not in (order["customer_id"], order["seller_id"]):
        raise HTTPException(status_code=403, detail="Access denied")
    return order

def mark_delivered(order_id: str, current_user: dict):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM orders WHERE id=?", (order_id,))
        order = cur.fetchone()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        if order["seller_id"] != current_user["id"]:
            raise HTTPException(status_code=403, detail="Only assigned seller can mark delivery")
        if order["status"] != "in_escrow":
            raise HTTPException(status_code=400, detail=f"Cannot deliver. Status: {order['status']}")
        cur.execute("UPDATE orders SET status='delivered',updated_at=datetime('now') WHERE id=?", (order_id,))
        cur.execute("SELECT * FROM orders WHERE id=?", (order_id,))
        return cur.fetchone()

def get_dashboard_analytics(current_user: dict):
    uid = current_user["id"]
    field = "customer_id" if current_user["role"] == "customer" else "seller_id"
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(f"SELECT COUNT(*) as c FROM orders WHERE {field}=?", (uid,))
        total = cur.fetchone()["c"]
        cur.execute(f"SELECT COUNT(*) as c FROM orders WHERE {field}=? AND status='completed'", (uid,))
        completed = cur.fetchone()["c"]
        cur.execute(f"SELECT COUNT(*) as c FROM orders WHERE {field}=? AND status='disputed'", (uid,))
        disputed = cur.fetchone()["c"]
        cur.execute(f"""
            SELECT COALESCE(SUM(e.amount),0) as h FROM escrow e
            JOIN orders o ON o.id=e.order_id
            WHERE o.{field}=? AND e.status='held'
        """, (uid,))
        held = cur.fetchone()["h"]
    return {"total_orders": total, "completed_orders": completed, "disputed_orders": disputed, "total_escrow_held": float(held)}
