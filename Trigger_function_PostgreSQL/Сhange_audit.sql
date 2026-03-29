CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name TEXT,
    email TEXT,
    role TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE users_audit (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    changed_by TEXT,
    field_changed TEXT,
    old_value TEXT,
    new_value TEXT
);


CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_users_timestamp
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION update_updated_at();


CREATE OR REPLACE FUNCTION log_user_update()
RETURNS TRIGGER AS
$$
BEGIN
    IF OLD.name IS DISTINCT FROM NEW.name THEN
        INSERT INTO users_audit (user_id, changed_by, field_changed, old_value, new_value)
        VALUES (NEW.id, current_user, 'name', OLD.name, NEW.name);    
    END IF;

    IF OLD.email IS DISTINCT FROM NEW.email THEN
        INSERT INTO users_audit (user_id, changed_by, field_changed, old_value, new_value)
        VALUES (NEW.id, current_user, 'email', OLD.email, NEW.email);    
    END IF;

    IF OLD.role IS DISTINCT FROM NEW.role THEN
        INSERT INTO users_audit (user_id, changed_by, field_changed, old_value, new_value)
        VALUES (NEW.id, current_user, 'role', OLD.role, NEW.role);    
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_user_changes
AFTER UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION log_user_update();


CREATE EXTENSION IF NOT EXISTS pg_cron;

CREATE OR REPLACE FUNCTION export_yesterdays_audit()
RETURNS void AS $$
DECLARE  
    path TEXT := '/tmp/users_audit_export_' || to_char(CURRENT_DATE - INTERVAL '1 day', 'YYYY-MM-DD') || '.csv';
BEGIN
    EXECUTE format(
        $inner$
        COPY (
            SELECT user_id, changed_at, changed_by, field_changed, old_value, new_value 
            FROM users_audit 
            WHERE changed_at::date = CURRENT_DATE - INTERVAL '1 day'
        ) TO %L WITH CSV HEADER
        $inner$, 
        path
    );
END;
$$ LANGUAGE plpgsql;

-- Установим планировщик pg_cron. Я поставил на 14:30
SELECT cron.schedule('30 14 * * *', $$SELECT export_yesterdays_audit();$$);

-- Проверим наличие задачи
SELECT * FROM cron.job;


