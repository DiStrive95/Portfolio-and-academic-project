import csv
import io
import requests
from clickhouse_driver import Client

CATALOG_URL = "https://gwosc.org/eventapi/csv/GWTC-1-confident/"

# Эта переменная поможет нам разделять нейтронные звёзды и чёрные дыры
# опираясь на массу. Меньше - звезда, больше - дыра.
NS_MAX_MASS = 3.0

def to_float(value):
    '''В полученном каталоге могут быть пустые параметры, либо не тот
        тип данных, который мы ожидаем. В таких случаях данная функция вернёт None'''

    if value is None or value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None

def classify(mass_1, mass_2):
    '''Проверяет массы двух объектов и определяет тип слияния'''

    if mass_1 is None or mass_2 is None:
        return "UNKNOWN"

    is_ns_1 = mass_1 < NS_MAX_MASS
    is_ns_2 = mass_2 < NS_MAX_MASS

    if is_ns_1 and is_ns_2:
        return "BNS" # Две нейтронные звезды
    elif not is_ns_1 and not is_ns_2:
        return "BBH" # Две черные дыры
    else:
        return "NSBH" # Смешанная пара


def fetch_events():
    '''Выполняет два этапа - Extract и Transform, с использованием
        двух предыдущих функций.'''

    response = requests.get(CATALOG_URL, timeout = 30)
    response.raise_for_status()

    reader = csv.DictReader(io.StringIO(response.text))
    events = []

    for row in reader:
        mass_1 = to_float(row["mass_1_source"])
        mass_2 = to_float(row["mass_2_source"])

        if mass_1 is None or mass_2 is None:
            continue

        total_mass = mass_1 + mass_2

        events.append([
            row["commonName"],
            to_float(row["GPS"]),
            mass_1,
            mass_2,
            total_mass,
            to_float(row["network_matched_filter_snr"]),
            to_float(row["luminosity_distance"]),
            to_float(row["redshift"]),
            row.get("catalog.shortName") or None,
            classify(mass_1, mass_2),
        ])

    return events

def main():
    ''' Добавляет этап Load, закрывая весь ETL.'''

    events = fetch_events()

    print(f"Скачано событий: {len(events)}")

    client = Client(
        host = "localhost",
        port = 9000,
        user = "default",
        password = "clickhouse",
        database = "gw",
    )

    # В данном случае предваврительно очистим всю таблицу. Объем данных мал
    # и он меняется редко. Поэтому быстрее перезагрузить всё заново, чем проверять дубли.
    client.execute("TRUNCATE TABLE gw.events")

    client.execute(
            """INSERT INTO gw.events
                (common_name, gps, mass_1_source, mass_2_source,
             total_mass_source, network_snr, luminosity_distance,
             redshift, catalog, merger_type)
        VALUES""", events
    )

    print("Данные успешно загружены")

if __name__ == "__main__":
    main()

# После запуска кода и успешной загрузки нужно проверить результат в sql-скрипте.