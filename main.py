from fastapi import FastAPI, Request,Header, HTTPException,Response, status, UploadFile, File, Query,Form, Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from passlib.context import CryptContext
from mysql.connector import Error
from fastapi.responses import HTMLResponse 
from fastapi import APIRouter
from typing import Optional
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from jwt.exceptions import PyJWTError
from datetime import datetime
import uuid as uuid_lib  
import random
import uuid
import shutil
import base64
import jwt
import os
import re
import datetime
import decimal
from datetime import date
from dotenv import load_dotenv
import mysql.connector
from auth import SECRET_KEY , ALGORITHM, verify_admin_token, hash_password, verify_password ,create_access_token,oauth2_scheme
from models import get_db_connection, create_tables
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
# Limit setup
limiter = Limiter(key_func=get_remote_address) 

load_dotenv()

templates = Jinja2Templates(directory="Template")

app = FastAPI(title="Saviours Hospital")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


app.mount("/static", StaticFiles(directory="static"), name="static")
app.add_middleware(
    SessionMiddleware, 
    secret_key=os.getenv("SECRET_KEY")
    )

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

create_tables()

# ----------------------------------------------------------------
# HOMEPAGE
# ----------------------------------------------------------------
# @app.get("/")
# def home(request: Request):
#     return templates.TemplateResponse("main_page.html", {"request": request})
@app.get("/")
def home_redirect():
    return RedirectResponse(url="/main_page", status_code=302)

# 2. Ye aapka main page render karega aur URL mein saaf '/main_page' dikhayega
@app.get("/main_page", response_class=HTMLResponse)
def read_main(request: Request):
    db = get_db_connection()
    # Apni queries yahan chalaayein
    db.close()
    
    return templates.TemplateResponse("main_page.html", {"request": request})

#================
#Secure Routing
#================
def check_auth(request:Request):
    token=request.cookies.get("admin_token")
    if not token:
        return False
# =====================================================================
# 1. ALL LOGIN & PUBLIC PAGES (Clean & Alias Handled)
# =====================================================================

# --- Admin ---------
@app.get("/admin_login", response_class=HTMLResponse)
@app.get("/admin_login.html", response_class=HTMLResponse)
def admin_login_page(request: Request):
    return templates.TemplateResponse("admin_login.html", {"request": request})

# --- ABOUT PAGE ALIASES ---
@app.get("/about", response_class=HTMLResponse)
def about_page(request: Request):
    return templates.TemplateResponse("about_page.html", {"request": request})

# --- PATIENT LOGIN PAGE (FIXED MISSING ROUTE) ---
@app.get("/patient_login", response_class=HTMLResponse)
@app.get("/patient_login.html", response_class=HTMLResponse)
def patient_login_page(request: Request):
    return templates.TemplateResponse("patient_login.html", {"request": request})


# --- RECEPTION LOGIN PAGE (FIXED .HTML MISMATCH) ---
@app.get("/reception_login", response_class=HTMLResponse)
@app.get("/reception_login.html", response_class=HTMLResponse)
def reception_login_page(request: Request):
    return templates.TemplateResponse("reception_login.html", {"request": request})

# --- DOCTOR LOGIN PAGE ---
@app.get("/doctor_login", response_class=HTMLResponse)
@app.get("/doctor_login.html", response_class=HTMLResponse)
def doctor_login_page(request: Request):
    return templates.TemplateResponse("doctor_login.html", {"request": request})

# --- LAB LOGIN PAGE ---
@app.get("/lab_login", response_class=HTMLResponse)
@app.get("/lab_login.html", response_class=HTMLResponse)
def lab_login_page(request: Request):
    return templates.TemplateResponse("lab_login.html", {"request": request})

# ================= PAGE ROUTE (WITH ALL ALIASES) =================
@app.get("/patient_record", response_class=HTMLResponse)
@app.get("/patient_record.html", response_class=HTMLResponse)
@app.get("/patient_records", response_class=HTMLResponse)
@app.get("/patient_records.html", response_class=HTMLResponse)
def patient_record_page(request: Request):
    # 🔒 COOKIE SECURITY CHECK: Agar login token nahi hai toh login page par bhejo
    if not request.cookies.get("admin_token"):
        return RedirectResponse(url="/admin_login", status_code=303)

    return templates.TemplateResponse("patient_record.html", {"request": request})

# @app.get("/patient_portal", response_class=HTMLResponse)
# @app.get("/patient_portal.html", response_class=HTMLResponse)
# def patient_portal_page(request: Request, uuid: str = None):
#     # Connection aur Cursor create karein
#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True)
    
#     # Database se patient fetch karein
#     cursor.execute("SELECT * FROM patients WHERE uuid = %s", (uuid,))
#     patient = cursor.fetchone()
    
#     # Clean up (connection close karein)
#     cursor.close()
#     conn.close()

#     # Agar patient na mile toh login page par redirect karein
#     if not patient:
#         return RedirectResponse(url="/patient_login.html")

#     # Patient data ke saath portal render karein
#     return templates.TemplateResponse("patient_portal.html", {
#         "request": request,
#         "patient": patient,
#         "patient_uuid": uuid
#     })


# --- PATIENT SUB-MODULES ---

# @app.get("/blood_reports", response_class=HTMLResponse)
# @app.get("/blood_reports.html", response_class=HTMLResponse)
# def blood_reports_page(request: Request):
#     if not request.session.get("patient_id"):
#         return RedirectResponse(url="/patient_login", status_code=status.HTTP_303_SEE_OTHER)
#     return templates.TemplateResponse("blood_reports.html", {"request": request})


# @app.get("/patient_history", response_class=HTMLResponse)
# @app.get("/patient_history.html", response_class=HTMLResponse)
# def patient_history_page(request: Request):
#     if not request.session.get("patient_id"):
#         return RedirectResponse(url="/patient_login", status_code=status.HTTP_303_SEE_OTHER)
#     return templates.TemplateResponse("patient_history.html", {"request": request})


# @app.get("/Book_appointment_p", response_class=HTMLResponse)
# @app.get("/Book_appointment_p.html", response_class=HTMLResponse)
# def book_appointment_page(request: Request):
#     if not request.session.get("patient_id"):
#         return RedirectResponse(url="/patient_login", status_code=status.HTTP_303_SEE_OTHER)
#     return templates.TemplateResponse("Book_appointment_p.html", {"request": request})


# @app.get("/feedback_page", response_class=HTMLResponse)
# @app.get("/feedback_page.html", response_class=HTMLResponse)
# def feedback_page(request: Request):
#     # if not request.session.get("patient_id"):
#     #     return RedirectResponse(url="/feedback_page", status_code=status.HTTP_303_SEE_OTHER)
#     return templates.TemplateResponse("feedback_page.html", {"request": request})

# --- DOCTOR & RECEPTION SUB-MODULES ---



@app.get("/doctor_patient_report", response_class=HTMLResponse)
@app.get("/doctor_patient_report.html", response_class=HTMLResponse)
def doctor_patient_report(request: Request):
    
    # Session check: Check karein ke session mein doctor_id mojood hai ya nahi
    if not request.session.get("doctor_id"):
        return RedirectResponse(url="/doctor_login", status_code=status.HTTP_303_SEE_OTHER)
    
    return templates.TemplateResponse("doctor_patient_report.html", {"request": request})

