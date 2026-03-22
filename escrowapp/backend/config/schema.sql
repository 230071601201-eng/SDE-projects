-- ============================================================
-- Escrow Payment System - PostgreSQL Schema
-- ============================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- USERS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name        VARCHAR(255) NOT NULL,
    email       VARCHAR(255) UNIQUE NOT NULL,
    password    VARCHAR(255) NOT NULL,  -- bcrypt hashed
    role        VARCHAR(20) NOT NULL CHECK (role IN ('customer', 'seller')),
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================
-- ORDERS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS orders (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    seller_id   UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    amount      NUMERIC(12, 2) NOT NULL CHECK (amount > 0),
    description TEXT,
    status      VARCHAR(20) NOT NULL DEFAULT 'pending'
                CHECK (status IN ('pending', 'in_escrow', 'delivered', 'completed', 'disputed')),
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================
-- ESCROW TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS escrow (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id    UUID UNIQUE NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    amount      NUMERIC(12, 2) NOT NULL CHECK (amount > 0),
    status      VARCHAR(20) NOT NULL DEFAULT 'held'
                CHECK (status IN ('held', 'released', 'refunded')),
    held_at     TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    released_at TIMESTAMP WITH TIME ZONE,
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================
-- TRANSACTIONS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS transactions (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id    UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    type        VARCHAR(20) NOT NULL CHECK (type IN ('deposit', 'release', 'refund')),
    amount      NUMERIC(12, 2) NOT NULL CHECK (amount > 0),
    note        TEXT,
    timestamp   TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================
-- INDEXES for performance
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_orders_customer   ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_seller     ON orders(seller_id);
CREATE INDEX IF NOT EXISTS idx_orders_status     ON orders(status);
CREATE INDEX IF NOT EXISTS idx_escrow_order      ON escrow(order_id);
CREATE INDEX IF NOT EXISTS idx_transactions_order ON transactions(order_id);

-- ============================================================
-- AUTO-UPDATE updated_at trigger
-- ============================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_orders_updated_at
    BEFORE UPDATE ON orders
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
