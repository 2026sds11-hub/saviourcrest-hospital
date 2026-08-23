import mysql.connector
import os
from auth import hash_password 

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", 3307)),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME", "saviours_hospital")
    )
def create_tables():
    conn=get_db_connection()
    cursor= conn.cursor()


PATIENTS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS patients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id VARCHAR(20) UNIQUE,
    full_name VARCHAR(120) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    gender VARCHAR(20),
    age INT,
    phone VARCHAR(20),
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""
#-------------- Doctor Signup -------------------------
DOCTOR_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS doctors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    uuid VARCHAR(36),
    full_name VARCHAR(100) NOT NULL,
    pmdc_id VARCHAR(50) UNIQUE NOT NULL,
    cnic VARCHAR(20) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    specialization VARCHAR(100) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

#======================================================================
#Admin
#======================================================================
ADMINS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS admins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    uuid VARCHAR(36),
    username VARCHAR(50) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""    

RECEPTIONIST_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS receptionist (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

LAB_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS lab_technician (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

SALARIES_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS salaries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_name VARCHAR(100) NOT NULL,
    role VARCHAR(50) NOT NULL,
    department VARCHAR(50) NOT NULL,
    monthly_salary DECIMAL(10, 2) NOT NULL,
    status VARCHAR(20) DEFAULT 'Unpaid',
    last_paid_date DATE DEFAULT NULL,
    doctor_id INT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""
# ---------live graph----------    
DISEASE_STATS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS disease_stats (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  disease_name VARCHAR(100) NOT NULL,
  cases        INT NOT NULL,
  region       VARCHAR(100) DEFAULT 'National',
  recorded_on  DATE NOT NULL
);
"""



def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Execute Table Creations
    cursor.execute(PATIENTS_TABLE_SQL)
    cursor.execute(DOCTOR_TABLE_SQL)
    cursor.execute(ADMINS_TABLE_SQL)
    cursor.execute(DISEASE_STATS_TABLE_SQL)
    cursor.execute(RECEPTIONIST_TABLE_SQL)
    cursor.execute(LAB_TABLE_SQL)

    # 2. Missing Columns Fixes for Live Database Schema Alteration
    try:
        cursor.execute("ALTER TABLE admins ADD COLUMN uuid VARCHAR(36);")
    except Exception:
        pass

    try:
        cursor.execute("ALTER TABLE doctors ADD COLUMN specialization VARCHAR(100);")
    except Exception:
        pass

    try:
        cursor.execute("ALTER TABLE doctors ADD COLUMN uuid VARCHAR(36);")
    except Exception:
        pass

    # 3. Force Reset Super Admin
    cursor.execute("DELETE FROM admins WHERE username = 'adminSaviourAli'")
    hashed_admin_pw = hash_password("admin12!!")
    cursor.execute(
        "INSERT INTO admins (username, hashed_password) VALUES (%s, %s)",
        ("adminSaviourAli", hashed_admin_pw)
    )

  # 4. Auto Seed Receptionist (Abdullah - REC_2000)
    try:
        cursor.execute(
            """
            INSERT INTO receptionists (hospital_id, full_name) 
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE full_name=VALUES(full_name)
            """,
            ("REC_2000", "Abdullah")
        )
    except Exception as e:
        print("Receptionist seed log:", e)

    # 5. Auto Seed Lab Technician (Ahmad - LAB_2222)
    try:
        cursor.execute(
            """
            INSERT INTO lab_technician (hospital_id, full_name) 
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE full_name=VALUES(full_name)
            """,
            ("LAB_2222", "Ahmad")
        )
    except Exception as e:
        print("Lab Technician seed log:", e)


        # Salaries Table Create
    cursor.execute(SALARIES_TABLE_SQL)

    # Salaries Auto-Seed (Aap ke screenshot 2 ka data)
    salaries_data = [
        ('Ali (REC_1222)', 'Receptionist', 'Reception', 55000.00, 'Unpaid'),
        ('Saood (REC_1999)', 'Receptionist', 'Reception', 55000.00, 'Unpaid'),
        ('Abdullah (REC_2000)', 'Receptionist', 'Reception', 55000.00, 'Unpaid'),
        ('Tom (REC_001)', 'Receptionist', 'Reception', 50000.00, 'Unpaid'),
        ('Ahmad (LAB_2222)', 'Lab Technician', 'Laboratory', 75000.00, 'Unpaid'),
        ('Qasim', 'Head', 'Manager', 120000.00, 'Unpaid'),
        ('David Osei', 'Head Nurse', 'Emergency', 85000.00, 'Unpaid'),
        ('Priya Nair', 'Administrator', 'Management', 100000.00, 'Unpaid'),
        ('Imran Qureshi', 'Lab Technician', 'Laboratory', 70000.00, 'Unpaid'),
        ('Farah Siddiqui', 'Pharmacy In-Charge', 'Pharmacy', 90000.00, 'Unpaid'),
        ('Umar Farooq', 'Billing Officer', 'Accounts', 65000.00, 'Unpaid')
    ]

    for name, role, dept, salary, status in salaries_data:
        try:
            cursor.execute(
                """
                INSERT INTO salaries (employee_name, role, department, monthly_salary, status)
                SELECT %s, %s, %s, %s, %s
                WHERE NOT EXISTS (SELECT 1 FROM salaries WHERE employee_name = %s);
                """,
                (name, role, dept, salary, status, name)
            )
        except Exception as e:
            print("Salary seed log:", e)


    try:
        cursor.execute("ALTER TABLE patients ADD COLUMN gender VARCHAR(20);")
    except Exception:
        pass

    try:
        cursor.execute("ALTER TABLE patients ADD COLUMN age INT;")
    except Exception:
        pass

    try:
        cursor.execute("ALTER TABLE patients ADD COLUMN phone VARCHAR(20);")
    except Exception:
        pass

    try:
        cursor.execute("ALTER TABLE patients ADD COLUMN password_hash VARCHAR(255);")
    except Exception:
        pass

    conn.commit()
    cursor.close()
    conn.close()
    print("Database tables and seed accounts updated successfully!")