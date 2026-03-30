from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import time
import psycopg2
from kafka import KafkaProducer, KafkaConsumer
import clickhouse_connect
import json

# Переменные подключения. Параметры взяты из docker-compose.
# Если для проверки проекта потребовалось поменять порты или другие параметры, нужно будет поменять и тут.
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
    'start_date': datetime(2024, 1, 1), # Стартовую дату можно поставить любую, т.к. ниже в даге catchup = False. Но при замене на True нужно вернутся сюда для настройки.
    'retries': 1,
}


# Загрузка из PostgreSQL
def extract_from_postgres(**context):


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
# Отправляем данные при помощи xcom
    context['ti'].xcom_push(key='users', value=users)
    print(f"Извлечено {len(users)} пользователей из PostgreSQL")
    return len(users)


# Отправка данных в кафку
def send_to_kafka(**context):

# Получаем данные из xcom
    users = context['ti'].xcom_pull(key='users', task_ids='extract_from_postgres')

    if not users:
        print("️Нет данных для отправки")
        return 0
# Передаём данные "производителю"
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
    return len(users)


# Получение данных "потребителем"
def load_to_clickhouse(**context):

    time.sleep(3)

    # Создаём консьюмера
    consumer = KafkaConsumer(
        KAFKA_CONFIG['topic'],
        bootstrap_servers=KAFKA_CONFIG['bootstrap_servers'],
        auto_offset_reset='latest',
        enable_auto_commit=False,
        group_id='clickhouse-group',
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        consumer_timeout_ms=5000
    )

    # Подключаемся к ClickHouse
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

    # Читаем сообщения и вставляем в ClickHouse
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
        print(f"Загружен пользователь {user['id']}: {user['name']}")

    consumer.close()
    client.close()

    print(f"Загружено {count} записей в ClickHouse")
    return count


# Создаём даг
with DAG(
        'postgres_to_clickhouse_simple',
        default_args=default_args,
        description='Простой ETL: PostgreSQL -> Kafka -> ClickHouse',
        schedule_interval='*/5 * * * *', # каждые 5 минут
        catchup=False,
) as dag:
    extract = PythonOperator(
        task_id='extract_from_postgres',
        python_callable=extract_from_postgres,
    )

    send = PythonOperator(
        task_id='send_to_kafka',
        python_callable=send_to_kafka,
    )

    load = PythonOperator(
        task_id='load_to_clickhouse',
        python_callable=load_to_clickhouse,
    )

    extract >> send >> load