import json
import clickhouse_connect

# Создаём таблицу
client = clickhouse_connect.get_client(
    host = "localhost",
    username = "default",
    password = "ycpass",
)

client.command("""
CREATE TABLE IF NOT EXISTS yc_companies
(
    id UInt32,
    name String,
    slug String,
    one_liner String,
    team_size UInt16,
    batch LowCardinality(String),
    status LowCardinality(String),
    tags Array(String),
    industries Array(String),
    regions Array(String),
    location String,
    has_badge UInt8
)
ENGINE = MergeTree()
ORDER BY (batch, status)
""")
print("Таблица создана")

# В json-файле есть лишние поля, которые нам не нужны и они не созданы в таблице.
# Поэтому, для загрузки данных, нужня взять только необходимое.

with open("companies_raw.json", encoding="utf-8") as f:
    companies = json.load(f)

rows = []

for c in companies:
    locations = c.get("locations") or []
    badges = c.get("badges") or []
    rows.append([
        c["id"],
        c["name"],
        c["slug"],
        c.get("oneLiner") or "",
        c.get("teamSize") or 0,
        c.get("batch") or "",
        c.get("status") or "",
        c.get("tags") or [],
        c.get("industries") or [],
        c.get("regions") or [],
        locations[0] if locations else "",
        1 if badges else 0,
    ])

print(f"Готово строк к заливке: {len(rows)}")

# Загружаем данные
client.insert(
    "yc_companies",
    rows,
    column_names=[
        "id", "name", "slug", "one_liner", "team_size",
        "batch", "status", "tags", "industries", "regions",
        "location", "has_badge",
    ],
)
print("Залито в ClickHouse")