@app.get("/appoint_accept", response_class=HTMLResponse)
@app.get("/appoint_accept.html", response_class=HTMLResponse)
def appoint_accept_page(request: Request):
    if not request.session.get("doctor_id") and not request.session.get("reception_id"):
        return RedirectResponse(url="/doctor_login", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("appoint_accept.html", {"request": request})

# --- LAB SUB-MODULES ---

@app.get("/lab_reports", response_class=HTMLResponse)
@app.get("/lab_reports.html", response_class=HTMLResponse)
def lab_reports_page(request: Request):
    if not request.session.get("lab_id") and not request.session.get("doctor_id"):
        return RedirectResponse(url="/lab_login", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("lab_reports.html", {"request": request})

# --- PUBLIC ACCESSIBLE ROUTES ---

@app.get("/about_page", response_class=HTMLResponse)
@app.get("/about_page.html", response_class=HTMLResponse)
def about_page(request: Request):
    return templates.TemplateResponse("about_page.html", {"request": request})

@app.get("/staff_cont", response_class=HTMLResponse)
@app.get("/staff_cont.html", response_class=HTMLResponse)
def staff_cont_page(request: Request):
    return templates.TemplateResponse("staff_cont.html", {"request": request})

@app.get("/doctors_list", response_class=HTMLResponse)
@app.get("/doctors_list.html", response_class=HTMLResponse)
def doctors_list_page(request: Request):
    return templates.TemplateResponse("doctors_list.html", {"request": request})

@app.get("/blood_bank", response_class=HTMLResponse)
@app.get("/blood_bank.html", response_class=HTMLResponse)
def blood_bank_page(request: Request):
    return templates.TemplateResponse("blood_bank.html", {"request": request})

@app.get("/blood_donor", response_class=HTMLResponse)
@app.get("/blood_donor.html", response_class=HTMLResponse)
def blood_donor_page(request: Request):
    return templates.TemplateResponse("blood_donor.html", {"request": request})

@app.get("/feedback_page", response_class=HTMLResponse)
@app.get("/feedback_page.html", response_class=HTMLResponse)
def feedback_page(request: Request):
    return templates.TemplateResponse("feedback_page.html", {"request": request})


#=====================================================================
# Admin Salaries
#=====================================================================   

# Request Body Schema
class SalaryUpdateSchema(BaseModel):
    employee_id: int
    status: str

# Salary Status Update Route
@app.post("/admin/update-salary-status")
async def update_salary_status(data: SalaryUpdateSchema):
    try:
        db = get_db_connection()  # Aapka existing DB connection function
        cursor = db.cursor()

        if data.status == "Paid":
            query = "UPDATE salaries SET status = %s, last_paid_date = %s WHERE id = %s"
            values = (data.status, date.today(), data.employee_id)
        else:
            query = "UPDATE salaries SET status = %s, last_paid_date = NULL WHERE id = %s"
            values = (data.status, data.employee_id)

        cursor.execute(query, values)
        db.commit()

        cursor.close()
        db.close()
        return {"status": "success", "message": "Salary status updated"}

    except Exception as e:
        print(f"❌ Salary Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))




#=====================================================================
# Admin
#=====================================================================
def encode_uuid(uuid_str: str) -> str:
    """Raw UUID ko URL-safe hash/encoded string mein convert karta hai"""
    if not uuid_str or uuid_str == "-": 
        return "-"
    encoded = base64.urlsafe_b64encode(uuid_str.encode()).decode().rstrip("=")
    return encoded

def decode_uuid(hashed_str: str) -> str:
    """Hashed URL parameter ko wapas original UUID mein decode karta hai"""
    if not hashed_str or hashed_str == "-": 
        return "-"
    padding = "=" * ((4 - len(hashed_str) % 4) % 4)
    return base64.urlsafe_b64decode((hashed_str + padding).encode()).decode()


@app.on_event("startup")
def startup_event():
    create_tables()

@app.post("/admin/login")
@limiter.limit("5/hour")
def admin_login(request: Request, response: Response, user_credentials: OAuth2PasswordRequestForm = Depends()):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT id, username, hashed_password, uuid FROM admins WHERE username = %s"
    cursor.execute(query, (user_credentials.username,))
    admin = cursor.fetchone()

    cursor.close()
    conn.close()

    # 1. Invalid credentials check
    if not admin or not verify_password(user_credentials.password, admin["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Username or Password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 2. UUID safe extraction & fallback
    admin_uuid = admin.get("uuid")
    if not admin_uuid:
        import uuid as uuid_lib
        admin_uuid = str(uuid_lib.uuid4())

    # 3. Always define hashed_uuid before return
    hashed_uuid = encode_uuid(str(admin_uuid))

    # 4. Token & Cookie setup
    access_token = create_access_token(data={"sub": admin["username"]})
    response.set_cookie(key="admin_token", value=access_token, httponly=True, max_age=3600)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "uuid": hashed_uuid,
        "redirect_url": f"/admin_portal?uuid={hashed_uuid}"
    }

 
#=======================================================================================
#Admin Doctor View and Delete
#=======================================================================================

@app.get("/admin_portal")
def get_admin_portal(request: Request, uuid: str = None):
    token = request.cookies.get("admin_token")
    if not token:
        return RedirectResponse(url="/admin_login", status_code=status.HTTP_303_SEE_OTHER)

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM doctors")
    doctors_list = cursor.fetchall()
    cursor.close()
    conn.close()

    return templates.TemplateResponse(
        "admin_portal.html", 
        {"request": request, "doctors": doctors_list, "admin_uuid": uuid}
    )

# 2. Patient Records Clean Route
@app.get("/patient_records")
def get_patient_records_page(request: Request, uuid: str = None):
    token = request.cookies.get("admin_token")
    if not token:
        return RedirectResponse(url="/admin_login", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse("patient_records.html", {"request": request})


  
# @app.delete("/admin/delete-doctor/{doctor_id}")
# def delete_doctor(doctor_id: int, request:Request):
#     token = request.cookies.get("admin_token")
#     if not token:
#         return {"error": "Not authenticated"}, 401
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute("DELETE FROM doctors WHERE id = %s", (doctor_id,))
#     conn.commit()
#     cursor.close()
#     conn.close()
#     return {"message": "Doctor deleted successfully"}





# ================= 1. CORS POLICY =================
from datetime import datetime
ALLOWED_ORIGINS = [
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:8000",
    "http://127.0.0.1:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS, 
    allow_credentials=True,
    allow_methods=["*"],       
    allow_headers=["*"],
)

@app.get("/api/v1/patients/records")
def get_patient_records(request: Request, period: str = "month"):
    if not request.cookies.get("admin_token"):
        return {
            "status": "error",
            "message": "Unauthorized access. Please log in first.",
            "data": []
        }

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True) if hasattr(conn, "cursor") else conn.cursor()

        # Dynamic WHERE clause
        if period == "today":
            where_clause = "WHERE DATE(registration_date) = CURDATE()"
        elif period == "week":
            where_clause = "WHERE YEARWEEK(registration_date, 1) = YEARWEEK(CURDATE(), 1)"
        elif period == "month":
            where_clause = "WHERE MONTH(registration_date) = MONTH(CURDATE()) AND YEAR(registration_date) = YEAR(CURDATE())"
        elif period == "all":
            where_clause = ""
        elif "-" in period:
            parts = period.split("-")
            year_val, month_val = parts[0], parts[1]
            where_clause = f"WHERE MONTH(registration_date) = {month_val} AND YEAR(registration_date) = {year_val}"
        else:
            where_clause = "WHERE MONTH(registration_date) = MONTH(CURDATE()) AND YEAR(registration_date) = YEAR(CURDATE())"

        # SELECT * se uuid column bhi automatic aa jayega
        query = f"""
            SELECT * FROM patients
            {where_clause}
            ORDER BY registration_date DESC
        """

        cursor.execute(query)
        records = cursor.fetchall()

        cursor.close()
        conn.close()

        formatted_data = []
        for r in records:
            if isinstance(r, dict):
                # Flexible extraction for column name fallbacks
                p_uuid = r.get("uuid") or "-"  # 👈 UUID Extract
                p_id = r.get("patient_id") or r.get("id") or "-"
                p_name = r.get("name") or r.get("patient_name") or r.get("full_name") or "-"
                p_phone = r.get("phone") or r.get("phone_number") or "-"
                p_cnic = r.get("cnic") or "-"
                p_age = r.get("age") or "-"
                p_source = str(r.get("source") or "reception").lower()
                
                raw_date = r.get("registration_date") or r.get("created_at") or r.get("date")
                if hasattr(raw_date, "strftime"):
                    p_date = raw_date.strftime("%Y-%m-%d")
                else:
                    p_date = str(raw_date)[:10] if raw_date else "-"
                    
                p_gender = r.get("gender") or "-"
                raw_uuid = r.get("uuid") or "-"
                p_uuid = encode_uuid(str(raw_uuid)) if raw_uuid != "-" else "-"

                formatted_data.append({
                    "uuid": p_uuid,  # 👈 Response mein Add kiya
                    "patient_id": p_id,
                    "name": p_name,
                    "phone": p_phone,
                    "cnic": p_cnic,
                    "age": p_age,
                    "source": p_source,
                    "date": p_date,
                    "gender": p_gender
                })
            else:
                formatted_data.append({
                    "uuid": r[8] if len(r) > 8 else "-",  # Fallback for tuple
                    "patient_id": r[0] if len(r) > 0 else "-",
                    "name": r[1] if len(r) > 1 else "-",
                    "phone": r[2] if len(r) > 2 else "-",
                    "cnic": r[3] if len(r) > 3 else "-",
                    "age": r[4] if len(r) > 4 else "-",
                    "source": str(r[5]).lower() if len(r) > 5 and r[5] else 'reception',
                    "date": str(r[6])[:10] if len(r) > 6 and r[6] else "-",
                    "gender": r[7] if len(r) > 7 else "-"
                })

        return {
            "status": "success",
            "data": formatted_data
        }

    except Exception as e:
        if conn and conn.is_connected():
            conn.close()
        print("Patient Records API Error:", str(e))
        return {
            "status": "error",
            "message": str(e),
            "data": []
        }


    

# ================= 3. GRAPH DATA ENDPOINT =================
@app.get("/api/v1/patients/chart-data")
def get_patient_chart_data():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            SELECT 
                FLOOR((DAY(registration_date) - 1) / 7) + 1 AS week_num,
                COUNT(*) AS total_patients
            FROM patients
            WHERE MONTH(registration_date) = MONTH(CURDATE()) 
              AND YEAR(registration_date) = YEAR(CURDATE())
            GROUP BY week_num
            ORDER BY week_num ASC
        """

        cursor.execute(query)
        rows = cursor.fetchall()

        cursor.close()
        conn.close()

        weeks_map = {"Week 1": 0, "Week 2": 0, "Week 3": 0, "Week 4": 0}

        for row in rows:
            week_num = int(row[0]) if row[0] else 1
            count = int(row[1]) if row[1] else 0
            label = f"Week {week_num}"
            if label in weeks_map:
                weeks_map[label] = count

        # Safe date string formatting
        current_month_year = datetime.now().strftime("%B %Y")

        return {
            "status": "success",
            "month_year": current_month_year,
            "labels": list(weeks_map.keys()),
            "data": list(weeks_map.values())
        }

    except Exception as e:
        if conn and conn.is_connected():
            conn.close()
        print("Backend Chart Error:", str(e))
        return {
            "status": "error",
            "month_year": "Current Month",
            "labels": ["Week 1", "Week 2", "Week 3", "Week 4"],
            "data": [0, 0, 0, 0]
        }

# ==========================================
# FIXING 404 ERRORS & SERVING HTML PAGES
# ==========================================


# 2. Faltu Favicon 404 Error ko chup karane ke liye
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return {"status": "ok"}    
#========================================================================================
@app.get("/")
def home():
    return {"message": "Saviour Crest Hospital Backend Running!"}
#================================================================
# Admin Doctor register
#================================================================
class DoctorCreate(BaseModel):
    full_name: str
    pmdc_id: str
    cnic: str
    email: EmailStr
    specialization: str
    password: str

    # 1. Doctor Register Endpoint (Salaries table Entry ke sath)
@app.post("/admin/register-doctor")
def register_doctor(doctor: DoctorCreate):
    hashed_pwd = hash_password(doctor.password)
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Doctors table mein insert
        sql = """INSERT INTO doctors 
                (pmdc_id, full_name, cnic, email, specialization, password_hash) 
                VALUES (%s, %s, %s, %s, %s, %s)"""
        values = (doctor.pmdc_id, doctor.full_name, doctor.cnic, doctor.email, doctor.specialization, hashed_pwd)
        cursor.execute(sql, values)
        
        doctor_id = cursor.lastrowid  # Naye doctor ki ID

        # Salaries table mein Auto-Insert
        sal_sql = """INSERT INTO salaries 
                    (employee_name, role, department, monthly_salary, status, doctor_id) 
                    VALUES (%s, %s, %s, %s, %s, %s)"""
        cursor.execute(sal_sql, (doctor.full_name, "Doctor", doctor.specialization, 250000.00, "Unpaid", doctor_id))

        conn.commit()
        return {"status": "success", "message": f"Doctor {doctor.full_name} registered successfully!"}

    except mysql.connector.IntegrityError:
        raise HTTPException(status_code=400, detail="Doctor with this PMDC ID, CNIC, or Email already exists.")
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()


# 2. Doctor Delete Endpoint (Salaries cleanup ke sath)
@app.delete("/admin/delete-doctor/{doctor_id}")
def delete_doctor(doctor_id: int, request: Request):
    token = request.cookies.get("admin_token")
    if not token:
        return {"error": "Not authenticated"}, 401
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Pehle salaries table se delete karein
    cursor.execute("DELETE FROM salaries WHERE doctor_id = %s", (doctor_id,))
    # Phir doctors table se delete karein
    cursor.execute("DELETE FROM doctors WHERE id = %s", (doctor_id,))
    
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": "Doctor deleted successfully"}

# @app.post("/admin/register-doctor/")
# def register_doctor(doctor: DoctorCreate):
#     hashed_pwd = hash_password(doctor.password)

#     try:
#         conn = get_db_connection()  
#         cursor = conn.cursor()

#         sql = """INSERT INTO doctors 
#                  (pmdc_id, full_name, cnic, email, specialization, password_hash) 
#                  VALUES (%s, %s, %s, %s, %s, %s)"""
        
#         values = (
#             doctor.pmdc_id, 
#             doctor.full_name, 
#             doctor.cnic, 
#             doctor.email,
#             doctor.specialization, 
#             hashed_pwd
#         )

#         cursor.execute(sql, values)
#         conn.commit()

#         return {"status": "success", "message": f"Doctor {doctor.full_name} registered successfully!"}

#     except mysql.connector.IntegrityError:
#         raise HTTPException(status_code=400, detail="Doctor with this PMDC ID, CNIC, or Email already exists.")
#     except Exception as err:
#         raise HTTPException(status_code=500, detail=str(err))
#     finally:
#         if 'conn' in locals() and conn.is_connected():
#             cursor.close()
#             conn.close()

# =================================================================
# PATIENT ROUTES
# =================================================================

# =====================================================================
# 2. PROTECTED PORTALS (Unified Logic & Session Checks)
# =====================================================================

# --- PATIENT PORTAL ---
# @app.get("/patient_portal/{patient_uuid}", response_class=HTMLResponse)
# # @app.get("/patient_portal.html", response_class=HTMLResponse)
# def patient_portal_page(request: Request):
#     patient_id = request.session.get("patient_id")
#     if not patient_id:
#         return RedirectResponse(url="/patient_login")

#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True)
#     cursor.execute("SELECT * FROM patients WHERE id = %s", (patient_id,))
#     patient = cursor.fetchone()
#     cursor.close()
#     conn.close()

#     if not patient:
#         request.session.pop("patient_id", None)
#         return RedirectResponse(url="/patient_login")
    
#     safe_patient = serialize_db_data(patient)

#     return templates.TemplateResponse("patient_portal.html", {"request": request, "patient": patient})

# ----------------------------------------------------------------
# LOGOUT — GET
# ----------------------------------------------------------------
# @app.get("/logout")
# def logout(request: Request):
#     request.session.clear()
#     return JSONResponse(content={"success": True, "message": "Logged out successfully!"})

# ----------------------------------------------------------------
# SIGNUP — POST /signup/patient
# ----------------------------------------------------------------
@app.post("/signup/patient")
def signup_patient(
    full_name: str = Form(...),
    email: str = Form(...),
    gender: str = Form(...),
    age: int = Form(...),
    phone: str = Form(...),
    password: str = Form(...)
):
    hashed_password = pwd_context.hash(password)
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # 1. Check karein ki kya patient Phone ya Email se pehle se database mein hai
        cursor.execute(
            "SELECT id, patient_id, password_hash FROM patients WHERE phone = %s OR email = %s", 
            (phone, email)
        )
        existing_patient = cursor.fetchone()

        if existing_patient:
            # Case A: User ne online signup pehle se kar rakha hai (password_hash exists)
            if existing_patient.get("password_hash"):
                return JSONResponse(
                    status_code=400, 
                    content={"success": False, "message": "Phone or Email is already registered. Please login."}
                )
            
            # Case B: Walk-in patient (Reception ne add kia tha, password_hash NULL tha)
            # Purani PT-ID aur record retain karke password update karein
            existing_id = existing_patient["id"]
            cursor.execute("""
                UPDATE patients 
                SET full_name = %s, email = %s, gender = %s, age = %s, phone = %s, password_hash = %s 
                WHERE id = %s
            """, (full_name, email, gender, age, phone, hashed_password, existing_id))
            
            conn.commit()
            return JSONResponse(content={"success": True, "message": "Walk-in profile linked successfully! You can now login."})

        else:
            # Case C: Bilkul Naya Patient (Database mein koi record nahi tha)
            cursor.execute(
                "INSERT INTO patients (full_name, email, gender, age, phone, password_hash) VALUES (%s, %s, %s, %s, %s, %s)",
                (full_name, email, gender, age, phone, hashed_password)
            )
            new_id = cursor.lastrowid

            # Formatted PT- ID Set Karein
            formatted_id = f"PT-{10000 + new_id}"
            cursor.execute(
                "UPDATE patients SET patient_id = %s WHERE id = %s",
                (formatted_id, new_id)
            )

            conn.commit()
            return JSONResponse(content={"success": True, "message": "Signed up successfully!"})

    except Exception as e:
        if conn:
            conn.rollback()
        print("❌ Signup Error Details:", str(e))
        return JSONResponse(status_code=500, content={"success": False, "message": "Server error. Please try again."})

    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

# ----------------------------------------------------------------
# LOGIN — POST /login/patient
# ----------------------------------------------------------------
@app.post("/login/patient")
def login_patient(request: Request, email: str = Form(...), password: str = Form(...)):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM patients WHERE email = %s", (email,))
        patient = cursor.fetchone()

        # Check 1: Patient exists
        if not patient or not patient.get("password_hash"):
            return JSONResponse(status_code=401, content={"success": False, "message": "Invalid email or password."})

        # Check 2: Password Match
        stored_hash = patient["password_hash"]
        is_password_valid = False
        try:
            is_password_valid = pwd_context.verify(password, stored_hash)
        except Exception:
            is_password_valid = (password == stored_hash)

        if not is_password_valid:
            return JSONResponse(status_code=401, content={"success": False, "message": "Invalid email or password."})

        # Session Save (Fixed: str format instead of int)
        real_id = patient.get("patient_id") or patient.get("id")
        request.session["patient_id"] = str(real_id)

        # Deterministic Hashed UUID
        patient_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(real_id)))

        return JSONResponse(content={
            "success": True,
            "message": "Login successful!",
            "redirect": f"/patient_portal?uuid={patient_uuid}"
        })

    except Exception as e:
        print("❌ Login Error Details:", str(e))
        return JSONResponse(status_code=500, content={"success": False, "message": f"Server error: {str(e)}"})
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/patient_login.html", status_code=status.HTTP_303_SEE_OTHER)            


# Pydantic Schemas
class ApproveAppointmentSchema(BaseModel):
    appointment_id: str
    confirmed_date: str
    confirmed_time: str

class RejectAppointmentSchema(BaseModel):
    appointment_id: str


# ---------------------------------------------------------
# A. Page Render Routes
# ---------------------------------------------------------

# @app.get("/dashboard/patient", response_class=HTMLResponse)
# async def render_patient_dashboard(request: Request):
#     return templates.TemplateResponse("patient_portal.html", {"request": request})

# @app.get("/dashboard/patient", response_class=HTMLResponse)
# async def render_patient_dashboard(request: Request):
#     # 1. Session se patient ID check karein
#     patient_id = request.session.get("patient_id")
    
#     # Agar user logged in nahi hai toh login page par redirect karein
#     if not patient_id:
#         return RedirectResponse(url="/login", status_code=303)

#     # 2. Database se patient details fetch karein
#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True)
#     cursor.execute("SELECT * FROM patients WHERE id = %s", (patient_id,))
#     patient = cursor.fetchone()
#     cursor.close()
#     conn.close()

#     # 3. Template response mein "patient" key pass karein
#     return templates.TemplateResponse("patient_portal.html", {
#         "request": request, 
#         "patient": patient
#     })



# --- PATIENT DASHBOARD / PORTAL (WITH HASHED UUID) ---
# @app.get("/dashboard/patient", response_class=HTMLResponse)
# @app.get("/patient_portal", response_class=HTMLResponse)
# @app.get("/patient_portal.html", response_class=HTMLResponse)
# async def render_patient_dashboard(request: Request, uuid_param: Optional[str] = Query(None, alias="uuid")):
#     # 1. Session check
#     patient_id = request.session.get("patient_id")
#     if not patient_id:
#         return RedirectResponse(url="/patient_login.html", status_code=status.HTTP_303_SEE_OTHER)

#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True)

#     try:
#         # 2. Database se patient details fetch karein (id aur patient_id dono se check)
#         cursor.execute(
#             "SELECT * FROM patients WHERE id = %s OR patient_id = %s", 
#             (patient_id, patient_id)
#         )
#         patient = cursor.fetchone()

#         if not patient:
#             return RedirectResponse(url="/patient_login.html", status_code=status.HTTP_303_SEE_OTHER)

#         real_patient_id = patient.get("patient_id") or patient.get("id")

#         # 3. Deterministic Hashed UUID Generate Karein
#         patient_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(real_patient_id)))

#         # 4. Agar URL me 'uuid' nahi hai toh Redirect karein
#         if not uuid_param:
#             return RedirectResponse(
#                 url=f"/dashboard/patient?uuid={patient_uuid}", 
#                 status_code=status.HTTP_302_FOUND
#             )

#         safe_patient = serialize_db_data(patient)

#         return templates.TemplateResponse(
#             "patient_portal.html",
#             {
#                 "request": request,
#                 "patient": safe_patient,
#                 "patient_id": real_patient_id,
#                 "patient_uuid": patient_uuid
#             }
#         )
#     finally:
#         if cursor:
#             cursor.close()
#         if conn and conn.is_connected():
#             conn.close()

# @app.get("/patient_portal", response_class=HTMLResponse)
# @app.get("/patient_portal.html", response_class=HTMLResponse)
# @app.get("/patient_portal/{patient_uuid_path}", response_class=HTMLResponse)
# @app.get("/dashboard/patient", response_class=HTMLResponse)
# @app.get("/dashboard/patient/{patient_uuid_path}", response_class=HTMLResponse)
# async def render_patient_dashboard(
#     request: Request,
#     uuid_param: Optional[str] = Query(None, alias="uuid"),
#     patient_uuid_path: Optional[str] = None
# ):
#     # 1. Session check
#     patient_id = request.session.get("patient_id")
#     if not patient_id:
#         return RedirectResponse(url="/patient_login.html", status_code=status.HTTP_303_SEE_OTHER)

#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True)

#     try:
#         # 2. Database se patient details fetch karein
#         cursor.execute(
#             "SELECT * FROM patients WHERE id = %s OR patient_id = %s",
#             (patient_id, patient_id)
#         )
#         patient = cursor.fetchone()

#         if not patient:
#             return RedirectResponse(url="/patient_login.html", status_code=status.HTTP_303_SEE_OTHER)

#         real_patient_id = patient.get("patient_id") or patient.get("id")

#         # 3. Deterministic Hashed UUID Generate Karein
#         patient_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(real_patient_id)))

#         # 4. Path Param ya Query Param me se UUID extract karein
#         current_uuid = patient_uuid_path or uuid_param

#         # FIX: Agar UUID missing ho, 'None' string ho, ya exact hashed UUID se match na kare toh auto-correct karein
#         if not current_uuid or str(current_uuid).lower() in ["none", "null"] or current_uuid != patient_uuid:
#             return RedirectResponse(
#                 url=f"/patient_portal?uuid={patient_uuid}",
#                 status_code=status.HTTP_302_FOUND
#             )

#         safe_patient = serialize_db_data(patient)

#         return templates.TemplateRespons (
#             "patient_portal.html",
#             {
#                 "request": request,
#                 "patient": safe_patient,
#                 "patient_id": real_patient_id,
#                 "patient_uuid": patient_uuid
#             }
#         )
#     finally:
#         if cursor:
#             cursor.close()
#         if conn and conn.is_connected():
#             conn.close()


@app.get("/patient_portal", response_class=HTMLResponse)
@app.get("/patient_portal.html", response_class=HTMLResponse)
@app.get("/patient_portal/{patient_uuid_path}", response_class=HTMLResponse)
@app.get("/dashboard/patient", response_class=HTMLResponse)
@app.get("/dashboard/patient/{patient_uuid_path}", response_class=HTMLResponse)
async def render_patient_dashboard(
    request: Request,
    uuid_param: Optional[str] = Query(None, alias="uuid"),
    patient_uuid_path: Optional[str] = None
):
    # 1. Session check
    patient_id = request.session.get("patient_id")
    if not patient_id:
        return RedirectResponse(url="/patient_login.html", status_code=status.HTTP_303_SEE_OTHER)

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # 2. Database se patient details fetch karein
        cursor.execute(
            "SELECT * FROM patients WHERE id = %s OR patient_id = %s",
            (patient_id, patient_id)
        )
        patient = cursor.fetchone()

        # 2. Database se patient details fetch karein
        cursor.execute(
            "SELECT * FROM patients WHERE id = %s OR patient_id = %s",
            (patient_id, patient_id)
        )
        patient = cursor.fetchone()
        if not patient:
            return RedirectResponse(url="/patient_login.html", status_code=status.HTTP_303_SEE_OTHER)

        cursor.execute("SELECT id, full_name, specialization FROM doctors")
        doctors_list = cursor.fetchall()

        

        real_patient_id = patient.get("patient_id") or patient.get("id")
        patient_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(real_patient_id)))

        current_uuid = patient_uuid_path or uuid_param

        # Fix missing/incorrect UUID in URL
        if not current_uuid or str(current_uuid).lower() in ["none", "null"] or current_uuid != patient_uuid:
            return RedirectResponse(
                url=f"/patient_portal?uuid={patient_uuid}",
                status_code=status.HTTP_302_FOUND
            )

        safe_patient = serialize_db_data(patient) if 'serialize_db_data' in globals() else patient

        # Safe template response for all FastAPI versions
        try:
            return templates.TemplateResponse(
                request=request,
                name="patient_portal.html",
                context={
                    "patient": safe_patient,
                    "patient_id": real_patient_id,
                    "patient_uuid": patient_uuid,
                    "doctors":doctors_list
                }
            )
        except TypeError:
            return templates.TemplateResponse(
                "patient_portal.html",
                {
                    "request": request,
                    "patient": safe_patient,
                    "patient_id": real_patient_id,
                    "patient_uuid": patient_uuid,
                    "doctors":doctors_list
                }
            )

    except Exception as e:
        print("❌ Dashboard Rendering Error:", str(e))
        return HTMLResponse(content=f"<h3>Server Error: {str(e)}</h3>", status_code=500)

    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


