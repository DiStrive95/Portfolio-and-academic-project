from datetime import datetime, timedelta
from pymongo import MongoClient
import json

client = MongoClient("mongodb://localhost:27017/")
db = client["my_database"]
collection = db["user_events"]
archive_collection = db["archived_users"]

today = datetime.now()
thirty_days_ago = today - timedelta(days=30)
fourteen_days_ago = today - timedelta(days=14)

# Агрегация для поиска пользователей
ag = [
    {
        "$group": {
            "_id": "$user_id",
            "last_activity": {"$max": "$event_time"},
            "registration_date": {"$first": "$user_info.registration_date"},
            "user_documents": {"$push": "$$ROOT"}  # ← собираем ВСЕ документы пользователя
        }
    },
    {
        "$match": {
            "registration_date": {"$lt": thirty_days_ago},
            "last_activity": {"$lt": fourteen_days_ago}
        }
    }
]

users_to_archive = list(collection.aggregate(ag))

if users_to_archive:
    # Собираем все документы для архивирования
    all_documents = []
    user_ids = []

    for user in users_to_archive:
        user_ids.append(user["_id"])
        all_documents.extend(user["user_documents"])  # добавляем все документы пользователя

    # Архивируем все документы
    if all_documents:
        archive_collection.insert_many(all_documents)

    # Удаляем все документы архивированных пользователей
    collection.delete_many({
        "user_id": {"$in": user_ids}
    })

    archived_count = len(user_ids)  # количество пользователей
    archived_ids = user_ids
else:
    archived_count = 0
    archived_ids = []

# Формируем отчёт
report_date = today.strftime("%Y-%m-%d")
report = {
    "date": report_date,
    "archived_users_count": archived_count,
    "archived_user_ids": archived_ids
}

filename = f"{report_date}.json"
with open(filename, "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2, ensure_ascii=False)

print(f"Отчёт сохранён: {filename}")
print(f"Архивировано пользователей: {archived_count}")