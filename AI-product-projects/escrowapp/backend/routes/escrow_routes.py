"""
routes/escrow_routes.py
-------------------------
Escrow lifecycle endpoints:
  POST /escrow/deposit         - Customer funds escrow
  POST /escrow/release         - Customer confirms delivery → releases funds
  POST /escrow/dispute         - Customer raises dispute
  POST /escrow/refund          - Customer requests refund (on disputed orders)
  GET  /escrow/transactions/{order_id}  - Transaction history
"""

from fastapi import APIRouter, Depends
from models.schemas import DepositRequest, ReleaseRequest, DisputeRequest, RefundRequest
from controllers.escrow_controller import (
    deposit_to_escrow, release_escrow, raise_dispute,
    refund_escrow, get_transactions
)
from middleware.auth import get_current_user, require_role

router = APIRouter(prefix="/escrow", tags=["Escrow"])


@router.post("/deposit", summary="Deposit funds into escrow (customer)")
def deposit(
    data: DepositRequest,
    current_user: dict = Depends(require_role("customer"))
):
    return deposit_to_escrow(str(data.order_id), current_user)


@router.post("/release", summary="Confirm delivery and release funds (customer)")
def release(
    data: ReleaseRequest,
    current_user: dict = Depends(require_role("customer"))
):
    return release_escrow(str(data.order_id), current_user)


@router.post("/dispute", summary="Raise a dispute on an order (customer)")
def dispute(
    data: DisputeRequest,
    current_user: dict = Depends(require_role("customer"))
):
    return raise_dispute(str(data.order_id), current_user)


@router.post("/refund", summary="Request refund (customer, disputed orders only)")
def refund(
    data: RefundRequest,
    current_user: dict = Depends(require_role("customer"))
):
    return refund_escrow(str(data.order_id), current_user)


@router.get("/transactions/{order_id}", summary="Get transaction history for an order")
def transactions(order_id: str, current_user: dict = Depends(get_current_user)):
    return get_transactions(order_id, current_user)