@app.get("/book_appointment", response_class=HTMLResponse)
async def render_booking_page(request: Request, doctor_id: str = None):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if doctor_id:
          cursor.execute("SELECT * FROM doctors WHERE doctor_uuid = %s OR id = %s", (doctor_id, doctor_id,))
    else:
        cursor.execute("SELECT * FROM doctors LIMIT 1")
    doctor = cursor.fetchone()
    cursor.close()
    conn.close()
    return templates.TemplateResponse("Book_appointment_p.html", {"request": request, "doctor": doctor})


# ✅ Doctor Appointment Requests Page (Fix: appoint_accept.html referenced)
@app.get("/doctor_appointment", response_class=HTMLResponse)
async def render_doctor_appointments(request: Request, doctor_id: int = None):
    active_id = doctor_id or request.session.get("doctor_id") 
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM doctors WHERE id = %s", (active_id,))
    doctor = cursor.fetchone()
    cursor.close()
    conn.close()

    if not doctor:
        doctor = {"id": 1, "full_name": "Dr. A. Karim", "specialization": "Cardiologist", "pmdc_id": "PMC-84920"}

    # Exact filename match:
    return templates.TemplateResponse("appoint_accept.html", {"request": request, "doctor": doctor})


# =====================================================================
# 2. PROTECTED PORTALS (Unified Logic & Session Checks)
# =====================================================================

@app.get("/doctor_portal", response_class=HTMLResponse)
@app.get("/doctor_portal.html", response_class=HTMLResponse)
def doctor_portal_page(request: Request):
    doctor_id = request.session.get("doctor_id")
    
    # 1. Session check
    if not doctor_id:
        return RedirectResponse(url="/doctor_login")

    # 🔒 2. HASHED URL CHECK: Agar URL me ?ref= parameter nahi hai to hashed token generate karke redirect karein
    ref_token = request.query_params.get("ref")
    if not ref_token:
        # Base64 encoded token from doctor_id & random UUID
        raw_payload = f"doc_{doctor_id}_{uuid.uuid4().hex[:10]}"
        hashed_ref = base64.b64encode(raw_payload.encode()).decode().rstrip("=")
        return RedirectResponse(url=f"/doctor_portal?ref={hashed_ref}")

    # 3. Database lookup for logged in doctor
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM doctors WHERE id = %s", (doctor_id,))
    doctor = cursor.fetchone()
    cursor.close()
    conn.close()

    if not doctor:
        request.session.pop("doctor_id", None)
        return RedirectResponse(url="/doctor_login")

    return templates.TemplateResponse("doctor_portal.html", {"request": request, "doctor": doctor})

# ---------------------------------------------------------
# B. Booking API
# ---------------------------------------------------------

