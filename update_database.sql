-- Обновление базы данных для системы скидок
-- Добавляем столбец для комиссии за пополнение
ALTER TABLE settings ADD COLUMN refill_commission_percent REAL DEFAULT 6.0;

-- Создаем таблицу скидок
CREATE TABLE IF NOT EXISTS discounts (
    discount_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR NOT NULL,
    description VARCHAR,
    discount_percent REAL NOT NULL,
    is_active BOOLEAN DEFAULT 1,
    start_date VARCHAR,
    start_unix BIGINT,
    end_date VARCHAR,
    end_unix BIGINT,
    min_purchase_amount REAL DEFAULT 0,
    max_discount_amount REAL DEFAULT 0,
    usage_limit INTEGER DEFAULT 0,
    used_count INTEGER DEFAULT 0,
    created_at VARCHAR,
    created_unix BIGINT,
    created_by BIGINT
);

-- Обновляем значение contests_is_on
UPDATE settings SET contests_is_on = 1 WHERE settings = 'main';
