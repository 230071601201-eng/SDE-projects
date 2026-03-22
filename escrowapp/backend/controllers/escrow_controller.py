"""
controllers/escrow_controller.py - SQLite version
"""
from fastapi import HTTPException
from config.database import get_db
import uuid, logging

logger = logging.getLogger(__name__)

def _get_order(cur, order_id):
    cur.execute("SELECT * FROM orders WHERE id=?", (order_id,))
    order = cur.fetchone()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

def _get_escrow(cur, order_id):
    cur.execute("SELECT * FROM escrow WHERE order_id=?", (order_id,))
    return cur.fetchone()

def _log_tx(cur, order_id, tx_type, amount, note=None):
    cur.execute(
        "INSERT INTO transactions (id,order_id,type,amount,note) VALUES (?,?,?,?,?)",
        (str(uuid.uuid4()), order_id, tx_type, amount, note)
    )

def deposit_to_escrow(order_id: str, current_user: dict):
    with get_db() as conn:
        cur = conn.cursor()
        order = _get_order(cur, order_id)
        if order["customer_id"] != current_user["id"]:
            raise HTTPException(status_code=403, detail="Only the order's customer can deposit")
        if order["status"] != "pending":
            raise HTTPException(status_code=400, detail=f"Cannot deposit. Status: {order['status']}")
        if _get_escrow(cur, order_id):
            raise HTTPException(status_code=400, detail="Escrow already exists")
        amount = float(order["amount"])
        eid = str(uuid.uuid4())
        cur.execute("INSERT INTO escrow (id,order_id,amount) VALUES (?,?,?)", (eid, order_id, amount))
        cur.execute("UPDATE orders SET status='in_escrow',updated_at=datetime('now') WHERE id=?", (order_id,))
        _log_tx(cur, order_id, "deposit", amount, "Funds deposited into escrow")
    return {"message": "Funds deposited into escrow", "order_id": order_id, "amount": amount, "status": "held"}

def release_escrow(order_id: str, current_user: dict):
    with get_db() as conn:
        cur = conn.cursor()
        order = _get_order(cur, order_id)
        if order["customer_id"] != current_user["id"]:
            raise HTTPException(status_code=403, detail="Only the order's customer can release")
        if order["status"] != "delivered":
            raise HTTPException(status_code=400, detail=f"Cannot release. Status: {order['status']}")
        escrow = _get_escrow(cur, order_id)
        if not escrow or escrow["status"] != "held":
            raise HTTPException(status_code=400, detail="Escrow not in held state")
        amount = float(escrow["amount"])
        cur.execute("UPDATE escrow SET status='released',released_at=datetime('now') WHERE order_id=?", (order_id,))
        cur.execute("UPDATE orders SET status='completed',updated_at=datetime('now') WHERE id=?", (order_id,))
        _log_tx(cur, order_id, "release", amount, "Funds released to seller")
    return {"message": "Payment released to seller!", "order_id": order_id, "amount": amount, "status": "released"}

def raise_dispute(order_id: str, current_user: dict):
    with get_db() as conn:
        cur = conn.cursor()
        order = _get_order(cur, order_id)
        if order["customer_id"] != current_user["id"]:
            raise HTTPException(status_code=403, detail="Only the order's customer can dispute")
        if order["status"] not in ("in_escrow", "delivered"):
            raise HTTPException(status_code=400, detail=f"Cannot dispute. Status: {order['status']}")
        escrow = _get_escrow(cur, order_id)
        if not escrow or escrow["status"] != "held":
            raise HTTPException(status_code=400, detail="Escrow not in held state")
        cur.execute("UPDATE orders SET status='disputed',updated_at=datetime('now') WHERE id=?", (order_id,))
    return {"message": "Dispute raised. Funds held until resolved.", "order_id": order_id, "status": "disputed"}

def refund_escrow(order_id: str, current_user: dict):
    with get_db() as conn:
        cur = conn.cursor()
        order = _get_order(cur, order_id)
        if order["customer_id"] != current_user["id"]:
            raise HTTPException(status_code=403, detail="Only the order's customer can refund")
        if order["status"] != "disputed":
            raise HTTPException(status_code=400, detail=f"Cannot refund. Status: {order['status']}")
        escrow = _get_escrow(cur, order_id)
        if not escrow or escrow["status"] != "held":
            raise HTTPException(status_code=400, detail="Escrow not in held state")
        amount = float(escrow["amount"])
        cur.execute("UPDATE escrow SET status='refunded',released_at=datetime('now') WHERE order_id=?", (order_id,))
        cur.execute("UPDATE orders SET status='completed',updated_at=datetime('now') WHERE id=?", (order_id,))
        _log_tx(cur, order_id, "refund", amount, "Funds refunded to customer")
    return {"message": "Refund processed!", "order_id": order_id, "amount": amount, "status": "refunded"}

def get_transactions(order_id: str, current_user: dict):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT customer_id,seller_id FROM orders WHERE id=?", (order_id,))
        order = cur.fetchone()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        if current_user["id"] not in (order["customer_id"], order["seller_id"]):
            raise HTTPException(status_code=403, detail="Access denied")
        cur.execute("SELECT * FROM transactions WHERE order_id=? ORDER BY timestamp ASC", (order_id,))
        return cur.fetchall()
