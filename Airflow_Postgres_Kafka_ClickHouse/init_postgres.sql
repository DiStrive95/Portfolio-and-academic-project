-- Создаём базу данных для Airflow
CREATE DATABASE airflow_db;

-- Создаём таблицы для проекта
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(255),
    role VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_events (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    event_type VARCHAR(50),
    points_spent INTEGER DEFAULT 0,
    event_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Тестовые данные
INSERT INTO users (name, email, role) VALUES
    ('Alice', 'alice@example.com', 'admin'),
    ('Bob', 'bob@example.com', 'user'),
    ('Charlie', 'charlie@example.com', 'user');