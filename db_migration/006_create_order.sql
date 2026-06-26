-- =============================================================================
-- Migration: 006_create_order.sql
-- =============================================================================

CREATE TABLE IF NOT EXISTS orders (
    order_id       SERIAL PRIMARY KEY,
    user_id        INT REFERENCES users(user_id),
    status         TEXT DEFAULT 'draft',  -- draft, confirmed, preparing, ready, delivered, cancelled
    comment        TEXT,
    delivery_type  TEXT,                  -- 'delivery' / 'pickup'
    address        TEXT,
    delivery_time  TEXT,                  -- 'asap' / 'HH:MM'
    payment_type   TEXT,                  -- 'cash' / 'card'
    change_from    NUMERIC(10,0),
    created_at     TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at     TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS order_items (
    order_item_id  SERIAL PRIMARY KEY,
    order_id       INT REFERENCES orders(order_id),
    item_id        INT REFERENCES menu_items(item_id),
    price_id       INT REFERENCES item_prices(price_id),
    quantity       INT DEFAULT 1,
    price          NUMERIC(10,0) NOT NULL
);

ALTER TABLE order_items 
ADD CONSTRAINT unique_order_item UNIQUE (order_id, item_id, price_id);