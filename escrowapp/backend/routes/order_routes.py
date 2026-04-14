"""
routes/order_routes.py
------------------------
Order management endpoints:
  POST /orders                   - Customer creates order
  GET  /orders                   - List user's orders
  GET  /orders/{id}              - Get order details
  POST /orders/{id}/deliver      - Seller marks as delivered
  GET  /orders/analytics         - Dashboard analytics
"""

from fastapi import APIRouter, Depends
from models.schemas import CreateOrderRequest
from controllers.order_controller import (
    create_order, get_orders_for_user, get_order_by_id,
    mark_delivered, get_dashboard_analytics
)
from middleware.auth import get_current_user, require_role

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("", summary="Create a new order (customer only)")
def create_order_route(
    data: CreateOrderRequest,
    current_user: dict = Depends(require_role("customer"))
):
    return create_order(data, current_user)


@router.get("/analytics", summary="Dashboard analytics")
def analytics(current_user: dict = Depends(get_current_user)):
    return get_dashboard_analytics(current_user)


@router.get("", summary="List orders for current user")
def list_orders(current_user: dict = Depends(get_current_user)):
    return get_orders_for_user(current_user)


@router.get("/{order_id}", summary="Get order by ID")
def get_order(order_id: str, current_user: dict = Depends(get_current_user)):
    return get_order_by_id(order_id, current_user)


@router.post("/{order_id}/deliver", summary="Seller marks order as delivered")
def deliver_order(
    order_id: str,
    current_user: dict = Depends(require_role("seller"))
):
    return mark_delivered(order_id, current_user)
