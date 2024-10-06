import os
import sqlite3
from sqlite3 import Connection, Error
from typing import List, Tuple
import random
import string
from datetime import datetime, timedelta

def create_tables(conn: Connection) -> None:
    """Create tables in the SQLite database."""
    cursor = conn.cursor()

    # Customers table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            age INTEGER NOT NULL CHECK(age > 0)
        );
    """)

    # Products table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            price REAL NOT NULL CHECK(price >= 0),
            stock INTEGER NOT NULL CHECK(stock >= 0)
        );
    """)

    # Orders table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL CHECK(quantity > 0),
            order_date TEXT NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        );
    """)

    # Suppliers table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS suppliers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            contact_name TEXT NOT NULL,
            contact_email TEXT NOT NULL UNIQUE
        );
    """)

    # Shipments table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS shipments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            shipment_date TEXT NOT NULL,
            delivery_date TEXT NOT NULL,
            supplier_id INTEGER NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(id),
            FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
        );
    """)

    conn.commit()

def random_string(length: int) -> str:
    """Generate a random string of fixed length."""
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for _ in range(length))

def random_email(name: str) -> str:
    """Generate a random email address based on a name."""
    domains = ['example.com', 'mail.com', 'test.com']
    return f"{name.lower().replace(' ', '.')}{random.randint(1, 100)}@{random.choice(domains)}"

def random_date(start: datetime, end: datetime) -> datetime:
    """Generate a random datetime between two datetime objects."""
    delta = end - start
    random_days = random.randrange(delta.days)
    return start + timedelta(days=random_days)

def insert_data(
    conn: Connection,
    num_customers: int = 100,
    num_products: int = 50,
    num_suppliers: int = 20,
    num_orders: int = 500,
    num_shipments: int = 400
) -> None:
    """Insert random data into the tables."""
    cursor = conn.cursor()

    # Generate random names
    first_names = ['John', 'Jane', 'Mike', 'Alice', 'Bob', 'Eve', 'Charlie', 'David', 'Emily', 'Frank']
    last_names = ['Smith', 'Johnson', 'Williams', 'Jones', 'Brown', 'Davis', 'Miller', 'Wilson', 'Moore', 'Taylor']

    # Insert customers
    customers_data: List[Tuple[str, str, int]] = []
    for _ in range(num_customers):
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        email = random_email(name)
        age = random.randint(18, 80)
        customers_data.append((name, email, age))
    cursor.executemany(
        "INSERT INTO customers (name, email, age) VALUES (?, ?, ?);",
        customers_data
    )

    # Insert products
    product_names = [f"Product_{i}" for i in range(1, num_products + 1)]
    products_data: List[Tuple[str, float, int]] = []
    for name in product_names:
        price = round(random.uniform(10.0, 1000.0), 2)
        stock = random.randint(0, 100)
        products_data.append((name, price, stock))
    cursor.executemany(
        "INSERT INTO products (name, price, stock) VALUES (?, ?, ?);",
        products_data
    )

    # Insert suppliers
    company_suffixes = ['Inc', 'Corp', 'LLC', 'Ltd', 'Co']
    suppliers_data: List[Tuple[str, str, str]] = []
    for _ in range(num_suppliers):
        company_name = f"{random_string(5)} {random.choice(company_suffixes)}"
        contact_name = f"{random.choice(first_names)} {random.choice(last_names)}"
        contact_email = random_email(contact_name)
        suppliers_data.append((company_name, contact_name, contact_email))
    cursor.executemany(
        "INSERT INTO suppliers (name, contact_name, contact_email) VALUES (?, ?, ?);",
        suppliers_data
    )

    conn.commit()

    # Fetch IDs for relationships
    cursor.execute("SELECT id FROM customers;")
    customer_ids = [row[0] for row in cursor.fetchall()]

    cursor.execute("SELECT id FROM products;")
    product_ids = [row[0] for row in cursor.fetchall()]

    cursor.execute("SELECT id FROM suppliers;")
    supplier_ids = [row[0] for row in cursor.fetchall()]

    # Insert orders
    orders_data: List[Tuple[int, int, int, str]] = []
    start_date = datetime.now() - timedelta(days=365)
    end_date = datetime.now()
    for _ in range(num_orders):
        customer_id = random.choice(customer_ids)
        product_id = random.choice(product_ids)
        quantity = random.randint(1, 10)
        order_date = random_date(start_date, end_date).strftime('%Y-%m-%d')
        orders_data.append((customer_id, product_id, quantity, order_date))
    cursor.executemany(
        "INSERT INTO orders (customer_id, product_id, quantity, order_date) VALUES (?, ?, ?, ?);",
        orders_data
    )

    conn.commit()

    # Fetch order IDs
    cursor.execute("SELECT id, order_date FROM orders;")
    orders_info = cursor.fetchall()
    order_ids = [row[0] for row in orders_info]

    # Insert shipments
    shipments_data: List[Tuple[int, str, str, int]] = []
    for _ in range(num_shipments):
        order_id = random.choice(order_ids)
        shipment_date_dt = random_date(start_date, end_date)
        shipment_date = shipment_date_dt.strftime('%Y-%m-%d')
        delivery_date_dt = shipment_date_dt + timedelta(days=random.randint(1, 30))
        delivery_date = delivery_date_dt.strftime('%Y-%m-%d')
        supplier_id = random.choice(supplier_ids)
        shipments_data.append((order_id, shipment_date, delivery_date, supplier_id))
    cursor.executemany(
        "INSERT INTO shipments (order_id, shipment_date, delivery_date, supplier_id) VALUES (?, ?, ?, ?);",
        shipments_data
    )

    conn.commit()

def populate_database(database_path: str = 'data/database.db') -> None:
    """
    Create and populate the SQLite database with sample data.

    Parameters:
        database_path (str): Path to the SQLite database file.
    """
    # Ensure the database directory exists
    os.makedirs(os.path.dirname(database_path), exist_ok=True)

    try:
        with sqlite3.connect(database_path) as conn:
            create_tables(conn)
            insert_data(conn)
        print("Database populated successfully.")
    except Error as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    populate_database()
