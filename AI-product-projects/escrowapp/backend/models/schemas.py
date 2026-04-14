"""
models/schemas.py
-----------------
Pydantic v2 schemas for request validation and response serialization.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from enum import Enum


# ── Enums ────────────────────────────────────────────────────

class UserRole(str, Enum):
    customer = "customer"
    seller   = "seller"

class OrderStatus(str, Enum):
    pending   = "pending"
    in_escrow = "in_escrow"
    delivered = "delivered"
    completed = "completed"
    disputed  = "disputed"

class EscrowStatus(str, Enum):
    held     = "held"
    released = "released"
    refunded = "refunded"

class TransactionType(str, Enum):
    deposit = "deposit"
    release = "release"
    refund  = "refund"


# ── Auth Schemas ─────────────────────────────────────────────

class SignupRequest(BaseModel):
    name:     str       = Field(..., min_length=2, max_length=255)
    email:    EmailStr
    password: str       = Field(..., min_length=6, max_length=100)
    role:     UserRole

class LoginRequest(BaseModel):
    email:    EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type:   str = "bearer"
    user: dict


# ── Order Schemas ────────────────────────────────────────────

class CreateOrderRequest(BaseModel):
    seller_id:   UUID
    amount:      float = Field(..., gt=0)
    description: Optional[str] = None

class OrderResponse(BaseModel):
    id:          str
    customer_id: str
    seller_id:   str
    amount:      float
    description: Optional[str]
    status:      str
    created_at:  datetime
    updated_at:  datetime


# ── Escrow Schemas ───────────────────────────────────────────

class DepositRequest(BaseModel):
    order_id: UUID

class ReleaseRequest(BaseModel):
    order_id: UUID

class DisputeRequest(BaseModel):
    order_id: UUID

class RefundRequest(BaseModel):
    order_id: UUID

class EscrowResponse(BaseModel):
    id:          str
    order_id:    str
    amount:      float
    status:      str
    held_at:     Optional[datetime]
    released_at: Optional[datetime]
    created_at:  datetime


# ── Transaction Schemas ──────────────────────────────────────

class TransactionResponse(BaseModel):
    id:        str
    order_id:  str
    type:      str
    amount:    float
    note:      Optional[str]
    timestamp: datetime


# ── Dashboard Schemas ────────────────────────────────────────

class DashboardAnalytics(BaseModel):
    total_orders:      int
    total_escrow_held: float
    completed_orders:  int
    disputed_orders:   int