@app.post("/api/appointments/book")
def book_appointment(
    patient_id: str = Form(...), 
    doctor_id: str = Form(...),
    appt_date: str = Form(...),
    appt_time: str = Form(...),
    amount_paid: str = Form(...),
    payment_proof: UploadFile = File(...)
):
    upload_folder = "static/uploads"
    os.makedirs(upload_folder, exist_ok=True)
    # file_path = f"/{upload_folder}/{payment_proof.filename}"
    
    # with open(f"static/uploads/{payment_proof.filename}", "wb") as buffer:
    #     shutil.copyfileobj(payment_proof.file, buffer)
    file_extension = payment_proof.filename.split(".")[-1]
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = f"{upload_folder}/{unique_filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(payment_proof.file, buffer)

    # Unique Appointment UUID
    appointment_uuid = str(uuid.uuid4())

    conn = get_db_connection()
    cursor = conn.cursor()
    
    # query = """
    #     INSERT INTO appointments 
    #     (patient_id, doctor_id, appt_date, appt_time, amount_paid, payment_proof_path, status)
    #     VALUES (%s, %s, %s, %s, %s, %s, 'Pending')
    # """
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. 'PT-60378' ke zariye real integer ID (e.g. 26) fetch karein
    cursor.execute("SELECT id FROM patients WHERE patient_id = %s", (patient_id,))
    patient_row = cursor.fetchone()

    if not patient_row:
        cursor.close()
        conn.close()
        return {"status": "error", "message": "Patient record not found"}

    real_patient_id = patient_row[0]

    # 2. Appointments table mein record insert karein
    query = """
        INSERT INTO appointments 
        (uuid, patient_id, doctor_id, appt_date, appt_time, amount_paid, payment_proof_path, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, 'Pending')
    """

    cursor.execute(query, (appointment_uuid, real_patient_id, doctor_id, appt_date, appt_time, amount_paid, file_path))
    conn.commit()
    
    cursor.close()
    conn.close()
    return {"status": "success", "message": "Appointment booked and is pending doctor approval!","appointment_uuid": appointment_uuid}


# ---------------------------------------------------------
# C. Doctor Portal Actions APIs
# ---------------------------------------------------------

@app.get("/api/doctor/appointments")
def get_pending_appointments(request: Request, doctor_id: int = None):
    doc_id = doctor_id or request.session.get("doctor_id") 

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # 1. JOIN mein 'a.patient_id = p.id' kar diya hai
        # 2. 'p.full_name' likha hai (bina 'AS' ke taaki JS mein undefined na aaye)
        query = """
            SELECT 
                a.appointment_id,
                a.patient_id,
                p.full_name,
                a.appt_date AS appointment_date,
                a.appt_time AS appointment_time,
                a.amount_paid AS amount,
                'Paid' AS payment_status,
                a.payment_proof_path AS payment_proof,
                a.status
            FROM appointments a
            LEFT JOIN patients p ON a.patient_id = p.id
            WHERE a.doctor_id = %s AND a.status = 'Pending'
            ORDER BY a.appointment_id DESC
        """
        cursor.execute(query, (doc_id,))
        appointments = cursor.fetchall()

        for appt in appointments:
            # Name undefined na aaye uske liye fallback logic
            appt["full_name"] = appt.get("full_name") or "Unknown Patient"
            
            # ID ko 5 digits ka banane ke liye (e.g. 18 se 00018)
            # Ab frontend par 'PT-00018' type show hoga
            # raw_id = appt.get("patient_id")
            # if raw_id:
            #     appt["patient_id"] = str(raw_id).zfill(5)
            # Line 874-876 replace karein:
            raw_id = appt.get("patient_uuid") or appt.get("patient_id")
            if raw_id:
                   appt["patient_id"] = str(raw_id)  # Raw UUID string pass hogi (.zfill hata diya)
            
            # Date aur Time fix
            if appt.get("appointment_date"):
                appt["appointment_date"] = str(appt["appointment_date"])
            if appt.get("appointment_time"):
                appt["appointment_time"] = str(appt["appointment_time"])

            return {"status": "success", "appointments": appointments}
    except Exception as e:
        print(f"❌ ERROR IN DOCTOR APPOINTMENTS: {e}")
        return {"status": "error", "message": str(e)}

    finally:
        cursor.close()
        conn.close()

@app.post("/api/appointments/approve")
async def approve_appointment(payload: ApproveAppointmentSchema):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 🔥 YAHAN CHANGE KIYA HAI: appt_date ki jagah confirmed_date likha hai
        query = """
            UPDATE appointments 
            SET status = 'Confirmed', 
                confirmed_date = %s, 
                confirmed_time = %s 
            WHERE uuid = %s
        """

              
     
               
        cursor.execute(query, (payload.confirmed_date, payload.confirmed_time, payload.appointment_id))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return {"status": "success", "message": "Appointment confirmed successfully!"}
    except Exception as e:
        print("Approve error:", e)
        raise HTTPException(status_code=500, detail="Database update failed.")

@app.post("/api/appointments/reject")
async def reject_appointment(payload: RejectAppointmentSchema):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = "UPDATE appointments SET status = 'Rejected' WHERE appointment_id = %s"
        cursor.execute(query, (payload.appointment_id,))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return {"status": "success", "message": "Appointment rejected successfully!"}
    except Exception as e:
        print("Reject error:", e)
        raise HTTPException(status_code=500, detail="Database update failed.")

@app.get("/api/patient/my-appointments")
async def get_patient_appointments(request: Request):
    patient_id = request.session.get("user_id") or request.session.get("patient_id")
    
    if not patient_id:
        return {"status": "error", "message": "Patient not logged in"}

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # 1. AUTO-UPDATE (Automation): Guzri hui 'Confirmed/Approved' dates ko 'Completed' mark kar do
        update_query = """
            UPDATE appointments 
            SET status = 'Completed' 
            WHERE appt_date < CURDATE() AND status IN ('Confirmed', 'Approved')
        """
        cursor.execute(update_query)
        conn.commit()

        # 2. FETCH APPOINTMENTS: Ab sirf wo lao jo Completed nahi hain (taaki portal par sirf kaam ki cheez aaye)
        select_query = """
            SELECT 
                a.appointment_id,
                a.patient_id,
                a.status,
                a.confirmed_date,
                a.confirmed_time,
                d.full_name AS doctor_name,
                d.specialization AS specialty
            FROM appointments a
            LEFT JOIN doctors d ON a.doctor_id = d.id
            WHERE a.patient_id = %s AND a.status != 'Completed'
            ORDER BY a.appointment_id DESC
        """
        cursor.execute(select_query, (patient_id,))
        rows = cursor.fetchall()

        formatted_appointments = []
        for row in rows:
            formatted_appointments.append({
                "appointment_id": row.get("appointment_id"),
                "patient_id": row.get("patient_id"),
                "status": row.get("status") or "Pending",
                "appointment_date": str(row.get("appt_date")) if row.get("appt_date") else "",
                "confirmed_time": str(row.get("appt_time")) if row.get("appt_time") else "",
                "doctor_name": row.get("doctor_name") or "Doctor",
                "specialty": row.get("specialty") or "General"
            })
        
        return {"status": "success", "appointments": formatted_appointments}
        
    except Exception as e:
        print(f"❌ DATABASE ERROR: {e}")
        return {"status": "error", "message": str(e)}
        
    finally:
        cursor.close()
        conn.close()

# 2. ADD THIS NEW ROUTE (To delete rejected appointments)
@app.delete("/api/patient/appointments/{appointment_id}")
async def delete_patient_appointment(appointment_id: str, request: Request):
    patient_id = request.session.get("user_id") or request.session.get("patient_id")
    
    if not patient_id:
        return {"status": "error", "message": "Unauthorized"}
        
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Sirf tabhi delete hoga jab status Rejected ho (security ke liye)
        query = "DELETE FROM appointments WHERE (appointment_uuid = %s OR appointment_id = %s) AND patient_id = %s AND status = 'Rejected'"
        cursor.execute(query, (appointment_id, patient_id))
        conn.commit()
        
        if cursor.rowcount > 0:
            return {"status": "success", "message": "Appointment deleted successfully"}
        else:
            return {"status": "error", "message": "Could not delete appointment (may not exist or not rejected)"}
            
    except Exception as e:
        print(f"❌ DELETE ERROR: {e}")
        return {"status": "error", "message": "Database error"}
    finally:
        cursor.close()
        conn.close()
# ==================================================================
# DOCTOR LOGIN ROUTE
# ==================================================================
@app.post("/login_doctor")
def login_doctor(
    request: Request, 
    pmdc_id: str = Form(...), 
    password: str = Form(...)
):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True) 
        
        cursor.execute("SELECT * FROM doctors WHERE pmdc_id = %s", (pmdc_id,))
        doctor = cursor.fetchone()
        
        cursor.close()
        conn.close()

        if not doctor or not verify_password(password, doctor["password_hash"]):
            return JSONResponse(
                status_code=401, 
                content={"success": False, "message": "Invalid PMDC ID or Password."}
            )

        if not doctor.get("is_active", True):
            return JSONResponse(
                status_code=403, 
                content={"success": False, "message": "Your account is currently inactive. Contact Admin."}
            )

            # Safe dictionary & object attribute fetching
        doc_pmdc = doctor.get("pmdc_id") if isinstance(doctor, dict) else getattr(doctor, "pmdc_id", pmdc_id)
        doc_id = doctor.get("id") if isinstance(doctor, dict) else getattr(doctor, "id", None)

        request.session["doctor_id"] = doc_id
        request.session["doctor_pmdc_id"] = doc_pmdc or pmdc_id  # Fallback to login form's input PMDC ID

        return JSONResponse(
            content={"success": True, "message": "Login successful!", "redirect": "/doctor_portal.html"}
        )
        
    except Exception as e:
        print("Login Error:", e)
        return JSONResponse(
            status_code=500, 
            content={"success": False, "message": "Server error. Please try again later."}
        )



# ==================================================================
# DOCTOR LOGOUT ROUTE
# ==================================================================
@app.get("/doctor/logout")
def logout_doctor(request: Request):
    request.session.pop("doctor_id", None)
    return RedirectResponse(url="/doctor_login?logged_out=true")

#=========================================================
#  RECEPTION LOGIN & PORTAL ROUTES 
#=========================================================
# ================= 1. LOGIN & LOGOUT =================

@app.post("/reception_login")
def login_receptionist_route(request: Request, full_name: str = Form(...), staff_id: str = Form(...)):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM receptionists WHERE full_name = %s AND hospital_id = %s", 
        (full_name, staff_id)
    )
    receptionist = cursor.fetchone()
    cursor.close()
    conn.close()

    if receptionist:
        request.session["reception_id"] = receptionist["id"]
        return RedirectResponse(url="/reception_portal?msg=login_success", status_code=303)
    else:
        return RedirectResponse(url="/reception_login?msg=invalid", status_code=303)

# --- RECEPTION PORTAL ---
@app.get("/reception_portal", response_class=HTMLResponse)
@app.get("/reception_portal.html", response_class=HTMLResponse)
def reception_portal_page(request: Request):
    reception_id = request.session.get("reception_id")
    if not reception_id:
        return RedirectResponse(url="/reception_login")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM receptionists WHERE id = %s", (reception_id,))
    reception_data = cursor.fetchone()

    today_date = date.today()

    cursor.execute("SELECT COUNT(id) as today_patients FROM patients WHERE DATE(registration_date) = %s", (today_date,))
    patients_count_result = cursor.fetchone()
    patients_count = patients_count_result["today_patients"] if patients_count_result else 0

    cursor.execute("SELECT COUNT(id) as today_invoices, SUM(amount) as today_revenue FROM invoices WHERE DATE(invoice_date) = %s", (today_date,))
    invoice_data = cursor.fetchone()
    invoices_count = invoice_data["today_invoices"] if invoice_data and invoice_data["today_invoices"] else 0
    today_revenue = invoice_data["today_revenue"] if invoice_data and invoice_data["today_revenue"] else 0

    cursor.close()
    conn.close()

    return templates.TemplateResponse(
        "reception_portal.html", 
        {
            "request": request, 
            "receptionist": reception_data,
            "patients_count": patients_count,
            "invoices_count": invoices_count,
            "today_revenue": today_revenue
        }
    )    

@app.get("/logout_receptionist")
def logout_receptionist(request: Request):
    request.session.pop("reception_id", None)
    return RedirectResponse(url="/reception_login.html?msg=logout_success", status_code=303)



