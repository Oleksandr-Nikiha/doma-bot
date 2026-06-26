-- =============================================================================
-- Migration: 003_create_menu.sql
-- =============================================================================

CREATE TABLE IF NOT EXISTS categories (
    category_id  SERIAL PRIMARY KEY,
    name         TEXT NOT NULL UNIQUE,
    emoji        TEXT,
    is_active    BOOLEAN DEFAULT TRUE,
    position     INT DEFAULT 0,
    keyboard_columns INT
);

CREATE TABLE IF NOT EXISTS menu_items (
    item_id      SERIAL PRIMARY KEY,
    category_id  INT REFERENCES categories(category_id),
    name         TEXT NOT NULL,
    description  TEXT,
    emoji        TEXT,
    is_active    BOOLEAN DEFAULT TRUE,
    position     INT DEFAULT 0,
    photo_id     TEXT;
);

CREATE TABLE IF NOT EXISTS size_templates (
    size_id   SERIAL PRIMARY KEY,
    name      TEXT NOT NULL,
    size_cm   INT,
    position  INT DEFAULT 0
);

CREATE TABLE IF NOT EXISTS item_prices (
    price_id  SERIAL PRIMARY KEY,
    item_id   INT REFERENCES menu_items(item_id),
    size_id   INT REFERENCES size_templates(size_id),
    weight_g  INT,
    price     NUMERIC(10,0) NOT NULL
);


-- =============================================================================
-- Початкові дані
-- =============================================================================

INSERT INTO categories (name, emoji, position) VALUES
('Піца',            '🍕', 0),
('Суші та роли',    '🍣', 1),
('Боули та салати', '🥗', 2),
('Закуски',         '🍟', 3),
('Десерти',         '🧁', 4),
('Напої',           '🍹', 5),
('Круасани',        '🥐', 6)
ON CONFLICT (name) DO NOTHING;

INSERT INTO size_templates (name, size_cm, position) VALUES
('S',   25, 0),
('M',   32, 1),
('XL',  40, 2),
('3XL', 60, 3)
ON CONFLICT DO NOTHING;