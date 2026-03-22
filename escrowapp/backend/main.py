"""
main.py
--------
FastAPI application entry point.
- Initializes DB connection pool
- Registers all routers
- Configures CORS
- Provides health check endpoint
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from config.database import init_db, close_db
from config.settings import CORS_ORIGINS, APP_HOST, APP_PORT, DEBUG
from routes.auth_routes import router as auth_router
from routes.order_routes import router as order_router
from routes.escrow_routes import router as escrow_router

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
logger = logging.getLogger(__name__)


# ── Application Lifecycle ─────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    logger.info("🚀 Starting Escrow Payment System API...")
    init_db()
    yield
    logger.info("Shutting down...")
    close_db()


# ── FastAPI App ───────────────────────────────────────────────

app = FastAPI(
    title="Escrow Payment System API",
    description="""
## Escrow-Based Delivery Payment System

Secure payment flow:
1. Customer creates order → **pending**
2. Customer deposits to escrow → **in_escrow**
3. Seller marks delivered → **delivered**
4. Customer confirms → funds released → **completed**
5. Or customer disputes → **disputed** → refund

### Auth
All endpoints (except /auth/signup and /auth/login) require a Bearer JWT token.
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# ── CORS ──────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────

app.include_router(auth_router)
app.include_router(order_router)
app.include_router(escrow_router)


# ── Health Check ──────────────────────────────────────────────

@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "healthy",
        "service": "Escrow Payment API",
        "version": "1.0.0"
    }


@app.get("/", tags=["System"])
def root():
    return {
        "message": "Escrow Payment System API",
        "docs": "/docs",
        "health": "/health"
    }


# ── Run ───────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=APP_HOST,
        port=APP_PORT,
        reload=DEBUG,
        log_level="debug" if DEBUG else "info"
    )