#================================== add amount to reception ============================
# 1. BOOKING ENDPOINT (Saves 2000 PKR & Proof Image)
@app.post("/api/appointments/book")
async def book_appointment(
    patient_id: int = Form(...), 
    doctor_id: int = Form(...),
    appt_date: str = Form(...),
    appt_time: str = Form(...),
    amount_paid: str = Form("2000"),
    payment_proof: UploadFile = File(...)
):
    try:
        upload_folder = "static/uploads"
        os.makedirs(upload_folder, exist_ok=True)
        file_path = f"/{upload_folder}/{payment_proof.filename}"
        
        with open(f"static/uploads/{payment_proof.filename}", "wb") as buffer:
            shutil.copyfileobj(payment_proof.file, buffer)

        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            INSERT INTO appointments 
            (patient_id, doctor_id, appt_date, appt_time, amount_paid, payment_proof_path, status)
            VALUES (%s, %s, %s, %s, %s, %s, 'Pending')
        """
        cursor.execute(query, (patient_id, doctor_id, appt_date, appt_time, amount_paid, file_path))
        conn.commit()
        
        cursor.close()
        conn.close()
        return {"status": "success", "message": "Appointment booked successfully!"}
        
    except Exception as e:
        print(f"❌ BOOKING ERROR: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# main.py mein book_appointment function ke andar


# @app.post("/api/appointments/book")
# async def book_appointment(
#     patient_id: int = Form(...),
#     doctor_id: int = Form(...),
#     appt_date: str = Form(...),
#     appt_time: str = Form(...),
#     amount_paid: str = Form("2000"),
#     payment_proof: UploadFile = File(...)
# ):
#     conn = None
#     cursor = None
#     try:
#         conn = get_db_connection()
#         cursor = conn.cursor(dictionary=True)

#         # 1. Verify karein ke doctor_id database mein exist karta hai ya nahi
#         cursor.execute("SELECT id FROM doctors WHERE id = %s", (doctor_id,))
#         valid_doctor = cursor.fetchone()

#         if not valid_doctor:
#             # Agar ID 3 exist nahi karti, toh pehle available doctor ki ID utha lein
#             cursor.execute("SELECT id FROM doctors LIMIT 1")
#             first_doctor = cursor.fetchone()
#             if first_doctor:
#                 doctor_id = first_doctor['id']
#             else:
#                 raise HTTPException(status_code=400, detail="Database mein koi doctor registered nahi hai.")

#         # 2. File Save Logic
#         upload_folder = "static/uploads"
#         os.makedirs(upload_folder, exist_ok=True)
#         unique_filename = f"{uuid.uuid4().hex}_{payment_proof.filename}"
#         file_path = f"{upload_folder}/{unique_filename}"

#         with open(file_path, "wb") as buffer:
#             shutil.copyfileobj(payment_proof.file, buffer)

#         # 3. Insert Appointment
#         query = """
#             INSERT INTO appointments 
#             (patient_id, doctor_id, appt_date, appt_time, amount_paid, payment_proof_path, status)
#             VALUES (%s, %s, %s, %s, %s, %s, 'Pending')
#         """
#         cursor.execute(query, (patient_id, doctor_id, appt_date, appt_time, amount_paid, file_path))
#         conn.commit()

#         return {"status": "success", "message": "Appointment booked successfully!"}

#     except Exception as e:
#         if conn:
#             conn.rollback()
#         print(f"BOOKING ERROR: {e}")
#         raise HTTPException(status_code=500, detail=str(e))
#     finally:
#         if cursor:
#             cursor.close()
#         if conn:
#             conn.close()

# 2. RECEPTION STATS ENDPOINT (Calculates Online Collection)
# @app.get("/api/reception/stats")
# def get_reception_stats():
#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True)

#     try:
#         # SQL Sum Query: Non-rejected JazzCash 2000 PKR payments ka total calculate karega
#         query = """
#             SELECT 
#                 COALESCE(SUM(CAST(amount_paid AS DECIMAL(10,2))), 0) AS total_online_revenue
#             FROM appointments 
#             WHERE payment_proof_path IS NOT NULL 
#               AND status != 'Rejected'
#         """
#         cursor.execute(query)
#         stats = cursor.fetchone()

#         return {
#             "status": "success", 
#             "total_online_revenue": float(stats["total_online_revenue"])
#         }

#     except Exception as e:
#         print(f"❌ RECEPTION STATS ERROR: {e}")
#         return {"status": "error", "message": str(e)}

#     finally:
#         cursor.close()
#         conn.close()
# 1. RECEPTION STATS ENDPOINT
@app.get("/api/reception/stats")
def get_reception_stats():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Patients registered today
        cursor.execute("SELECT COUNT(*) AS count FROM patients WHERE DATE(registration_date) = CURDATE()")
        patients_today = cursor.fetchone()["count"]

        # Invoices issued today & invoice revenue
        cursor.execute("SELECT COUNT(*) AS count, COALESCE(SUM(amount), 0) AS invoice_revenue FROM invoices WHERE DATE(invoice_date) = CURDATE()")
        inv_data = cursor.fetchone()
        invoices_today = inv_data["count"]
        invoice_revenue = float(inv_data["invoice_revenue"])

        # Online revenue from appointments
        cursor.execute("""
            SELECT COALESCE(SUM(CAST(amount_paid AS DECIMAL(10,2))), 0) AS total_online_revenue
            FROM appointments
            WHERE payment_proof_path IS NOT NULL AND status != 'Rejected'
        """)
        online_revenue = float(cursor.fetchone()["total_online_revenue"])

        return {
            "status": "success",
            "patients_today": patients_today,
            "invoices_today": invoices_today,
            "collected_today": invoice_revenue + online_revenue
        }
    except Exception as e:
        print(f"❌ RECEPTION STATS ERROR: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()


# 2. REGISTER PATIENT
@app.post("/register_patient")
async def register_patient(
    request: Request,
    full_name: str = Form(...),
    phone: str = Form(...),
    age: int = Form(...),
    gender: str = Form(...),
    cnic: str = Form(None),
    email:str=Form(None)
):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        new_patient_id = f"PT-{random.randint(10000, 99999)}"

        cursor.execute(
            "INSERT INTO patients (patient_id, full_name, phone, age, gender, cnic, registration_date) VALUES (%s, %s, %s, %s, %s, %s, NOW())",
            (new_patient_id, full_name, phone, age, gender, cnic,email)
        )
        conn.commit()

        return JSONResponse(content={
            "status": "success", 
            "patient_id": new_patient_id
        })
    except Exception as e:
        print(f"Error registering patient: {e}")
        return JSONResponse(content={"status": "error", "message": str(e)})
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()


# 3. SEARCH PATIENT
@app.get("/search_patient")
async def search_patient(
    pt_id: Optional[str] = None,
    phone: Optional[str] = None,
    name: Optional[str] = None
):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        patient = None

        if pt_id:
            cursor.execute(
                "SELECT patient_id as pt_id, full_name, phone FROM patients WHERE patient_id = %s",
                (pt_id,)
            )
            patient = cursor.fetchone()
        elif phone:
            if name:
                cursor.execute(
                    "SELECT patient_id as pt_id, full_name, phone FROM patients WHERE phone = %s AND full_name LIKE %s",
                    (phone, f"%{name}%")
                )
            else:
                cursor.execute(
                    "SELECT patient_id as pt_id, full_name, phone FROM patients WHERE phone = %s",
                    (phone,)
                )
            patient = cursor.fetchone()

        if patient:
            return JSONResponse(content={
                "status": "success",
                "pt_id": patient["pt_id"],
                "full_name": patient["full_name"],
                "phone": patient["phone"]
            })
        else:
            return JSONResponse(content={"status": "error", "message": "Patient not found"})
    except Exception as e:
        print(f"Error searching patient: {e}")
        return JSONResponse(content={"status": "error", "message": "Database error"})
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
#==================================================================

# ================= 3. REGISTER PATIENT (AUTO-ID) =================
# @app.post("/register_patient")
# async def register_patient(
#     request: Request,
#     full_name: str = Form(...),
#     phone: str = Form(...),
#     age: int = Form(...),
#     gender: str = Form(...),
#     cnic: str = Form(None)
# ):
#     try:
#         conn = get_db_connection()
#         cursor = conn.cursor()
        
#         new_patient_id = f"PT-{random.randint(10000, 99999)}"
        
#         cursor.execute(
#             "INSERT INTO patients (patient_id, full_name, phone, age, gender, cnic, registration_date) VALUES (%s, %s, %s, %s, %s, %s, NOW())",
#             (new_patient_id, full_name, phone, age, gender, cnic)
#         )
#         conn.commit()
        
#         return JSONResponse(content={"status": "success", "patient_id": new_patient_id})
#     except Exception as e:
#         print(f"Error registering patient: {e}")
#         return JSONResponse(content={"status": "error"})
#     finally:
#         if 'conn' in locals() and conn.is_connected():
#             cursor.close()
#             conn.close()


@app.post("/register_patient")
async def register_patient(
    request: Request,
    full_name: str = Form(...),
    phone: str = Form(...),
    age: int = Form(...),
    gender: str = Form(...),
    cnic: str = Form(None)
):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        new_patient_id = f"PT-{random.randint(10000, 99999)}"
        patient_uuid = str(uuid.uuid4()) # Stored in DB for system use

        cursor.execute(
            "INSERT INTO patients (patient_id, uuid, full_name, phone, age, gender, cnic, registration_date) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())",
            (new_patient_id, patient_uuid, full_name, phone, age, gender, cnic)
        )
        conn.commit()

        # Returns only patient_id needed for Receptionist Desk
        return JSONResponse(content={
            "status": "success", 
            "patient_id": new_patient_id
        })
    except Exception as e:
        print(f"Error registering patient: {e}")
        return JSONResponse(content={"status": "error", "message": str(e)})
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

# ================= 4. FETCH PATIENT NAME =================
@app.get("/get_patient_name/{patient_id}")
async def get_patient_name(patient_id: str):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT full_name FROM patients WHERE patient_id = %s", (patient_id,))
        patient = cursor.fetchone()
        
        if patient:
            return JSONResponse(content={"status": "success", "name": patient["full_name"]})
        else:
            return JSONResponse(content={"status": "error", "name": ""})
            
    except Exception as e:
        print(f"Error fetching name: {e}")
        return JSONResponse(content={"status": "error", "name": ""})
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

# ================= 4. SEARCH PATIENT (BY PT ID OR PHONE/NAME) =================
# @app.get("/search_patient")
# async def search_patient(
#     pt_id: Optional[str] = None,
#     phone: Optional[str] = None,
#     name: Optional[str] = None
# ):
#     try:
#         conn = get_db_connection()
#         cursor = conn.cursor(dictionary=True)
        
#         patient = None

#         if pt_id:
#             cursor.execute(
#                 "SELECT patient_id as pt_id, full_name, phone FROM patients WHERE patient_id = %s", 
#                 (pt_id,)
#             )
#             patient = cursor.fetchone()
            
#         elif phone:
#             if name:
#                 cursor.execute(
#                     "SELECT patient_id as pt_id, full_name, phone FROM patients WHERE phone = %s AND full_name LIKE %s", 
#                     (phone, f"%{name}%")
#                 )
#             else:
#                 cursor.execute(
#                     "SELECT patient_id as pt_id, full_name, phone FROM patients WHERE phone = %s", 
#                     (phone,)
#                 )
#             patient = cursor.fetchone()

#         if patient:
#             return JSONResponse(content={
#                 "status": "success", 
#                 "pt_id": patient["pt_id"],
#                 "full_name": patient["full_name"],
#                 "phone": patient["phone"]
#             })
#         else:
#             return JSONResponse(content={"status": "error", "message": "Patient not found"})
            
#     except Exception as e:
#         print(f"Error searching patient: {e}")
#         return JSONResponse(content={"status": "error", "message": "Database error"})
#     finally:
#         if 'conn' in locals() and conn.is_connected():
#             cursor.close()
#             conn.close()

@app.get("/search_patient")
async def search_patient(
    pt_id: Optional[str] = None,
    phone: Optional[str] = None,
    name: Optional[str] = None
):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        patient = None

        if pt_id:
            cursor.execute(
                "SELECT patient_id as pt_id, uuid as patient_uuid, full_name, phone FROM patients WHERE patient_id = %s",
                (pt_id,)
            )
            patient = cursor.fetchone()
        elif phone:
            if name:
                cursor.execute(
                    "SELECT patient_id as pt_id, uuid as patient_uuid, full_name, phone FROM patients WHERE phone = %s AND full_name LIKE %s",
                    (phone, f"%{name}%")
                )
            else:
                cursor.execute(
                    "SELECT patient_id as pt_id, uuid as patient_uuid, full_name, phone FROM patients WHERE phone = %s",
                    (phone,)
                )
            patient = cursor.fetchone()

        if patient:
            return JSONResponse(content={
                "status": "success",
                "pt_id": patient["pt_id"],
                "patient_uuid": patient.get("patient_uuid", ""),
                "full_name": patient["full_name"],
                "phone": patient["phone"]
            })
        else:
            return JSONResponse(content={"status": "error", "message": "Patient not found"})
    except Exception as e:
        print(f"Error searching patient: {e}")
        return JSONResponse(content={"status": "error", "message": "Database error"})
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

# ================= 5. GENERATE INVOICE =================
@app.post("/generate_invoice")
async def generate_invoice(
    request: Request,
    patient_id: str = Form(...),
    service: str = Form(...),
    amount: float = Form(...),
    payment_method: str = Form(...)
):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO invoices (patient_id, service_name, amount, payment_method, invoice_date) VALUES (%s, %s, %s, %s, NOW())",
            (patient_id, service, amount, payment_method)
        )
        conn.commit()
        
        return JSONResponse(content={"status": "success"})
    except Exception as e:
        print(f"Error generating invoice: {e}")
        return JSONResponse(content={"status": "error"})
    finally:
      if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()


# ---------------------------------------------------------
# Request Schema for Approval
# ---------------------------------------------------------
class ApproveAppointmentRequest(BaseModel):
    confirmed_date: str
    confirmed_time: str

# ---------------------------------------------------------
# 1. NEW ROUTE: Fetch Appointments for Doctor (With Patient Name!)
# ---------------------------------------------------------

@app.get("/appoint_accept")
def appoint_accept_page():
    return {"message":"Appointment accept page"}

