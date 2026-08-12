import sqlite3
import os
from typing import Dict

def create_ecommerce_db(db_path: str):
    if os.path.exists(db_path):
        os.remove(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.executescript("""
    CREATE TABLE customers (
        customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        city TEXT NOT NULL,
        country TEXT NOT NULL,
        created_at DATE NOT NULL
    );

    CREATE TABLE categories (
        category_id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_name TEXT NOT NULL,
        description TEXT
    );

    CREATE TABLE products (
        product_id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name TEXT NOT NULL,
        category_id INTEGER NOT NULL,
        price REAL NOT NULL,
        stock_quantity INTEGER NOT NULL,
        FOREIGN KEY (category_id) REFERENCES categories(category_id)
    );

    CREATE TABLE orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        order_date DATE NOT NULL,
        total_amount REAL NOT NULL,
        status TEXT NOT NULL,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
    );

    CREATE TABLE order_items (
        item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        unit_price REAL NOT NULL,
        FOREIGN KEY (order_id) REFERENCES orders(order_id),
        FOREIGN KEY (product_id) REFERENCES products(product_id)
    );

    -- Seed Data
    INSERT INTO categories (category_name, description) VALUES
    ('Electronics', 'Gadgets, devices, and accessories'),
    ('Clothing', 'Apparel and fashion items'),
    ('Home & Living', 'Furniture and home decor'),
    ('Books', 'Printed books and ebooks');

    INSERT INTO customers (name, email, city, country, created_at) VALUES
    ('Alice Smith', 'alice@example.com', 'New York', 'USA', '2023-01-15'),
    ('Bob Jones', 'bob@example.com', 'London', 'UK', '2023-02-20'),
    ('Charlie Brown', 'charlie@example.com', 'Tokyo', 'Japan', '2023-03-10'),
    ('Diana Prince', 'diana@example.com', 'Paris', 'France', '2023-04-05'),
    ('Evan Wright', 'evan@example.com', 'Toronto', 'Canada', '2023-05-12');

    INSERT INTO products (product_name, category_id, price, stock_quantity) VALUES
    ('Laptop Pro 15', 1, 1299.99, 45),
    ('Wireless Noise-Canceling Headphones', 1, 199.50, 120),
    ('Smartphone X', 1, 899.00, 80),
    ('Cotton Casual T-Shirt', 2, 24.99, 300),
    ('Slim Fit Denim Jeans', 2, 59.90, 150),
    ('Ergonomic Office Chair', 3, 249.99, 35),
    ('Modern Table Lamp', 3, 45.00, 90),
    ('Python Data Science Handbook', 4, 39.95, 200),
    ('Designing Data-Intensive Applications', 4, 49.99, 175);

    INSERT INTO orders (customer_id, order_date, total_amount, status) VALUES
    (1, '2023-06-01', 1499.49, 'Completed'),
    (1, '2023-07-15', 59.90, 'Completed'),
    (2, '2023-06-10', 899.00, 'Completed'),
    (3, '2023-06-25', 294.99, 'Shipped'),
    (4, '2023-07-02', 1299.99, 'Completed'),
    (5, '2023-07-20', 89.94, 'Pending');

    INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
    (1, 1, 1, 1299.99),
    (1, 2, 1, 199.50),
    (2, 5, 1, 59.90),
    (3, 3, 1, 899.00),
    (4, 2, 1, 199.50),
    (4, 7, 1, 45.00),
    (4, 8, 1, 39.95),
    (5, 1, 1, 1299.99),
    (6, 4, 2, 24.99),
    (6, 8, 1, 39.95);
    """)

    conn.commit()
    conn.close()


def create_hr_db(db_path: str):
    if os.path.exists(db_path):
        os.remove(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.executescript("""
    CREATE TABLE departments (
        dept_id INTEGER PRIMARY KEY AUTOINCREMENT,
        dept_name TEXT NOT NULL,
        location TEXT NOT NULL,
        budget REAL NOT NULL
    );

    CREATE TABLE employees (
        emp_id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        hire_date DATE NOT NULL,
        dept_id INTEGER NOT NULL,
        salary REAL NOT NULL,
        FOREIGN KEY (dept_id) REFERENCES departments(dept_id)
    );

    CREATE TABLE projects (
        project_id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_name TEXT NOT NULL,
        dept_id INTEGER NOT NULL,
        budget REAL NOT NULL,
        status TEXT NOT NULL,
        FOREIGN KEY (dept_id) REFERENCES departments(dept_id)
    );

    CREATE TABLE employee_projects (
        emp_id INTEGER NOT NULL,
        project_id INTEGER NOT NULL,
        hours_allocated INTEGER NOT NULL,
        PRIMARY KEY (emp_id, project_id),
        FOREIGN KEY (emp_id) REFERENCES employees(emp_id),
        FOREIGN KEY (project_id) REFERENCES projects(project_id)
    );

    -- Seed Data
    INSERT INTO departments (dept_name, location, budget) VALUES
    ('Engineering', 'Building A', 1500000.00),
    ('Marketing', 'Building B', 600000.00),
    ('Human Resources', 'Building A', 400000.00),
    ('Sales', 'Building C', 900000.00),
    ('Finance', 'Building B', 750000.00);

    INSERT INTO employees (first_name, last_name, email, hire_date, dept_id, salary) VALUES
    ('John', 'Doe', 'john.doe@company.com', '2021-03-15', 1, 115000.00),
    ('Jane', 'Smith', 'jane.smith@company.com', '2020-06-01', 1, 135000.00),
    ('Robert', 'Johnson', 'robert.j@company.com', '2019-11-10', 2, 85000.00),
    ('Emily', 'Davis', 'emily.d@company.com', '2022-01-20', 3, 72000.00),
    ('Michael', 'Wilson', 'michael.w@company.com', '2018-08-05', 4, 98000.00),
    ('Sarah', 'Taylor', 'sarah.t@company.com', '2021-09-12', 1, 120000.00),
    ('David', 'Anderson', 'david.a@company.com', '2022-05-18', 5, 92000.00);

    INSERT INTO projects (project_name, dept_id, budget, status) VALUES
    ('Cloud Migration', 1, 450000.00, 'In Progress'),
    ('Brand Relaunch', 2, 200000.00, 'Completed'),
    ('HR Portal Redesign', 3, 120000.00, 'In Progress'),
    ('CRM Integration', 4, 300000.00, 'Planning'),
    ('AI Analytics Engine', 1, 600000.00, 'In Progress');

    INSERT INTO employee_projects (emp_id, project_id, hours_allocated) VALUES
    (1, 1, 120),
    (1, 5, 80),
    (2, 1, 160),
    (2, 5, 100),
    (3, 2, 140),
    (4, 3, 150),
    (5, 4, 130),
    (6, 5, 160),
    (7, 4, 90);
    """)

    conn.commit()
    conn.close()


def create_university_db(db_path: str):
    if os.path.exists(db_path):
        os.remove(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.executescript("""
    CREATE TABLE departments (
        dept_id INTEGER PRIMARY KEY AUTOINCREMENT,
        dept_name TEXT NOT NULL,
        building TEXT NOT NULL
    );

    CREATE TABLE instructors (
        instructor_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        dept_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        FOREIGN KEY (dept_id) REFERENCES departments(dept_id)
    );

    CREATE TABLE courses (
        course_id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_code TEXT UNIQUE NOT NULL,
        title TEXT NOT NULL,
        credits INTEGER NOT NULL,
        dept_id INTEGER NOT NULL,
        instructor_id INTEGER NOT NULL,
        FOREIGN KEY (dept_id) REFERENCES departments(dept_id),
        FOREIGN KEY (instructor_id) REFERENCES instructors(instructor_id)
    );

    CREATE TABLE students (
        student_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        major TEXT NOT NULL,
        enrollment_year INTEGER NOT NULL
    );

    CREATE TABLE enrollments (
        enrollment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        course_id INTEGER NOT NULL,
        semester TEXT NOT NULL,
        grade TEXT,
        FOREIGN KEY (student_id) REFERENCES students(student_id),
        FOREIGN KEY (course_id) REFERENCES courses(course_id)
    );

    -- Seed Data
    INSERT INTO departments (dept_name, building) VALUES
    ('Computer Science', 'Turing Hall'),
    ('Mathematics', 'Euler Building'),
    ('Physics', 'Feynman Complex');

    INSERT INTO instructors (name, email, dept_id, title) VALUES
    ('Dr. Alan Turing', 'turing@univ.edu', 1, 'Professor'),
    ('Dr. Ada Lovelace', 'lovelace@univ.edu', 1, 'Associate Professor'),
    ('Dr. Carl Gauss', 'gauss@univ.edu', 2, 'Professor'),
    ('Dr. Marie Curie', 'curie@univ.edu', 3, 'Professor');

    INSERT INTO courses (course_code, title, credits, dept_id, instructor_id) VALUES
    ('CS101', 'Introduction to Computer Science', 4, 1, 1),
    ('CS301', 'Database Systems', 4, 1, 2),
    ('MATH201', 'Linear Algebra', 3, 2, 3),
    ('PHYS101', 'General Physics I', 4, 3, 4);

    INSERT INTO students (name, email, major, enrollment_year) VALUES
    ('Alex Johnson', 'alex@univ.edu', 'Computer Science', 2021),
    ('Beth Miller', 'beth@univ.edu', 'Mathematics', 2022),
    ('Chris Lee', 'chris@univ.edu', 'Physics', 2021),
    ('Diana Garcia', 'diana@univ.edu', 'Computer Science', 2023);

    INSERT INTO enrollments (student_id, course_id, semester, grade) VALUES
    (1, 1, 'Fall 2022', 'A'),
    (1, 2, 'Spring 2023', 'A-'),
    (2, 3, 'Fall 2022', 'A'),
    (3, 4, 'Fall 2022', 'B+'),
    (4, 1, 'Fall 2023', 'A');
    """)

    conn.commit()
    conn.close()


def initialize_all_databases(data_dir: str) -> Dict[str, str]:
    os.makedirs(data_dir, exist_ok=True)
    db_paths = {
        "ecommerce": os.path.join(data_dir, "ecommerce.db"),
        "hr": os.path.join(data_dir, "hr.db"),
        "university": os.path.join(data_dir, "university.db")
    }

    create_ecommerce_db(db_paths["ecommerce"])
    create_hr_db(db_paths["hr"])
    create_university_db(db_paths["university"])

    return db_paths

if __name__ == "__main__":
    import tempfile
    tmp_dir = tempfile.mkdtemp()
    paths = initialize_all_databases(tmp_dir)
    print(f"Databases initialized successfully in {tmp_dir}: {paths}")
