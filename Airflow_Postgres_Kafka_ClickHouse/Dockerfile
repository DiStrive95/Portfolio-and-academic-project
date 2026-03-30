FROM apache/airflow:2.9.2

USER root

# Устанавливаем системные зависимости (нужны для clickhouse-connect)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

USER airflow

# Устанавливаем Python-пакеты
RUN pip install --no-cache-dir \
    kafka-python \
    clickhouse-connect \
    psycopg2-binary