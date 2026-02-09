import sqlite3
import os

def setup_db():
    # Use absolute paths for reliability
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    data_dir = os.path.join(project_root, "data")
    db_path = os.path.join(data_dir, "sample.db")
    
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create Tables
    cursor.execute("DROP TABLE IF EXISTS order_items")
    cursor.execute("DROP TABLE IF EXISTS orders")
    cursor.execute("DROP TABLE IF EXISTS products")
    cursor.execute("DROP TABLE IF EXISTS customers")

    cursor.execute("""
    CREATE TABLE customers (
        customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE,
        city TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE products (
        product_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT,
        price REAL
    )
    """)

    cursor.execute("""
    CREATE TABLE orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        order_date TEXT,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
    )
    """)

    cursor.execute("""
    CREATE TABLE order_items (
        item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER,
        product_id INTEGER,
        quantity INTEGER,
        FOREIGN KEY (order_id) REFERENCES orders(order_id),
        FOREIGN KEY (product_id) REFERENCES products(product_id)
    )
    """)

    # Seed Data
    cursor.execute("INSERT INTO customers (name, email, city) VALUES ('Alice Johnson', 'alice@example.com', 'New York')")
    cursor.execute("INSERT INTO customers (name, email, city) VALUES ('Bob Smith', 'bob@example.com', 'Los Angeles')")
    cursor.execute("INSERT INTO customers (name, email, city) VALUES ('Charlie Brown', 'charlie@example.com', 'Chicago')")

    cursor.execute("INSERT INTO products (name, category, price) VALUES ('Laptop', 'Electronics', 1000.00)")
    cursor.execute("INSERT INTO products (name, category, price) VALUES ('Mouse', 'Electronics', 25.00)")
    cursor.execute("INSERT INTO products (name, category, price) VALUES ('Keyboard', 'Electronics', 50.00)")
    cursor.execute("INSERT INTO products (name, category, price) VALUES ('Monitor', 'Electronics', 300.00)")

    cursor.execute("INSERT INTO orders (customer_id, order_date) VALUES (1, '2024-01-10')")
    cursor.execute("INSERT INTO orders (customer_id, order_date) VALUES (1, '2024-02-15')")
    cursor.execute("INSERT INTO orders (customer_id, order_date) VALUES (2, '2024-01-20')")

    cursor.execute("INSERT INTO order_items (order_id, product_id, quantity) VALUES (1, 1, 2)")
    cursor.execute("INSERT INTO order_items (order_id, product_id, quantity) VALUES (1, 2, 10)")
    cursor.execute("INSERT INTO order_items (order_id, product_id, quantity) VALUES (2, 3, 5)")
    cursor.execute("INSERT INTO order_items (order_id, product_id, quantity) VALUES (3, 4, 3)")
    cursor.execute("INSERT INTO order_items (order_id, product_id, quantity) VALUES (3, 1, 1)")

    conn.commit()
    conn.close()
    print(f"Sample database created at {db_path}")

if __name__ == "__main__":
    setup_db()
