# 🔒 EscrowPay — Secure Delivery Payment System

A full-stack escrow payment system where funds are locked until delivery is confirmed.  
**Stack:** Python (FastAPI) · PostgreSQL · Vanilla HTML/CSS/JS · JWT Auth

---

## 📁 Project Structure

```
escrow-system/
├── backend/
│   ├── main.py                    ← FastAPI entry point
│   ├── requirements.txt
│   ├── .env.example               ← copy to .env
│   ├── config/
│   │   ├── database.py            ← PostgreSQL connection pool
│   │   ├── settings.py            ← env vars
│   │   └── schema.sql             ← DB schema (run once)
│   ├── models/
│   │   └── schemas.py             ← Pydantic request/response models
│   ├── middleware/
│   │   └── auth.py                ← JWT + role-based access control
│   ├── controllers/
│   │   ├── auth_controller.py     ← signup, login, list sellers
│   │   ├── order_controller.py    ← CRUD + deliver + analytics
│   │   └── escrow_controller.py   ← deposit, release, dispute, refund
│   └── routes/
│       ├── auth_routes.py
│       ├── order_routes.py
│       └── escrow_routes.py
│
├── frontend/
│   ├── index.html                 ← Complete SPA (login/signup/dashboard)
│   └── services/
│       └── api.js                 ← API client (importable module)
│
└── EscrowPay.postman_collection.json
```

---

## ⚡ Step-by-Step Setup

### Step 1 — Prerequisites

Install these if not already present:

| Tool       | Version | Install |
|------------|---------|---------|
| Python     | 3.10+   | [python.org](https://python.org) |
| PostgreSQL | 14+     | [postgresql.org](https://postgresql.org) |
| pip        | latest  | bundled with Python |

---

### Step 2 — Database Setup

Open `psql` as the postgres superuser:

```bash
psql -U postgres
```

Then run:

```sql
-- Create the database
CREATE DATABASE escrow_db;

-- Connect to it
\c escrow_db

-- Run the schema (paste contents of backend/config/schema.sql)
-- Or from terminal:
```

From terminal (easier):

```bash
psql -U postgres -c "CREATE DATABASE escrow_db;"
psql -U postgres -d escrow_db -f backend/config/schema.sql
```

---

### Step 3 — Backend Setup

```bash
# Navigate to backend
cd escrow-system/backend

# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment config
cp .env.example .env
```

Now **edit `.env`** with your actual values:

```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/escrow_db
JWT_SECRET_KEY=pick-a-long-random-string-here
```

---

### Step 4 — Run the Backend

```bash
# From backend/ directory (with venv active)
python main.py
```

You should see:
```
✅ Database connection pool initialized
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Verify:** Open http://localhost:8000/docs — you should see the Swagger UI.

---

### Step 5 — Run the Frontend

The frontend is a single HTML file — no build step needed.

**Option A: Open directly**
```
Open frontend/index.html in your browser
```

**Option B: Serve with Python (recommended, avoids CORS quirks)**
```bash
cd escrow-system/frontend
python -m http.server 5500
# Open http://localhost:5500
```

**Option C: VS Code Live Server**
Right-click `frontend/index.html` → "Open with Live Server"

---

### Step 6 — Test the Flow

#### 6a. Create accounts

1. Open the app → click **"Create one"**
2. Sign up as a **Seller** (e.g. bob@example.com)
3. Sign out → Sign up as a **Customer** (e.g. alice@example.com)

#### 6b. Full escrow flow (as Customer)

| Step | Action | Status Change |
|------|--------|--------------|
| 1 | Create order, select Bob as seller | `pending` |
| 2 | Click **Pay** → deposit to escrow | `in_escrow` |
| 3 | Bob logs in → clicks **Delivered** | `delivered` |
| 4 | Alice clicks **Confirm** → releases funds | `completed` |

#### 6c. Dispute flow

| Step | Action | Status |
|------|--------|--------|
| 1–2 | Same as above | `in_escrow` |
| 3 | Click **Dispute** | `disputed` |
| 4 | Click **Refund** | `completed` (refunded) |

---

## 🔑 API Reference

| Method | Endpoint | Role | Description |
|--------|----------|------|-------------|
| POST | `/auth/signup` | Public | Register user |
| POST | `/auth/login` | Public | Get JWT token |
| GET | `/auth/me` | Any | Current user profile |
| GET | `/auth/sellers` | Any | List all sellers |
| POST | `/orders` | Customer | Create order |
| GET | `/orders` | Any | List own orders |
| GET | `/orders/:id` | Any | Get order |
| POST | `/orders/:id/deliver` | Seller | Mark delivered |
| GET | `/orders/analytics` | Any | Dashboard stats |
| POST | `/escrow/deposit` | Customer | Fund escrow |
| POST | `/escrow/release` | Customer | Release to seller |
| POST | `/escrow/dispute` | Customer | Raise dispute |
| POST | `/escrow/refund` | Customer | Refund |
| GET | `/escrow/transactions/:id` | Any | Tx history |

---

## 🔐 Business Logic Rules

```
✅ Only customer can: deposit, release, dispute, refund
✅ Only seller can: mark delivered
✅ Deposit requires: order.status == 'pending'
✅ Release requires: order.status == 'delivered' AND escrow.status == 'held'
✅ Dispute requires: order.status in ['in_escrow', 'delivered']
✅ Refund requires:  order.status == 'disputed' AND escrow.status == 'held'
🚫 Double-release prevented: escrow.status checked before every action
🚫 Double-refund prevented:  same mechanism
```

---

## 💳 Stripe Integration (Future)

The escrow controller is structured to support real payments. Replace the simulated deposit in `escrow_controller.py`:

```python
# In deposit_to_escrow():
# Replace the direct escrow insert with:

import stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

payment_intent = stripe.PaymentIntent.create(
    amount=int(amount * 100),  # cents
    currency="inr",
    capture_method="manual",   # authorize but don't capture yet
    metadata={"order_id": order_id}
)

# Store payment_intent.id in escrow table
# On release: stripe.PaymentIntent.capture(payment_intent_id)
# On refund:  stripe.Refund.create(payment_intent=payment_intent_id)
```

---

## 🧪 Postman Testing

1. Import `EscrowPay.postman_collection.json` into Postman
2. After login, the token auto-saves to `{{TOKEN}}` variable
3. After create order, `{{ORDER_ID}}` auto-saves
4. Run requests in sequence for a complete flow test

---

## 🔧 Troubleshooting

| Issue | Fix |
|-------|-----|
| `connection refused` on DB | Check PostgreSQL is running: `pg_ctl status` |
| `JWT decode error` | Make sure `JWT_SECRET_KEY` in `.env` is set |
| CORS error in browser | Add your frontend URL to `CORS_ORIGINS` in `.env` |
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` in the venv |
| `role "postgres" does not exist` | Use your OS username: `psql -U $(whoami)` |
