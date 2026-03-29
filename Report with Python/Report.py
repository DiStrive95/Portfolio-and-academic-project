purchases = [
    {"item": "apple", "category": "fruit", "price": 1.2, "quantity": 10},
    {"item": "banana", "category": "fruit", "price": 0.5, "quantity": 5},
    {"item": "milk", "category": "dairy", "price": 1.5, "quantity": 2},
    {"item": "bread", "category": "bakery", "price": 2.0, "quantity": 3},
]

def total_revenue(purchases):

    total_rev = 0

    for i in purchases:
        total_rev += i["price"] * i["quantity"]
    return f"Общая выручка: {total_rev}"

print(total_revenue(purchases))


def items_by_category(purchases):
    items_by_cat = {}

    for purchase in purchases:
        category = purchase["category"]
        item = purchase["item"]

        items_by_cat.setdefault(category, [])
        if item not in items_by_cat[category]:
            items_by_cat[category].append(item)

    return f"Товары по категориям: {items_by_cat}"

print(items_by_category(purchases))

def m_p(purchases):
    m = []

    for purchase in purchases:
        m.append(purchase["price"])

    return min(m)

def expensive_purchases(purchases, min_price):
    mod_purchases = []

    for purchase in purchases:
        if purchase["price"] >= min_price:
            mod_purchases.append(purchase)

    return f"Покупки дороже {min_price}: {mod_purchases}"

min_price = m_p(purchases)
print(expensive_purchases(purchases, min_price))

def average_price_by_category(purchases):
    category_prices = {}

    for purchase in purchases:
        category = purchase["category"]
        price = purchase["price"]
        item = purchase["item"]

        if category not in category_prices:
            category_prices[category] = {}

        category_prices[category][item] = price

        result = {}
        for category, items in category_prices.items():
            prices = list(items.values())
            result[category] = sum(prices) / len(prices)

    return f"Средняя цена по категориям: {result}"

print(average_price_by_category(purchases))


def most_frequent_category(purchases):

    category_quantity = {}

    for purchase in purchases:
        category = purchase["category"]
        quantity = purchase["quantity"]

        category_quantity[category] = category_quantity.get(category, 0) + quantity

    max_category = max(category_quantity, key=category_quantity.get)

    return f"Категория с наибольшим количеством проданных товаров: {max_category}"

print(most_frequent_category(purchases))