@app.get("/api/doctor/{doctor_id}/appointments")
def get_doctor_appointments(doctor_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # JOIN patients table to get full_name and phone
    query = """
        SELECT 
            a.appointment_id,
            a.patient_id,
            a.doctor_id,
            a.appt_date,
            a.appt_time,
            a.appt_type,
            a.amount_paid,
            a.payment_proof_path,
            a.status,
            a.confirmed_date,
            a.confirmed_time,
            a.created_at,
            p.full_name AS patient_name,
            p.phone AS patient_phone
        FROM appointments a
        JOIN patients p ON a.patient_id = p.id
        WHERE a.doctor_id = %s
        ORDER BY a.created_at DESC
    """
    cursor.execute(query, (doctor_id,))
    result = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return {"data": result}


# ---------------------------------------------------------
# 2. Doctor Route: Approve Appointment (Fixed Column Bug)
# ---------------------------------------------------------
class ApproveAppointmentRequest(BaseModel):
    appointment_id: int
    confirmed_date: Optional[str] = None
    confirmed_time: Optional[str] = None

@app.post("/api/appointments/approve")
def approve_appointment_direct(payload: ApproveAppointmentRequest):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # 1. Pehle existing appointment details fetch karo
        cursor.execute("SELECT appt_date, appt_time FROM appointments WHERE appointment_id = %s", (payload.appointment_id,))
        appt = cursor.fetchone()

        if not appt:
            return {"status": "error", "message": "Appointment not found"}

        # 2. Agar payload mein confirmed date/time nahi mila toh requested appt_date/appt_time utha lo
        final_date = payload.confirmed_date or appt.get("appt_date")
        final_time = payload.confirmed_time or appt.get("appt_time")

        # 3. Update columns in Database
        query = """
            UPDATE appointments
            SET status = 'Confirmed',
                confirmed_date = %s,
                confirmed_time = %s
            WHERE appointment_id = %s
        """
        cursor.execute(query, (final_date, final_time, payload.appointment_id))
        conn.commit()

        print("✅ DATABASE SUCCESSFULLY UPDATED!")
        return {"status": "success", "message": "Appointment approved successfully!"}

    except Exception as e:
        print(f"❌ DATABASE ERROR: {e}")
        return {"status": "error", "message": str(e)}

    finally:
        cursor.close()
        conn.close()


# ---------------------------------------------------------
# 3. Doctor Route: Reject Appointment (Fixed Column Bug)
# ---------------------------------------------------------
@app.post("/api/appointments/{appointment_id}/reject")
def reject_appointment(appointment_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # FIX: Checked appointment_id instead of non-existent 'id'
    cursor.execute("SELECT appointment_id FROM appointments WHERE appointment_id = %s", (appointment_id,))
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Appointment not found")

    query = "UPDATE appointments SET status = 'Rejected' WHERE appointment_id = %s"
    cursor.execute(query, (appointment_id,))
    conn.commit()
    
    cursor.close()
    conn.close()
    return {"status": "success", "message": f"Appointment {appointment_id} rejected."}       


# ---------------------------------------------------------
# 4. Patient Route: Fetch Patient Appointments
# ---------------------------------------------------------
@app.get("/api/patient/{patient_id}/appointments")
def get_patient_appointments(patient_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM appointments WHERE patient_id = %s", (patient_id,))
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return {"data": result}
# ==============================================================
# 1. LAB TECHNICIAN LOGIN & LOGOUT ROUTES
# ==============================================================

@app.get("/login/lab", response_class=HTMLResponse)
def get_lab_login_page(request: Request):
    return templates.TemplateResponse("lab_login.html", {"request": request})

@app.post("/login/lab")
def login_lab_route(request: Request, full_name: str = Form(...), staff_id: str = Form(...)):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute(
        "SELECT * FROM lab_technician WHERE full_name = %s AND hospital_id = %s",
        (full_name, staff_id)
    )
    
    lab_tech = cursor.fetchone()
    cursor.close()
    conn.close()

    if lab_tech:
        request.session["lab_id"] = lab_tech["id"]
        return RedirectResponse(url="/lab_reports.html?msg=login_success", status_code=303)
    else:
        return RedirectResponse(url="/login/lab?msg=invalid", status_code=303)

@app.get("/logout/lab")
def logout_lab(request: Request):
    request.session.pop("lab_id", None)
    return RedirectResponse(url="/login/lab?msg=logout_success", status_code=303)

# 2. LAB PORTAL / DASHBOARD ROUTE

@app.get("/lab_reports.html", response_class=HTMLResponse)
def lab_portal_page(request: Request):
    lab_id = request.session.get("lab_id")
    if not lab_id:
        return RedirectResponse(url="/login/lab")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM lab_technician WHERE id = %s", (lab_id,))
    lab_data = cursor.fetchone()
    cursor.close()
    conn.close()

    return templates.TemplateResponse(
        "lab_reports.html",
        {"request": request, "lab_tech": lab_data}
    )

#========================================================
# Doctor & patient route
#========================================================

# ==================== PYDANTIC SCHEMAS ====================
class MedicineItem(BaseModel):
    medicine_name: str
    dosage: str
    frequency: str
    duration: str

class LabOrderItem(BaseModel):
    test_name: str
    urgency: Optional[str] = "Normal"
    instructions: Optional[str] = ""

# class DoctorVisitRequest(BaseModel):
#     patient_id: str
#     doctor_pmdc_id: str
#     temperature: Optional[str] = None
#     blood_pressure: Optional[str] = None
#     diagnosis_notes: Optional[str] = None
#     medicines: List[MedicineItem] = []
#     lab_tests: List[LabOrderItem] = []

class DoctorVisitRequest(BaseModel):
    patient_id: str
    doctor_pmdc_id: Optional[str] = ""  # Fixed: Ab missing field par 422 error nahi aayega
    temperature: Optional[str] = None
    blood_pressure: Optional[str] = None
    diagnosis_notes: Optional[str] = None
    medicines: List[MedicineItem] = []
    lab_tests: List[LabOrderItem] = []

# ==================== HELPER FUNCTION (UPDATED) ====================
# def serialize_db_data(data):
#     if isinstance(data, list):
#         return [serialize_db_data(item) for item in data]
#     if isinstance(data, dict):
#         new_data = {}
#         for k, v in data.items():
#             # Fix: Type checking string se ki hai taake import clash na ho
#             type_name = type(v).__name__
#             if type_name in ('date', 'datetime', 'time', 'timedelta'):
#                 new_data[k] = str(v)
#             elif type_name == 'Decimal':
#                 new_data[k] = float(v)
#             else:
#                 new_data[k] = v
#         return new_data
#     return data
# ==================== ENDPOINTS ====================

# 1. Patient Data Fetch Endpoint (ID ya Name+Phone se)
@app.get("/api/doctor/search-patient")
def search_patient_for_doctor(
    patient_id: Optional[str] = Query(None),
    name: Optional[str] = Query(None),
    phone: Optional[str] = Query(None)
):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        patient = None
        search_id = None

        if patient_id:
            search_id = patient_id.strip()
            if not search_id.startswith("PT-"):
                search_id = f"PT-{search_id}"
                
            cursor.execute("SELECT * FROM patients WHERE patient_id = %s", (search_id,))
            patient = cursor.fetchone()
            
        elif name and phone:
            query = "SELECT * FROM patients WHERE full_name LIKE %s AND phone = %s"
            cursor.execute(query, (f"%{name.strip()}%", phone.strip()))
            patient = cursor.fetchone()
            
            if patient:
                search_id = patient['patient_id'] 

        else:
            raise HTTPException(status_code=400, detail="Please provide either Patient ID or both Name & Phone number.")

        if not patient:
            raise HTTPException(status_code=404, detail="Patient NOT found in database")

        cursor.execute("SELECT * FROM medical_history WHERE patient_id = %s ORDER BY visit_date DESC", (search_id,))
        history_records = cursor.fetchall()
        
        cursor.execute("SELECT * FROM prescriptions WHERE patient_id = %s ORDER BY prescribed_date DESC", (search_id,))
        prescriptions = cursor.fetchall()

        safe_patient = serialize_db_data(patient)
        safe_history = serialize_db_data(history_records)
        safe_prescriptions = serialize_db_data(prescriptions)

        return {
            "status": "success",
            "patient": patient,
            "history": history_records,
            "prescriptions": prescriptions
        }
        
    except Exception as e:
        print ("❌️ Search API error:", str(e))
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

# 2. Save Medical History, Prescriptions, and Lab Orders Endpoint
@app.post("/api/doctor/save-visit")
def save_doctor_visit(request: Request, data: DoctorVisitRequest):
    active_doctor_pmdc = (
        request.session.get("doctor_pmdc_id") or 
        request.session.get("pmdc_id") or 
        request.session.get("user_id") or 
        data.doctor_pmdc_id
    )

    if not active_doctor_pmdc or active_doctor_pmdc.strip() == "":
        raise HTTPException(status_code=400, detail="Doctor session invalid. Please log in again.")

    data.doctor_pmdc_id = active_doctor_pmdc.strip()
# def save_doctor_visit(data: DoctorVisitRequest):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        history_query = """
            INSERT INTO medical_history 
            (patient_id, doctor_pmdc_id, temperature, blood_pressure, diagnosis_notes) 
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(history_query, (
            data.patient_id, 
            data.doctor_pmdc_id, 
            data.temperature, 
            data.blood_pressure, 
            data.diagnosis_notes
        ))
        
        history_id = cursor.lastrowid
        
        if data.medicines:
            rx_query = """
                INSERT INTO prescriptions 
                (history_id, patient_id, doctor_pmdc_id, medicine_name, dosage, frequency, duration) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            for med in data.medicines:
                cursor.execute(rx_query, (
                    history_id,
                    data.patient_id,
                    data.doctor_pmdc_id,
                    med.medicine_name,
                    med.dosage,
                    med.frequency,
                    med.duration
                ))

        if data.lab_tests:
            lab_query = """
                INSERT INTO lab_orders 
                (patient_id, doctor_pmdc_id, test_name, urgency, instructions) 
                VALUES (%s, %s, %s, %s, %s)
            """
            for lab in data.lab_tests:
                cursor.execute(lab_query, (
                    data.patient_id,
                    data.doctor_pmdc_id,
                    lab.test_name,
                    lab.urgency,
                    lab.instructions
                ))

        conn.commit()
        
        return {
            "status": "success",
            "message": "Patient visit history and prescriptions saved successfully!",
            "history_id": history_id
        }
        
    except Exception as e:
        conn.rollback() 
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        conn.close()

#=====================================================
# Lab portal
#=====================================================
UPLOAD_DIR = "static/uploads/lab_reports"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Allowed Security Rules
ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png"}
ALLOWED_MIME_TYPES = {"application/pdf", "image/jpeg", "image/png"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 Megabytes

async def validate_and_save_file(file: UploadFile, order_id: int) -> str:
    if not file or not file.filename:
        return None

    filename = file.filename.lower()
    ext = os.path.splitext(filename)[1]
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Security Error: File type allowed nahi hai! (Only PDF, JPG, PNG)")

    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=400, detail="Security Error: Invalid MIME type detected!")

    content = await file.read()
    
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="Security Error: File ka size 5MB se zyada nahi hona chahiye!")

    is_pdf = content.startswith(b"%PDF")
    is_jpeg = content.startswith(b"\xff\xd8\xff")
    is_png = content.startswith(b"\x89PNG\r\n\x1a\n")

    if not (is_pdf or is_jpeg or is_png):
        raise HTTPException(
            status_code=400, 
            detail="Security Error: Fake extension detected! Real file standard format se match nahi ho rahi."
        )

    unique_filename = f"lab_report_order_{order_id}_{uuid.uuid4().hex[:8]}{ext}"
    saved_path = os.path.join(UPLOAD_DIR, unique_filename)

    with open(saved_path, "wb") as buffer:
        buffer.write(content)

    return f"/static/uploads/lab_reports/{unique_filename}"

# ==========================================
# 1. GET: Fetch Pending Lab Orders
# ==========================================
@app.get("/api/lab/pending-orders")
def get_pending_lab_orders():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        query = """
            SELECT l.id, l.patient_id, l.test_name, l.urgency, l.order_date, p.full_name 
            FROM lab_orders l
            JOIN patients p ON l.patient_id = p.patient_id
            WHERE l.status = 'Pending'
            ORDER BY l.urgency DESC, l.order_date ASC
        """
        cursor.execute(query)
        pending_orders = cursor.fetchall()
        
        count_query = """
            SELECT COUNT(*) as total 
            FROM lab_orders 
            WHERE status = 'Completed' AND WEEK(order_date) = WEEK(NOW())
        """
        cursor.execute(count_query)
        completed_count = cursor.fetchone()['total']
        
        return {
            "status": "success", 
            "data": pending_orders, 
            "completed_this_week": completed_count
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        conn.close()

# 2. POST: Secure Upload & Save Report
@app.post("/api/lab/upload-report")
async def upload_lab_report(
    order_id: int = Form(...),
    patient_id: str = Form(...),
    test_name: str = Form(...),
    report_type: str = Form(...),
    test_price: float = Form(...),
    result_summary: str = Form(""),
    report_file: UploadFile = File(None)
):
    file_path = None
    if report_file and report_file.filename:
        file_path = await validate_and_save_file(report_file, order_id)

    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        insert_report = """
            INSERT INTO lab_reports (order_id, report_type, result_summary, file_path, test_price)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(insert_report, (order_id, report_type, result_summary, file_path, test_price))

        update_order = "UPDATE lab_orders SET status = 'Completed' WHERE id = %s"
        cursor.execute(update_order, (order_id,))

        bill_description = f"Lab Test: {test_name} ({report_type})"
        insert_bill = """
            INSERT INTO patient_bills (patient_id, bill_type, description, amount, status)
            VALUES (%s, 'Lab Test', %s, %s, 'Unpaid')
        """
        cursor.execute(insert_bill, (patient_id, bill_description, test_price))

        conn.commit()
        
        return {
            "status": "success", 
            "message": "Report uploaded and bill generated successfully!"
        }

    except Exception as e:
        conn.rollback() 
        raise HTTPException(status_code=500, detail=f"Database Processing Error: {str(e)}")
    finally:
        cursor.close()
        conn.close()

       

# =====================================================
# Doctor Portal: Search Patient & Fetch Lab Reports
# =====================================================


# ==========================================
# HELPER FUNCTION FOR DATA SERIALIZATION
# ==========================================
def serialize_db_data(data):
    if isinstance(data, list):
        return [serialize_db_data(item) for item in data]
    if isinstance(data, dict):
        new_data = {}
        for k, v in data.items():
            type_name = type(v).__name__
            if type_name in ('date', 'datetime', 'time', 'timedelta'):
                new_data[k] = str(v)
            elif type_name == 'Decimal':
                new_data[k] = float(v)
            else:
                new_data[k] = v
        return new_data
    return data


# ==========================================
# 1. PAGE RENDER ROUTE (Doctor Patient Reports Page)
# ==========================================
# @app.get("/doctor_patient_report", response_class=HTMLResponse)
# @app.get("/doctor_patient_report.html", response_class=HTMLResponse)
# async def doctor_patient_report(request: Request):
#     doctor_id = request.session.get("doctor_id")

#     if not doctor_id:
#         return RedirectResponse(url="/doctor_login", status_code=status.HTTP_303_SEE_OTHER)


#     doctor = None
#     try:
#         conn = get_db_connection()
#         cursor = conn.cursor(dictionary=True)
#         # Doctor Table Search by ID or PMDC ID
#         cursor.execute(
#             "SELECT full_name, specialization, pmdc_id FROM doctors WHERE id = %s OR pmdc_id = %s", 
#             (doctor_id, doctor_id)
#         )
#         doctor = cursor.fetchone()
#         cursor.close()
#         conn.close()
#     except Exception as e:
#         print(f"Database Error fetching doctor info: {e}")

#     # Fallback to prevent N/A in Jinja UI if DB fetch fails
#     if not doctor:
#         doctor = {
#             "full_name": "Dr. Doctor",
#             "specialization": "Specialist",
#             "pmdc_id": "PMDC-00000"
#         }

#     return templates.TemplateResponse("doctor_patient_report.html", {
#         "request": request,
#         "doctor": doctor
#     })

@app.get("/doctor_patient_report", response_class=HTMLResponse)
@app.get("/doctor_patient_report.html", response_class=HTMLResponse)
async def doctor_patient_report(request: Request):
    doctor_id = request.session.get("doctor_id")

    if not doctor_id:
        return RedirectResponse(url="/doctor_login", status_code=status.HTTP_303_SEE_OTHER)

    # 🔒 HASHED URL CHECK: Agar URL me ?ref= nahi hai to auto-generate karke redirect karein
    ref_token = request.query_params.get("ref")
    if not ref_token:
        raw_payload = f"doc_rpt_{doctor_id}_{uuid.uuid4().hex[:10]}"
        hashed_ref = base64.b64encode(raw_payload.encode()).decode().rstrip("=")
        return RedirectResponse(
            url=f"/doctor_patient_report?ref={hashed_ref}", 
            status_code=status.HTTP_303_SEE_OTHER
        )

    doctor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        # Doctor Table Search by ID or PMDC ID
        cursor.execute(
            "SELECT * FROM full_name, specialization, pmdc_id FROM doctors WHERE id = %s OR pmdc_id = %s",
            (doctor_id, doctor_id)
        )
        doctor = cursor.fetchone()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Database Error fetching doctor info: {e}")

    # Fallback to prevent N/A in Jinja UI if DB fetch fails
    if not doctor:
        doctor = {
            "full_name": "Dr. Doctor",
            "specialization": "Specialist",
            "pmdc_id": "PMDC-00000"
        }

    return templates.TemplateResponse("doctor_patient_report.html", {
        "request": request,
        "doctor": doctor
    })

# ==========================================
# 2. API ROUTE (Patient Search & Lab Reports Fetching)
# ==========================================
@app.get("/api/doctor/patient-reports")
def get_patient_reports(patient_id: str, patient_name: str, phone: str):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        p_id = patient_id.strip()
        p_name = patient_name.strip()
        p_phone = phone.strip()

        patient_query = """
                  SELECT patient_id, uuid, full_name, phone, gender, age
                  FROM patients
                  WHERE (patient_id = %s OR uuid = %s) AND LOWER(full_name) = LOWER(%s) AND phone = %s
"""
        # patient_query = """
        #     SELECT patient_id, full_name, phone
        #     FROM patients
        #     WHERE patient_id = %s
        #       AND LOWER(full_name) = LOWER(%s)
        #       AND phone = %s
        # """
        cursor.execute(patient_query, (p_id,p_id, p_name, p_phone))
        patient = cursor.fetchone()

        if not patient: 
            raise HTTPException(
                status_code=404,
                detail="Patient record didnt matched, Please check entered Data!."
            )

        # Lab Reports fetch query (Blood group lab_reports se fetch hoga agar wahan available ho)
        reports_query = """
            SELECT 
                lr.id,
                lo.test_name,
                lr.report_type,
                lr.result_summary,
                lr.file_path,
                lr.test_price,
                lo.order_date,
                lr.reported_at
            FROM lab_reports lr
            JOIN lab_orders lo ON lr.order_id = lo.id
            WHERE lo.patient_id = %s OR lo.patient_id = %s 
            ORDER BY lr.reported_at DESC
        """
        cursor.execute(reports_query, (patient['patient_id'],patient['uuid']))
        reports = cursor.fetchall()

        return {
            "status": "success",
            "patient": serialize_db_data(patient),
            "reports": serialize_db_data(reports)
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"❌ DATABASE/SERVER ERROR: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        conn.close()
# ==============================================================
# PATIENT BLOOD & LAB REPORTS ROUTE
# ==============================================================
# @app.get("/blood_reports.html", response_class=HTMLResponse)
# @app.get("/blood_reports", response_class=HTMLResponse)
# def blood_reports_page(request: Request):
#     # Check if patient is logged in via session
#     patient_db_id = request.session.get("patient_id")
#     if not patient_db_id:
#         return RedirectResponse(url="/patient_login.html")

#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True)

#     try:
#         # 1. Fetch logged-in Patient Details
#         cursor.execute("SELECT * FROM patients WHERE id = %s", (patient_db_id,))
#         patient = cursor.fetchone()

#         if not patient:
#             return RedirectResponse(url="/patient_login.html")

#         # 2. Fetch Lab Reports for this patient (joining lab_reports with lab_orders)
#         patient_pt_id = patient.get("patient_id") # e.g. 'PT-82708'
        
#         reports_query = """
#             SELECT 
#                 lr.id,
#                 lo.test_name,
#                 lr.report_type,
#                 lr.result_summary,
#                 lr.file_path,
#                 lr.reported_at
#             FROM lab_reports lr
#             JOIN lab_orders lo ON lr.order_id = lo.id
#             WHERE lo.patient_id = %s
#             ORDER BY lr.reported_at DESC
#         """
#         cursor.execute(reports_query, (patient_pt_id,))
#         raw_reports = cursor.fetchall()

#         # Serialize dates and decimals safely using helper function
#         reports = serialize_db_data(raw_reports)

#         return templates.TemplateResponse(
#             "blood_reports.html",
#             {
#                 "request": request,
#                 "patient": patient,
#                 "reports": reports
#             }
#         )

#     except Exception as e:
#         print("❌ Error fetching patient blood reports:", str(e))
#         return templates.TemplateResponse(
#             "blood_reports.html",
#             {
#                 "request": request,
#                 "patient": None,
#                 "reports": []
#             }
#         )
#     finally:
#         cursor.close()
#         conn.close()


# @app.get("/blood_reports.html", response_class=HTMLResponse)
# @app.get("/blood_reports", response_class=HTMLResponse)
# def blood_reports_page(request: Request, uuid: Optional[str] = Query(None)):
#     # 1. Check session login
#     patient_db_id = request.session.get("patient_id")
#     if not patient_db_id:
#         return RedirectResponse(url="/patient_login.html")

#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True)

#     try:
#         # 2. Fetch logged-in Patient Details
#         cursor.execute("SELECT * FROM patients WHERE id = %s", (patient_db_id,))
#         patient = cursor.fetchone()

#         if not patient:
#             return RedirectResponse(url="/patient_login.html")

#         # Patient ka UUID nikalein
#         patient_uuid = patient.get("uuid") or patient.get("patient_id", "")

#         # AGAR URL MEIN UUID NAHI HAI TOH REDIRECT KAREIN (Taki Address Bar Mein URL Update Ho Jaye)
#         if not uuid and patient_uuid:
#             return RedirectResponse(url=f"/blood_reports.html?uuid={patient_uuid}")

#         # 3. Fetch Lab Reports
#         patient_pt_id = patient.get("patient_id")

#         reports_query = """
#             SELECT 
#                 lr.id,
#                 lo.test_name,
#                 lr.report_type,
#                 lr.result_summary,
#                 lr.file_path,
#                 lr.reported_at
#             FROM lab_reports lr
#             JOIN lab_orders lo ON lr.order_id = lo.id
#             WHERE lo.patient_id = %s
#             ORDER BY lr.reported_at DESC
#         """
#         cursor.execute(reports_query, (patient_pt_id,))
#         raw_reports = cursor.fetchall()

#         reports = serialize_db_data(raw_reports)

#         return templates.TemplateResponse(
#             "blood_reports.html",
#             {
#                 "request": request,
#                 "patient": patient,
#                 "reports": reports,
#                 "patient_uuid": patient_uuid
#             }
#         )

#     except Exception as e:
#         print("❌ Error fetching patient blood reports:", str(e))
#         return templates.TemplateResponse(
#             "blood_reports.html",
#             {
#                 "request": request,
#                 "patient": None,
#                 "reports": [],
#                 "patient_uuid": uuid or ""
#             }
#         )
#     finally:
#         cursor.close()
#         conn.close()

import uuid  # Top par import zaroor check kar lein

@app.get("/blood_reports.html", response_class=HTMLResponse)
@app.get("/blood_reports", response_class=HTMLResponse)
def blood_reports_page(request: Request, uuid_param: Optional[str] = Query(None, alias="uuid")):
    # 1. Check session login
    patient_db_id = request.session.get("patient_id")
    if not patient_db_id:
        return RedirectResponse(url="/patient_login.html")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # 2. Fetch logged-in Patient Details (id aur patient_id DONO check karein)
        cursor.execute("SELECT * FROM patients WHERE id = %s OR patient_id = %s", (patient_db_id, patient_db_id))
        patient = cursor.fetchone()

        if not patient:
            return RedirectResponse(url="/patient_login.html")

        # Patient ka UUID consistent tareeqay se nikalein
        real_id = patient.get("patient_id") or patient.get("id")
        patient_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(real_id)))

        # Agar URL mein UUID sahi nahi hai toh URL update karein
        if not uuid_param or uuid_param != patient_uuid:
            return RedirectResponse(url=f"/blood_reports.html?uuid={patient_uuid}")

        # 3. Fetch Lab Reports
        patient_pt_id = patient.get("patient_id") or patient.get("id")

        reports_query = """
            SELECT 
                lr.id,
                lo.test_name,
                lr.report_type,
                lr.result_summary,
                lr.file_path,
                lr.reported_at
            FROM lab_reports lr
            JOIN lab_orders lo ON lr.order_id = lo.id
            WHERE lo.patient_id = %s OR lo.patient_id = %s
            ORDER BY lr.reported_at DESC
        """
        
        cursor.execute(reports_query, (patient_pt_id, patient_db_id))
        raw_reports = cursor.fetchall()

        reports = serialize_db_data(raw_reports) if 'serialize_db_data' in globals() else raw_reports

        return templates.TemplateResponse(
            "blood_reports.html",
            {
                "request": request,
                "patient": patient,
                "reports": reports,
                "patient_uuid": patient_uuid
            }
        )

    except Exception as e:
        print("❌ Error fetching patient blood reports:", str(e))
        return templates.TemplateResponse(
            "blood_reports.html",
            {
                "request": request,
                "patient": None,
                "reports": [],
                "patient_uuid": uuid_param or ""
            }
        )
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


# --- PATIENT HISTORY (WITH UUID IN URL) ---
@app.get("/patient_history", response_class=HTMLResponse)
@app.get("/patient_history.html", response_class=HTMLResponse)
def patient_history_page(request: Request, uuid_param: Optional[str] = Query(None, alias="uuid")):
    # 1. Session check
    session_patient_id = request.session.get("patient_id")
    if not session_patient_id:
        return RedirectResponse(url="/patient_login.html", status_code=status.HTTP_303_SEE_OTHER)

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # 2. Session ID se Patient Details Fetch Karein
        cursor.execute(
            "SELECT * FROM patients WHERE patient_id = %s OR id = %s", 
            (session_patient_id, session_patient_id)
        )
        patient = cursor.fetchone()

        if not patient:
            return RedirectResponse(url="/patient_login.html", status_code=status.HTTP_303_SEE_OTHER)

        # Patient ki real ID
        real_patient_id = patient.get("patient_id") or patient.get("id")

        # 3. Hashed UUID Generate Karein (Real ID se Deterministic UUID Hash)
        patient_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(real_patient_id)))

        # 4. Agar URL me 'uuid' parameter nahi hai, toh URL par Hashed UUID ke sath REDIRECT karein
        if not uuid_param:
            return RedirectResponse(
                url=f"/patient_history?uuid={patient_uuid}", 
                status_code=status.HTTP_302_FOUND
            )

        # 5. Medical History Fetch Karein
        query = """
            SELECT mh.*, d.full_name AS doctor_name
            FROM medical_history mh
            LEFT JOIN doctors d ON mh.doctor_pmdc_id = d.pmdc_id
            WHERE mh.patient_id = %s
            ORDER BY mh.visit_date DESC
        """

        cursor.execute(query, (real_patient_id,))
        history_records = cursor.fetchall()

        # 6. Prescriptions / Medicines Map Karein
        for visit in history_records:
            cursor.execute("SELECT * FROM prescriptions WHERE history_id = %s", (visit["id"],))
            visit["medicines"] = cursor.fetchall()

        # Data serialization
        safe_patient = serialize_db_data(patient)
        safe_history = serialize_db_data(history_records)

        return templates.TemplateResponse(
            "patient_history.html",
            {
                "request": request,
                "patient": safe_patient,
                "patient_id": real_patient_id,
                "patient_uuid": patient_uuid,
                "history_records": safe_history
            }
        )

    except Exception as e:
        print("❌ Error fetching history:", str(e))
        return templates.TemplateResponse(
            "patient_history.html",
            {"request": request, "history_records": [], "error": str(e), "patient": None}
        )
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()
#=====================================================
# Feedback
#=====================================================
@app.get("/")
def feedback_form_page(request:Request):
    return templates.TemplateResponse("feedback_page.html", {"request":request}) 
 
