import requests
import time
import json

URL = "https://api.ycombinator.com/v0.1/companies"

# Подключаемся и получаем одну страницу
def fetch_page(page):

    response = requests.get(URL, params={"page":page}, timeout=10)
    response.raise_for_status()
    return response.json()

# Из информации на первой странице получаем общее количество страниц.
# Если их количество изменится, код будет работать корректно.
first = fetch_page(1)
total_pages = first["totalPages"]
print(f"Всего страниц:{total_pages}")

# Соберем в список компании со всех страниц.
# Данные с первой страницы у нас уже есть, так что используем.
companies = list(first["companies"])

# Название остальных соберем циклом
for page in range(2, total_pages + 1):
    data = fetch_page(page)
    # На каждой странице лежит информация о 25 компаний. Используем extend, чтобы получился один общий список.
    companies.extend(data["companies"])
    print(f"Страница {page}/{total_pages}, всего собрано: {len(companies)}")
    time.sleep(0.3)

print(f"\nГотово. Всего компанийЖ {len(companies)}")

# Сохраним предварительный результат
with open("companies_raw.json", "w", encoding='utf-8') as f:
    json.dump(companies, f, ensure_ascii = False, indent = 2)

