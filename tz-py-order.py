import psycopg2
import sys

connection = psycopg2.connect(
    dbname="shop",
    user="postgres",
    password="admin",
    host="localhost",
    port="5432"
)
cur = connection.cursor()

def get_order_items(order_ids):
    query = """
            SELECT o.order_id, o.product_id, o.quantity
            FROM order_items o
            WHERE o.order_id IN %s;
            """
    cur.execute(query, (tuple(order_ids),))
    return cur.fetchall()

def get_product_info(product_ids):
    query = """
            SELECT p.id, p.name, p.shelf_id, p.extra_shelf_ids
            FROM products p
            WHERE p.id IN %s;
            """
    cur.execute(query, (tuple(product_ids),))
    return cur.fetchall()

def get_shelf_info(shelf_ids):
    query = """
            SELECT s.id, s.name
            FROM shelves s
            WHERE s.id IN %s;
            """
    cur.execute(query, (tuple(shelf_ids),))
    return dict(cur.fetchall())

def get_extra_shelves(extra_shelf_ids):
    query = """
            SELECT id, name
            FROM shelves
            WHERE id IN %s;
            """
    cur.execute(query, (tuple(extra_shelf_ids),))
    return dict(cur.fetchall())

def main():
    order_ids = list(map(int, sys.argv[1].split(',')))
    print(f"Страница сборки заказов {', '.join(map(str, order_ids))}")
    order_items = get_order_items(order_ids)
    product_ids = set(item[1] for item in order_items)
    product_info = {item[0]: (item[1], item[2], item[3]) for item in get_product_info(product_ids)}
    shelf_info = get_shelf_info({item[1] for item in product_info.values()})
    extra_shelves = get_extra_shelves({int(id_) for ids in product_info.values() for id_ in ids[2]})
    items = []

    for order_id, product_id, quantity in order_items:
        product, shelf_id, extra_shelf_ids = product_info[product_id]
        shelf = shelf_info[shelf_id]
        extra_shelf = ', '.join(extra_shelves[int(id_)] for id_ in extra_shelf_ids) if extra_shelf_ids else None
        items.append((shelf, order_id, product, product_id, quantity, extra_shelf))

    items.sort(key=lambda x: (x[0], x[1]))
    current_shelf = None
    for shelf, order_id, product, product_id, quantity, extra_shelf in items:
        if shelf != current_shelf:
            if current_shelf:
                print()
            print(f"===Стеллаж {shelf}")
            current_shelf = shelf

        print(f"{product} (id={product_id})")
        print(f"заказ {order_id}, {quantity} шт")
        if extra_shelf:
            print(f"доп стеллаж: {extra_shelf}")
        print(f"")

if __name__ == "__main__":
    main()