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
  id            INT AUTO_INCREMENT PRIMARY KEY,
  patient_id    VARCHAR(20) UNIQUE,
  full_name     VARCHAR(120) NOT NULL,
  email         VARCHAR(150) UNIQUE NOT NULL,
  phone         VARCHAR(20),
  password_hash VARCHAR(255) NOT NULL,
  created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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

# def create_tables():
#     conn = get_db_connection()
#     cursor = conn.cursor()


#  # 1. PEHLE SAB PURANI TABLES DROP KAREIN
#     # cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
#     # cursor.execute("DROP TABLE IF EXISTS medical_history;")
#     # cursor.execute("DROP TABLE IF EXISTS lab_orders;")
#     # cursor.execute("DROP TABLE IF EXISTS patients;")
#     # cursor.execute("DROP TABLE IF EXISTS doctors;")
#     # cursor.execute("DROP TABLE IF EXISTS admins;")
#     # cursor.execute("DROP TABLE IF EXISTS disease_stats;")
#     # cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")

#     # 2. PHIR NAYI TABLES CREATE KAREIN
#     cursor.execute(PATIENTS_TABLE_SQL)
#     cursor.execute(DOCTOR_TABLE_SQL)
#     cursor.execute(ADMINS_TABLE_SQL)
#     cursor.execute(DISEASE_STATS_TABLE_SQL)

#     # Super Admin Check & Create
#     cursor.execute("SELECT * FROM admins WHERE username = %s", ("adminSaviourAli",))
#     admin_exists = cursor.fetchone()
#     if not admin_exists:
#         strong_password = os.getenv("ADMIN_PASSWORD", "Doctor@SecurePassword786!") 
#         hashed_pw = hash_password(strong_password)
#         insert_query = "INSERT INTO admins (username, hashed_password) VALUES (%s, %s)"
#         cursor.execute(insert_query, ("adminSaviourAli", hashed_pw))
#         print("Super Admin 'adminSaviourAli' created successfully in MySQL!")

#     conn.commit()
#     cursor.close()
#     conn.close()

# def create_tables():
#     conn = get_db_connection()
#     cursor = conn.cursor()

#     # 1. Tables Create Karein
#     cursor.execute(PATIENTS_TABLE_SQL)
#     cursor.execute(DOCTOR_TABLE_SQL)
#     cursor.execute(ADMINS_TABLE_SQL)
#     cursor.execute(DISEASE_STATS_TABLE_SQL)

#     # 2. FORCE RESET ADMIN (Password: admin12!!)
#     cursor.execute("DELETE FROM admins WHERE username = 'adminSaviourAli'")
#     hashed_admin_pw = hash_password("admin12!!")
#     cursor.execute(
#         "INSERT INTO admins (username, hashed_password) VALUES (%s, %s)",
#         ("adminSaviourAli", hashed_admin_pw)
#     )
#     print("Admin successfully created with password 'admin12!!'")

#     conn.commit()
#     cursor.close()
#     conn.close()

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

   # 4. Auto Seed Receptionist (REC_2000)
    rec_pw = hash_password("Rec12345!")
    try:
        cursor.execute(
            """
            INSERT INTO receptionist (username, name, hashed_password) 
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE name=VALUES(name), hashed_password=VALUES(hashed_password)
            """,
            ("REC_2000", "Abdullah", rec_pw)
        )
    except Exception as e:
        print("Receptionist seed log:", e)

    # 5. Auto Seed Lab Technician (LAB_2222)
    lab_pw = hash_password("Lab12345!")
    try:
        # Check column names safely
        cursor.execute(
            """
            INSERT INTO lab_technician (name, hashed_password) 
            VALUES (%s, %s)
            """,
            ("Ahmad", lab_pw)
        )
    except Exception as e:
        print("Lab Technician seed log:", e)

    conn.commit()
    cursor.close()
    conn.close()
    print("Database tables and seed accounts updated successfully!")