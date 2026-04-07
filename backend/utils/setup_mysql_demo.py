import mysql.connector
import sys

def setup_mysql_sample():
    print("🚀 Setting up MySQL Sample Database...")
    try:
        # 1. Connect without DB first to create it
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="" # Assuming default empty password
        )
        cursor = conn.cursor()
        
        # 2. Create Database
        cursor.execute("CREATE DATABASE IF NOT EXISTS chatsql_demo")
        cursor.execute("USE chatsql_demo")
        
        # 3. Create Tables
        print("Creating tables: departments, employees...")
        cursor.execute("DROP TABLE IF EXISTS employees")
        cursor.execute("DROP TABLE IF EXISTS departments")
        
        cursor.execute("""
            CREATE TABLE departments (
                dept_id INT AUTO_INCREMENT PRIMARY KEY,
                dept_name VARCHAR(50) NOT NULL,
                location VARCHAR(50)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE employees (
                emp_id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                role VARCHAR(50),
                salary DECIMAL(10,2),
                dept_id INT,
                FOREIGN KEY (dept_id) REFERENCES departments(dept_id)
            )
        """)
        
        # 4. Insert Sample Data
        cursor.execute("INSERT INTO departments (dept_name, location) VALUES ('Engineering', 'New York'), ('Marketing', 'London')")
        
        cursor.execute("""
            INSERT INTO employees (name, role, salary, dept_id) VALUES 
            ('Alice Johnson', 'Lead Engineer', 120000.00, 1),
            ('Bob Smith', 'Senior Developer', 95000.00, 1),
            ('Charlie Brown', 'Marketing Manager', 85000.00, 2)
        """)
        
        conn.commit()
        print("✅ MySQL Sample DB 'chatsql_demo' is READY!")
        print("👉 You can now connect to 'chatsql_demo' in ChatSQL.")
        
    except mysql.connector.Error as err:
        print(f"❌ Error: {err}")
        print("\n💡 Tip: Ensure your MySQL server (XAMPP/WAMP/MySQL Installer) is running on localhost.")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    setup_mysql_sample()
