import psycopg2
import sys

def get_orders(order_ids):
    conn = psycopg2.connect("dbname='shop' user='postgres' password='admin' host='localhost' port='5432'")
    cur = conn.cursor()
    query = """
            SELECT s.name, p.name, o.order_id, o.quantity, p.id, string_agg(s2.name, ',') AS extra_shelves
            FROM order_items o
            JOIN products p ON o.product_id = p.id
            JOIN shelves s ON p.shelf_id = s.id
            LEFT JOIN unnest(p.extra_shelf_ids) AS extra_shelf_id ON true
            LEFT JOIN shelves s2 ON extra_shelf_id = s2.id
            WHERE o.order_id IN %s
            GROUP BY s.name, p.name, o.order_id, o.quantity, p.id
            ORDER BY s.name, o.order_id, p.id;
            """
    cur.execute(query, (tuple(order_ids),))
    return cur.fetchall()

def main():
    order_ids = list(map(int, sys.argv[1].split(',')))
    print(f"Страница сборки заказов {', '.join(map(str, order_ids))}")
    orders = get_orders(order_ids)

    current_shelf = None
    for order in orders:
        shelf, product, order_id, quantity, product_id, extra_shelf = order
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
