-- =============================================================================
-- Migration: 001_create_users.sql
-- Створення таблиці для збереження користувачів бота
-- =============================================================================

CREATE TABLE IF NOT EXISTS users (
    user_id       SERIAL PRIMARY KEY,
    telegram_id   BIGINT UNIQUE NOT NULL,
    phone         TEXT,
    display_name  TEXT,
    is_registered BOOLEAN DEFAULT FALSE,
    created_at    TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);