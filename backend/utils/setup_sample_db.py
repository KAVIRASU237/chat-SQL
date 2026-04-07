import sqlite3
import os
import random
from datetime import datetime, timedelta

def random_date(start_year=2022, end_year=2024):
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    delta = end - start
    return (start + timedelta(days=random.randint(0, delta.days))).strftime("%Y-%m-%d")

def setup_db():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    data_dir = os.path.join(project_root, "data")
    db_path = os.path.join(data_dir, "sample.db")

    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # ------------------------------------------------------------------ #
    #  DROP existing tables (order matters due to foreign keys)           #
    # ------------------------------------------------------------------ #
    for tbl in ["order_items", "orders", "reviews", "products",
                "categories", "customers", "employees"]:
        cursor.execute(f"DROP TABLE IF EXISTS {tbl}")

    # ------------------------------------------------------------------ #
    #  CREATE TABLES                                                       #
    # ------------------------------------------------------------------ #

    cursor.execute("""
    CREATE TABLE categories (
        category_id   INTEGER PRIMARY KEY AUTOINCREMENT,
        name          TEXT NOT NULL UNIQUE,
        description   TEXT
    )""")

    cursor.execute("""
    CREATE TABLE products (
        product_id    INTEGER PRIMARY KEY AUTOINCREMENT,
        name          TEXT NOT NULL,
        category_id   INTEGER NOT NULL,
        price         REAL NOT NULL,
        stock         INTEGER DEFAULT 0,
        brand         TEXT,
        FOREIGN KEY (category_id) REFERENCES categories(category_id)
    )""")

    cursor.execute("""
    CREATE TABLE customers (
        customer_id   INTEGER PRIMARY KEY AUTOINCREMENT,
        name          TEXT NOT NULL,
        email         TEXT UNIQUE NOT NULL,
        phone         TEXT,
        city          TEXT,
        state         TEXT,
        country       TEXT DEFAULT 'India',
        joined_date   TEXT
    )""")

    cursor.execute("""
    CREATE TABLE employees (
        employee_id   INTEGER PRIMARY KEY AUTOINCREMENT,
        name          TEXT NOT NULL,
        role          TEXT,
        department    TEXT,
        salary        REAL,
        hire_date     TEXT
    )""")

    cursor.execute("""
    CREATE TABLE orders (
        order_id      INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id   INTEGER NOT NULL,
        employee_id   INTEGER,
        order_date    TEXT NOT NULL,
        status        TEXT CHECK(status IN ('Pending','Processing','Shipped','Delivered','Cancelled')) DEFAULT 'Pending',
        total_amount  REAL DEFAULT 0,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
        FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
    )""")

    cursor.execute("""
    CREATE TABLE order_items (
        item_id       INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id      INTEGER NOT NULL,
        product_id    INTEGER NOT NULL,
        quantity      INTEGER NOT NULL,
        unit_price    REAL NOT NULL,
        FOREIGN KEY (order_id)   REFERENCES orders(order_id),
        FOREIGN KEY (product_id) REFERENCES products(product_id)
    )""")

    cursor.execute("""
    CREATE TABLE reviews (
        review_id     INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id    INTEGER NOT NULL,
        customer_id   INTEGER NOT NULL,
        rating        INTEGER CHECK(rating BETWEEN 1 AND 5),
        comment       TEXT,
        review_date   TEXT,
        FOREIGN KEY (product_id)  REFERENCES products(product_id),
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
    )""")

    # ------------------------------------------------------------------ #
    #  SEED: CATEGORIES                                                    #
    # ------------------------------------------------------------------ #
    categories = [
        ("Electronics",    "Gadgets, devices and electronic accessories"),
        ("Clothing",       "Men's, women's and kids' apparel"),
        ("Books",          "Fiction, non-fiction and academic titles"),
        ("Home & Kitchen", "Appliances, cookware and home décor"),
        ("Sports",         "Fitness equipment and outdoor gear"),
        ("Toys",           "Children's toys and games"),
        ("Beauty",         "Skincare, haircare and cosmetics"),
        ("Grocery",        "Fresh produce, packaged foods and beverages"),
    ]
    cursor.executemany("INSERT INTO categories (name, description) VALUES (?,?)", categories)

    # ------------------------------------------------------------------ #
    #  SEED: PRODUCTS (50 products)                                        #
    # ------------------------------------------------------------------ #
    products = [
        # Electronics (cat 1)
        ("Laptop Pro 15",        1,  75000, 40,  "Dell"),
        ("UltraBook Air",        1,  95000, 25,  "Apple"),
        ("Gaming Laptop X",      1,  85000, 15,  "Asus"),
        ("Wireless Mouse",       1,    999, 200, "Logitech"),
        ("Mechanical Keyboard",  1,   3500, 150, "Corsair"),
        ("4K Monitor 27\"",      1,  28000,  60, "LG"),
        ("Bluetooth Headphones", 1,   5500, 120, "Sony"),
        ("Smartphone Z12",       1,  45000,  80, "Samsung"),
        ("Tablet Pro 11",        1,  55000,  35, "Apple"),
        ("USB-C Hub 7-in-1",     1,   2200, 300, "Anker"),
        ("SSD 1TB",              1,   7500, 500, "WD"),
        ("Webcam HD 1080p",      1,   3200,  90, "Logitech"),
        # Clothing (cat 2)
        ("Men's Slim Fit Jeans", 2,   1800, 300, "Levi's"),
        ("Women's Kurti Set",    2,   1200, 400, "W"),
        ("Sports T-Shirt",       2,    699, 600, "Nike"),
        ("Winter Jacket",        2,   4500, 100, "Puma"),
        ("Cotton Socks Pack",    2,    299, 800, "Dollar"),
        ("Formal Shirt",         2,   1500, 250, "Arrow"),
        # Books (cat 3)
        ("Clean Code",           3,    650,  80, "O'Reilly"),
        ("DBMS Fundamentals",    3,    450, 120, "Pearson"),
        ("Deep Learning Book",   3,    800,  60, "MIT Press"),
        ("Python Crash Course",  3,    599,  90, "NoStarch"),
        ("The Pragmatic Prog.",  3,    750,  70, "Addison"),
        # Home & Kitchen (cat 4)
        ("Pressure Cooker 5L",   4,   2200, 150, "Prestige"),
        ("Non-stick Pan Set",    4,   1800, 200, "Hawkins"),
        ("Air Fryer 4L",         4,   6500,  80, "Philips"),
        ("Water Purifier",       4,  12000,  40, "Kent"),
        ("Mixer Grinder 750W",   4,   3800, 110, "Butterfly"),
        ("Microwave Oven 25L",   4,   9500,  55, "LG"),
        # Sports (cat 5)
        ("Yoga Mat 6mm",         5,    899, 250, "Kobo"),
        ("Dumbbell Set 10kg",    5,   2500, 100, "Kore"),
        ("Treadmill T200",       5,  35000,  20, "PowerMax"),
        ("Badminton Racket",     5,    799, 300, "Yonex"),
        ("Football Size 5",      5,    699, 200, "Cosco"),
        ("Cycling Helmet",       5,   1500, 150, "Vega"),
        # Toys (cat 6)
        ("LEGO City Set",        6,   3200,  80, "LEGO"),
        ("Remote Control Car",   6,   1800, 120, "Hot Wheels"),
        ("Puzzle 1000 pcs",      6,    599, 200, "Funskool"),
        ("Action Figure Set",    6,   1200, 150, "Hasbro"),
        # Beauty (cat 7)
        ("Face Serum 30ml",      7,    999, 300, "Mamaearth"),
        ("Sunscreen SPF50",      7,    499, 400, "Lotus"),
        ("Hair Growth Oil",      7,    349, 500, "Bajaj"),
        ("Lipstick Matte Set",   7,    799, 250, "Lakme"),
        ("Moisturiser 200ml",    7,    599, 350, "Nivea"),
        # Grocery (cat 8)
        ("Basmati Rice 5kg",     8,    450, 600, "India Gate"),
        ("Olive Oil 1L",         8,    750, 400, "Figaro"),
        ("Almonds 500g",         8,    599, 350, "Happilo"),
        ("Green Tea 100 bags",   8,    349, 500, "Lipton"),
        ("Oats 1kg",             8,    199, 700, "Quaker"),
        ("Honey 500g",           8,    349, 450, "Dabur"),
    ]
    cursor.executemany(
        "INSERT INTO products (name,category_id,price,stock,brand) VALUES (?,?,?,?,?)",
        products
    )

    # ------------------------------------------------------------------ #
    #  SEED: CUSTOMERS (40 customers)                                      #
    # ------------------------------------------------------------------ #
    first_names = ["Aarav","Priya","Rahul","Sneha","Vikram","Ananya","Kiran","Deepa",
                   "Suresh","Meena","Arjun","Kavya","Rohit","Lakshmi","Nikhil","Pooja",
                   "Arun","Divya","Sanjay","Rekha","Ajay","Nisha","Manoj","Sunita",
                   "Ravi","Geeta","Vivek","Asha","Dinesh","Radha","Harish","Uma",
                   "Praveen","Shobha","Ganesh","Saranya","Venkat","Bhavana","Krishna","Manjula"]
    last_names  = ["Kumar","Sharma","Patel","Reddy","Singh","Nair","Iyer","Pillai",
                   "Gupta","Rao","Joshi","Mehta","Das","Verma","Menon","Bose",
                   "Kaur","Jain","Choudhary","Mishra","Tiwari","Pandey","Shah","Agarwal",
                   "Shetty","Hegde","Patil","Desai","Naik","Kulkarni","Bhatt","Chauhan",
                   "Murthy","Gowda","Krishnan","Rajan","Anand","Balu","Varma","Srinivas"]
    cities      = ["Chennai","Coimbatore","Mumbai","Delhi","Bangalore","Hyderabad","Pune",
                   "Kolkata","Ahmedabad","Jaipur","Lucknow","Bhopal","Surat","Kochi"]
    states      = {"Chennai":"Tamil Nadu","Coimbatore":"Tamil Nadu","Mumbai":"Maharashtra",
                   "Delhi":"Delhi","Bangalore":"Karnataka","Hyderabad":"Telangana",
                   "Pune":"Maharashtra","Kolkata":"West Bengal","Ahmedabad":"Gujarat",
                   "Jaipur":"Rajasthan","Lucknow":"Uttar Pradesh","Bhopal":"Madhya Pradesh",
                   "Surat":"Gujarat","Kochi":"Kerala"}

    customer_rows = []
    for i in range(40):
        fn   = first_names[i]
        ln   = last_names[i]
        city = random.choice(cities)
        customer_rows.append((
            f"{fn} {ln}",
            f"{fn.lower()}.{ln.lower()}{i}@example.com",
            f"9{random.randint(100000000,999999999)}",
            city,
            states[city],
            "India",
            random_date(2021, 2023)
        ))
    cursor.executemany(
        "INSERT INTO customers (name,email,phone,city,state,country,joined_date) VALUES (?,?,?,?,?,?,?)",
        customer_rows
    )

    # ------------------------------------------------------------------ #
    #  SEED: EMPLOYEES (10 employees)                                      #
    # ------------------------------------------------------------------ #
    employees = [
        ("Rajan Pillai",   "Sales Manager",   "Sales",      85000, "2019-06-01"),
        ("Meena Iyer",     "Sales Executive", "Sales",      45000, "2020-03-15"),
        ("Arjun Nair",     "Sales Executive", "Sales",      42000, "2021-07-10"),
        ("Divya Menon",    "Support Agent",   "Support",    38000, "2022-01-20"),
        ("Suresh Reddy",   "Support Agent",   "Support",    36000, "2021-09-05"),
        ("Kavya Sharma",   "Data Analyst",    "Analytics",  55000, "2020-11-01"),
        ("Nikhil Gupta",   "Backend Dev",     "Tech",       70000, "2019-08-20"),
        ("Pooja Patel",    "Frontend Dev",    "Tech",       65000, "2020-05-12"),
        ("Vikram Singh",   "HR Manager",      "HR",         60000, "2018-04-01"),
        ("Ananya Rao",     "Logistics Head",  "Logistics",  55000, "2019-12-15"),
    ]
    cursor.executemany(
        "INSERT INTO employees (name,role,department,salary,hire_date) VALUES (?,?,?,?,?)",
        employees
    )

    # ------------------------------------------------------------------ #
    #  SEED: ORDERS + ORDER_ITEMS (80 orders)                             #
    # ------------------------------------------------------------------ #
    statuses    = ["Pending","Processing","Shipped","Delivered","Delivered","Delivered","Cancelled"]
    product_ids = list(range(1, len(products) + 1))

    for order_id_offset in range(1, 81):
        cust_id  = random.randint(1, 40)
        emp_id   = random.randint(1, 10)
        odate    = random_date(2022, 2024)
        status   = random.choice(statuses)

        cursor.execute(
            "INSERT INTO orders (customer_id,employee_id,order_date,status,total_amount) VALUES (?,?,?,?,?)",
            (cust_id, emp_id, odate, status, 0)
        )
        oid = cursor.lastrowid

        # 1–5 line items per order
        chosen_prods = random.sample(product_ids, k=random.randint(1, 5))
        order_total  = 0
        for pid in chosen_prods:
            # price from products list (0-indexed)
            unit_price = products[pid - 1][2]
            qty        = random.randint(1, 5)
            order_total += unit_price * qty
            cursor.execute(
                "INSERT INTO order_items (order_id,product_id,quantity,unit_price) VALUES (?,?,?,?)",
                (oid, pid, qty, unit_price)
            )

        # update total_amount
        cursor.execute("UPDATE orders SET total_amount=? WHERE order_id=?", (round(order_total, 2), oid))

    # ------------------------------------------------------------------ #
    #  SEED: REVIEWS (60 reviews)                                          #
    # ------------------------------------------------------------------ #
    comments = [
        "Great product, very satisfied!",
        "Good quality but a bit pricey.",
        "Exactly as described.",
        "Arrived quickly, works perfectly.",
        "Not worth the money.",
        "Would recommend to friends.",
        "Average experience, nothing special.",
        "Excellent build quality.",
        "Delivery was delayed but product is fine.",
        "Superb! Will buy again.",
    ]
    review_combos = set()
    attempts = 0
    while len(review_combos) < 60 and attempts < 500:
        attempts += 1
        pid  = random.randint(1, len(products))
        cid  = random.randint(1, 40)
        if (pid, cid) in review_combos:
            continue
        review_combos.add((pid, cid))
        cursor.execute(
            "INSERT INTO reviews (product_id,customer_id,rating,comment,review_date) VALUES (?,?,?,?,?)",
            (pid, cid, random.randint(1, 5), random.choice(comments), random_date(2022, 2024))
        )

    conn.commit()
    conn.close()
    print(f"✅ Sample database created at: {db_path}")
    print("   Tables: categories, products, customers, employees, orders, order_items, reviews")
    print("   Rows  : 8 categories | 50 products | 40 customers | 10 employees")
    print("           80 orders | ~200 order_items | 60 reviews")


if __name__ == "__main__":
    setup_db()