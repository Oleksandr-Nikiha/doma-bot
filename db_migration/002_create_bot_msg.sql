-- =============================================================================
-- Migration: 002_create_bot_msg.sql
-- Створення таблиці для повідомлень бота
-- =============================================================================

CREATE TABLE IF NOT EXISTS bot_messages (
    handler     TEXT PRIMARY KEY,
    messages    JSONB NOT NULL,
    updated_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Тригер для автооновлення updated_at
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER bot_messages_updated_at
    BEFORE UPDATE ON bot_messages
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- =============================================================================
-- Початкові дані
-- =============================================================================

INSERT INTO bot_messages (handler, messages) VALUES
('commands', '{
    "start":   "Привіт! 👋\nЛаскаво просимо до мережі закладів НямНям 🍕\nДля початку роботи, нам необхідно з тобою познайомитися 🤗\nДля цього необхідно поділитися номером та імʼям ☺️",
    "help":    "📋 <b>Доступні команди:</b>\n\n/help — список команд\n/order — поточне замовлення\n/history — історія замовленнь",
    "order":   "Наразі це меню знаходиться в розробці",
    "history": "Наразі це меню знаходиться в розробці"
}')
ON CONFLICT (handler) DO NOTHING;