class FeedbackSchema(BaseModel):
    patient_name : str
    rating : int
    comment: str
@app.post("/api/feedback")
def submit_feedback (data: FeedbackSchema):
    if not data.patient_name.strip():
        raise HTTPException(status_code=400, detail= "patient name is required.") 
    if not (1 <= data.rating <= 5):
        raise HTTPException (status_code=400, detail="Rating should be between 1 and 5")

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        query = "INSERT INTO feedback (patient_name, rating, comment) VALUES (%s , %s , %s)"
        cursor.execute(query, (data.patient_name.strip(), data.rating, data.comment.strip()))
        conn.commit()
        return {"message": "Feedback successfully saved"}
    finally:
        cursor.close()
        conn.close()
@app.get("/api/feedback/top")
def get_top_feedback():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)    
    try:
        query = "SELECT patient_name, rating, comment FROM feedback ORDER BY id DESC LIMIT 4"
        cursor.execute (query)  
        feedback = cursor.fetchall()
        return feedback
    finally:
        cursor.close()
        conn.close()  

             
#=====================================================
# ChatBot
#=====================================================
class ChatMessage(BaseModel):
    message: str

@app.post("/api/chatbot")
async def chatbot_response(chat: ChatMessage):
    user_msg = chat.message.lower().strip()

    knowledge_base = [
        {
            "keywords": ["history", "background", "about hospital", "established", "started", "who are you", "story", "origin"],
            "reply": "SaviourCrest Hospital was established 25 years ago as a small emergency clinic. Over the decades, it has grown into a state-of-the-art multi-specialty hospital providing 24/7 emergency care, advanced diagnostics, and specialized treatments to over 40,000 patients annually."
        },
        {
            "keywords": ["qualified", "qualification", "doctor", "doctors", "specialist", "experience", "degree", "professors", "experience"],
            "reply": "SaviourCrest Hospital has over 120 highly qualified doctors and specialists. Our medical team includes FCPS, FRCS, and board-certified professors with years of international and clinical experience in Cardiology, Pediatrics, Orthopedics, Neurology, and General Surgery."
        },
        {
            "keywords": ["machine", "machines", "equipment", "technology", "lab", "diagnostic", "testing", "mri", "ct scan", "xray", "x-ray", "ultrasound", "ventilator", "ot", "operation theatre"],
            "reply": "Our diagnostic labs and Operation Theatres are equipped with modern technology, including High-Resolution 1.5T MRI, 128-Slice CT Scanners, Digital X-Ray machines, 4D Ultrasound, Automated Hematology Analyzers, and advanced ICUs with life-support ventilators."
        },
        {
            "keywords": ["emergency", "icu", "ccu", "ambulance", "urgent", "24/7", "helpline", "accident", "trauma"],
            "reply": "Our Emergency Ward and Trauma Unit operate 24/7, 365 days a year. We have on-duty emergency physicians, fully equipped ambulances, and immediate ICU/CCU support. For urgent help, call our emergency line."
        },
        {
            "keywords": ["blood", "donor", "donate", "plasma", "blood bank", "blood group", "o+", "a+", "b+"],
            "reply": "SaviourCrest Blood Bank is open 24/7 with active stocks for all blood groups. You can register as a voluntary blood donor directly through our Blood Bank page on the website."
        },
        {
            "keywords": ["appointment", "book", "booking", "schedule", "fee", "fees", "charges", "cost", "price", "consultation"],
            "reply": "You can book an appointment by clicking the 'Book Appointment' button on our top navigation bar or logging into the Patient Portal. Consultation fees range depending on the specialist (approx. 1,500 - 3,000 PKR)."
        },
        {
            "keywords": ["timing", "timings", "hours", "open", "visiting", "visit time", "schedule"],
            "reply": "Emergency Services, Blood Bank, and Lab Diagnostics are open 24/7. OPD Clinics generally run from 9:00 AM to 9:00 PM (Mon - Sat). Patient visiting hours are from 4:00 PM to 7:00 PM daily."
        },
        {
            "keywords": ["location", "address", "where", "map", "contact", "phone", "number", "email", "reception", "call"],
            "reply": "SaviourCrest Hospital is located in Pakistan. You can contact our main reception line at +92 (---)-(--) or emergency helpline at +92 (---)-(---)."
        },
        {
            "keywords": ["hi", "hello", "hey", "assalam", "salam", "greetings"],
            "reply": "Hello! Welcome to SaviourCrest Hospital AI Assistant. How can I assist you with doctor booking, lab services, or hospital information today?"
        }
    ]

    best_match = None
    highest_score = 0

    for item in knowledge_base:
        score = sum(1 for kw in item["keywords"] if kw in user_msg)
        if score > highest_score:
            highest_score = score
            best_match = item["reply"]

    if not best_match:
        best_match = (
            "Thank you for reaching out to SaviourCrest Hospital! "
            "I can help you with information about our Doctors, 24/7 Emergency, Hospital History, "
            "Lab Equipment, Blood Bank, and Appointments. "
            "Please call our front desk directly at +92 (---)-(--) for further details."
        )

    return {"reply": best_match}

