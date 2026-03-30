from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import time
import psycopg2
from kafka import KafkaProducer, KafkaConsumer
import clickhouse_connect
import json

# Создаём переменные с параметрами подключения.
POSTGRES_CONFIG = {
    'host': 'postgres',
    'port': 5432,
    'database': 'test_db',
    'user': 'admin',
    'password': 'admin'
}

KAFKA_CONFIG = {
    'bootstrap_servers': 'kafka:9093',
    'topic': 'users-topic'
}

CLICKHOUSE_CONFIG = {
    'host': 'clickhouse',
    'port': 8123,
    'username': 'user',
    'password': 'strongpassword'
}

default_args = {
    'owner': 'me',
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
}


# Создаём основную функцию, в которой будет основной код. Для хранения данных в памяти Python.
def run_etl_pipeline():
    """Запускает полный ETL пайплайн."""

    print("Запуск ETL пайплайна.")

    # Сначала достаём из PostgreSQL
    print("\nИзвлечение данных из PostgreSQL...")
    conn = psycopg2.connect(**POSTGRES_CONFIG)
    cur = conn.cursor()
    cur.execute("SELECT id, name, email, role FROM users")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    # Превращаем в список словарей
    users = []
    for row in rows:
        users.append({
            'id': row[0],
            'name': row[1],
            'email': row[2],
            'role': row[3],
            'timestamp': str(datetime.now())
        })

    print(f"Извлечено {len(users)} пользователей из PostgreSQL")

    if not users:
        print("Нет данных для обработки")
        return 0

    # Создаём "производителя" для записи данных.
    print("\nОтправка данных в Kafka...")
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_CONFIG['bootstrap_servers'],
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

    for user in users:
        producer.send(KAFKA_CONFIG['topic'], value=user)
        print(f"Отправлен пользователь {user['id']}: {user['name']}")

    producer.flush()
    producer.close()
    print(f"Отправлено {len(users)} сообщений в Kafka")

    # Небольшая пауза для записи в Kafka
    time.sleep(3)

    # Создаём "потребителя" для чтения данных
    print("\n💾 Загрузка данных в ClickHouse...")

    consumer = KafkaConsumer(
        KAFKA_CONFIG['topic'],
        bootstrap_servers=KAFKA_CONFIG['bootstrap_servers'],
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='clickhouse-group',
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        consumer_timeout_ms=5000
    )

    client = clickhouse_connect.get_client(**CLICKHOUSE_CONFIG)

    # Создаём таблицу, если её нет
    client.command("""
        CREATE TABLE IF NOT EXISTS users_import (
            id UInt32,
            name String,
            email String,
            role String,
            import_time DateTime
        ) ENGINE = MergeTree()
        ORDER BY id
    """)

    count = 0
    for message in consumer:
        user = message.value
        client.insert(
            'users_import',
            [[
                user['id'],
                user['name'],
                user['email'],
                user['role'],
                datetime.now()
            ]],
            column_names=['id', 'name', 'email', 'role', 'import_time']
        )
        count += 1
        print(f"   Загружен пользователь {user['id']}: {user['name']}")

    consumer.close()
    client.close()

    print(f"Загружено {count} записей в ClickHouse")
    return count


# Создаём даг
with DAG(
        'postgres_to_clickhouse_simple',
        default_args=default_args,
        description='ETL: PostgreSQL → Kafka → ClickHouse',
        schedule_interval='*/5 * * * *',
        catchup=False,
) as dag:
    etl_task = PythonOperator(
        task_id='run_etl_pipeline',
        python_callable=run_etl_pipeline,
    )