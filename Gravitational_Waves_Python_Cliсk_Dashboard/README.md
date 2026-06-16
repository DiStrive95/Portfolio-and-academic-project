 # Проект "Гравитационные волны" =)
 
### Что тут происходит?

1. В Docker  нужно поднять хранилище ClickHouse. 
        Для этого в терминале потребуется запустить команду:
        ```docker run -d --name gw-clickhouse -e CLICKHOUSE_USER=default -e CLICKHOUSE_PASSWORD=clickhouse -e CLICKHOUSE_DB=default -p 8123:8123 -p 9000:9000 --ulimit nofile=262144:262144 clickhouse/clickhouse-server:24.3```
        Параметры можно поменять, но в коде тоже придётся исправить. У меня на windows  эта команда работает при вводе одной стркой.
2. Данные берутся из открытого научного источника https://gwosc.org/eventapi/csv/GWTC/. 
Чтобы они успешно загрузились, сначала создатся база данных и в ней таблица - скрипт Create_database_and_table.sql.
3. Следующим шагом будет запуск python-кода из файла load.py. В нём функции ETL процесса.
4. Analysis.sql содержит простые запросы, для контекста проекта.
5. Построение дашборда осуществяется кодом из dashboard.py. Используется streamlit. Запуск скрипта через терминал из папки, где он находится ```python -m streamlit run dashboard.py```. Откроется браузер с визуализацией.

Дополнительные комментарии содержатся в коде.

В результате должна получиться такая страница:
 
<img width="2557" height="938" alt="ДШ1" src="https://github.com/user-attachments/assets/a8e4e148-6d59-4e70-a03f-0ed045136010" />
<img width="2557" height="582" alt="ДШ2" src="https://github.com/user-attachments/assets/529abb64-debb-42e0-ae70-0810cefa02b4" />
<img width="2378" height="932" alt="ДШ3" src="https://github.com/user-attachments/assets/9b2210b4-9faf-4f81-863d-04d99f84928a" />