#=============================================================================
# Blood registration
#=============================================================================



# ==========================================
# 1. ROUTE: Blood Donor HTML Page
# ==========================================
@app.get("/blood-donor", response_class=HTMLResponse)
async def serve_blood_donor_page(request: Request):
    # Templates folder mein rakhi HTML file ko render karega
    return templates.TemplateResponse("blood_donor.html", {"request": request})


# ==========================================
# 2. ROUTE: Blood Donor Registration (POST)
# ==========================================
@app.post("/blood-donation/register")
async def register_blood_donor(
    full_name: str = Form(...),
    age: int = Form(...),
    gender: str = Form(...),
    blood_group: str = Form(...),
    phone: str = Form(...),
    email: Optional[str] = Form(None),
    city: str = Form(...),
    last_donated: Optional[str] = Form(None)
):
    # Condition 1: Age >= 18 Check
    if age < 18:
        return JSONResponse(
            status_code=400,
            content={"success": False, "message": "Donor must be 18 years or older to register."}
        )

    clean_email = email.strip() if email and email.strip() else None
    donation_date = last_donated if last_donated and last_donated.strip() else None

    db = None
    cursor = None
    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        # Condition 2 & 3: Check if Phone or Email already exists
        if clean_email:
            check_query = "SELECT id FROM blood_donors WHERE phone = %s OR email = %s"
            cursor.execute(check_query, (phone, clean_email))
        else:
            check_query = "SELECT id FROM blood_donors WHERE phone = %s"
            cursor.execute(check_query, (phone,))

        if cursor.fetchone():
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "Phone number or Email is already registered."}
            )

        # Insert Data into Database
        insert_query = """
            INSERT INTO blood_donors (full_name, age, gender, blood_group, phone, email, city, last_donated)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (full_name, age, gender, blood_group, phone, clean_email, city, donation_date))
        db.commit()

        return JSONResponse(
            status_code=200,
            content={"success": True, "message": "Registration Successful!"}
        )

    except mysql.connector.Error as err:
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"Database Error: {err.msg}"}
        )
    finally:
        if cursor:
            cursor.close()
        if db and db.is_connected():
            db.close()


# ==========================================
# 3. ROUTE: Live Chart Data API (GET)
# ==========================================
@app.get("/api/blood-bank/stock-data")
async def get_blood_stock_data():
    all_groups = ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]
    stock_counts = {group: 0 for group in all_groups}

    db = None
    cursor = None
    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        # Har blood group ke donors count karne ki query
        query = """
            SELECT blood_group, COUNT(*) AS count 
            FROM blood_donors 
            GROUP BY blood_group
        """
        cursor.execute(query)
        results = cursor.fetchall()

        for row in results:
            group = row['blood_group']
            if group in stock_counts:
                stock_counts[group] = row['count']

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "labels": list(stock_counts.keys()),
                "counts": list(stock_counts.values())
            }
        )

    except mysql.connector.Error as err:
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"Database Error: {err.msg}"}
        )
    finally:
        if cursor:
            cursor.close()
        if db and db.is_connected():
            db.close()



@app.get("/api/blood-bank/donor-counts")
async def get_donor_counts():
    db = None
    cursor = None
    try:
        # Aapka project wala existing connection helper
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        query = """
            SELECT blood_group, COUNT(*) as count 
            FROM blood_donors 
            GROUP BY blood_group
        """
        cursor.execute(query)
        rows = cursor.fetchall()

        counts = {
            "O+": 0, "O-": 0,
            "A+": 0, "A-": 0,
            "B+": 0, "B-": 0,
            "AB+": 0, "AB-": 0
        }

        for row in rows:
            group = str(row.get("blood_group", "")).strip().upper()
            if group in counts:
                counts[group] = row.get("count", 0)

        return counts

    except Exception as e:
        print("❌ Database Error in /donor-counts:", e)
        return {
            "O+": 0, "O-": 0, "A+": 0, "A-": 0,
            "B+": 0, "B-": 0, "AB+": 0, "AB-": 0
        }
    finally:
        if cursor:
            cursor.close()
        if db and db.is_connected():
            db.close()         
#=====================================================
#Disease_stats
#=====================================================
@app.get("/api/disease/stats")
def get_disease_stats():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT disease_name, cases FROM disease_stats ORDER BY recorded_on DESC LIMIT 5")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        if not rows:
            return {"labels": ["Flu", "Dengue", "Diabetes", "Hypertension", "Typhoid", "HIV", "Hepatitis", "Heart Attack", "Major (Road) Accidents", "Polio"],
                    "values": [320, 180, 260, 300, 90, 5, 76, 200, 15, 25]}

        labels = [row["disease_name"] for row in rows]
        values = [row["cases"] for row in rows]
        return {"labels": labels, "values": values}
    except Error:
        return {"labels": [], "values": []}    
#=================================================================================================
@app.get("/{page_name}")
def serve_page(page_name: str, request: Request):
    if not page_name.endswith(".html"):
        return JSONResponse(status_code=404, content={"detail": "Not found"})
    try:
        return templates.TemplateResponse(page_name, {"request": request})
    except Exception:
        return JSONResponse(status_code=404, content={"detail": "Page not found"})