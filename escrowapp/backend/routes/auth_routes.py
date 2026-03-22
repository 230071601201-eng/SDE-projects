"""
routes/auth_routes.py
-----------------------
Authentication endpoints:
  POST /signup
  POST /login
  GET  /sellers  (for customer to pick a seller when creating order)
  GET  /me       (current user profile)
"""

from fastapi import APIRouter, Depends
from models.schemas import SignupRequest, LoginRequest
from controllers.auth_controller import signup, login, list_sellers
from middleware.auth import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", summary="Register a new user")
def signup_route(data: SignupRequest):
    return signup(data)


@router.post("/login", summary="Login and receive JWT")
def login_route(data: LoginRequest):
    return login(data)


@router.get("/me", summary="Get current user profile")
def me(current_user: dict = Depends(get_current_user)):
    return current_user


@router.get("/sellers", summary="List all sellers (for order creation)")
def get_sellers(current_user: dict = Depends(get_current_user)):
    return list_sellers()
