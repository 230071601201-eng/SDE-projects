"""
controllers/auth_controller.py - SQLite version
"""
from fastapi import HTTPException
from passlib.context import CryptContext
from models.schemas import SignupRequest, LoginRequest
from config.database import get_db
from middleware.auth import create_access_token
import logging, uuid

logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(plain): return pwd_context.hash(plain[:72])
def verify_password(plain, hashed): return pwd_context.verify(plain[:72], hashed)

def signup(data: SignupRequest):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE email=?", (data.email,))
        if cur.fetchone():
            raise HTTPException(status_code=409, detail="Email already registered")
        uid = str(uuid.uuid4())
        cur.execute(
            "INSERT INTO users (id,name,email,password,role) VALUES (?,?,?,?,?)",
            (uid, data.name, data.email, hash_password(data.password), data.role.value)
        )
        cur.execute("SELECT id,name,email,role FROM users WHERE id=?", (uid,))
        user = cur.fetchone()
    token = create_access_token({"sub": user["id"], "role": user["role"]})
    return {"access_token": token, "token_type": "bearer", "user": user}

def login(data: LoginRequest):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id,name,email,password,role FROM users WHERE email=?", (data.email,))
        user = cur.fetchone()
    if not user or not verify_password(data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token({"sub": user["id"], "role": user["role"]})
    return {"access_token": token, "token_type": "bearer",
            "user": {"id": user["id"], "name": user["name"], "email": user["email"], "role": user["role"]}}

def get_user_by_id(user_id: str):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id,name,email,role,created_at FROM users WHERE id=?", (user_id,))
        return cur.fetchone()

def list_sellers():
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id,name,email FROM users WHERE role='seller' ORDER BY name")
        return cur.fetchall()
