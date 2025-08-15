# backend.py
import mysql.connector
from datetime import datetime, date

DB_NAME = "school"
MYSQL_USER = "root"
MYSQL_PASSWORD = "Naveen@123"
MYSQL_HOST = "localhost"

# ---------- Connections ----------
def _server_conn():
    return mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
    )

def _db_conn():
    return mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=DB_NAME,
    )

# ---------- Setup ----------
def setup():
    # Create database if not exists
    conn = _server_conn()
    cur = conn.cursor()
    cur.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
    conn.commit()
    conn.close()

    # Create / migrate table
    conn = _db_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INT PRIMARY KEY AUTO_INCREMENT,
            name VARCHAR(100) NOT NULL,
            age INT,
            grade VARCHAR(10),
            phone VARCHAR(20),
            address VARCHAR(255),
            dob DATE
        )
    """)
    conn.commit()
    conn.close()

# Run setup on import
setup()

# ---------- Helpers ----------
def _parse_dob_for_db(dob_text: str):
    """Accepts 'DD/MM/YYYY' or empty; returns 'YYYY-MM-DD' or None"""
    if not dob_text:
        return None
    try:
        d = datetime.strptime(dob_text, "%d/%m/%Y").date()
        if d > date.today():
            raise ValueError("DOB cannot be in the future.")
        if d.year < 1900:
            raise ValueError("DOB year too small.")
        return d.strftime("%Y-%m-%d")
    except ValueError as e:
        raise ValueError(f"Invalid DOB (use DD/MM/YYYY). {e}")

def _format_dob_for_ui(db_date):
    """MySQL date (YYYY-MM-DD) -> 'DD/MM/YYYY' for UI."""
    if not db_date:
        return ""
    try:
        return datetime.strptime(str(db_date), "%Y-%m-%d").strftime("%d/%m/%Y")
    except Exception:
        return str(db_date)

# ---------- CRUD (GUI-facing) ----------
def view_all():
    conn = _db_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, name, age, grade, phone, address, dob FROM students ORDER BY id")
    rows = cur.fetchall()
    conn.close()
    # Format DOB for UI
    formatted = []
    for r in rows:
        r = list(r)
        r[6] = _format_dob_for_ui(r[6])
        formatted.append(tuple(r))
    return formatted

def search(query: str):
    conn = _db_conn()
    cur = conn.cursor()
    like = f"%{query}%"
    if query.isdigit():
        # search by id exact OR age exact OR other fields like
        cur.execute("""
            SELECT id, name, age, grade, phone, address, dob
            FROM students
            WHERE id=%s OR age=%s OR name LIKE %s OR grade LIKE %s OR phone LIKE %s OR address LIKE %s
            ORDER BY id
        """, (int(query), int(query), like, like, like, like))
    else:
        cur.execute("""
            SELECT id, name, age, grade, phone, address, dob
            FROM students
            WHERE name LIKE %s OR grade LIKE %s OR phone LIKE %s OR address LIKE %s
            ORDER BY id
        """, (like, like, like, like))
    rows = cur.fetchall()
    conn.close()
    # format dob for UI
    out = []
    for r in rows:
        r = list(r)
        r[6] = _format_dob_for_ui(r[6])
        out.append(tuple(r))
    return out

def insert(name, age, grade, phone, address, dob_text):
    # basic validation
    if not name:
        raise ValueError("Name is required.")
    if age and not str(age).isdigit():
        raise ValueError("Age must be a number.")
    if phone and not str(phone).isdigit():
        raise ValueError("Phone must contain digits only.")

    dob_db = _parse_dob_for_db(dob_text) if dob_text else None

    conn = _db_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO students (name, age, grade, phone, address, dob)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (name, int(age) if age else None, grade or None,
          phone or None, address or None, dob_db))
    conn.commit()
    conn.close()

def update(sid, name, age, grade, phone, address, dob_text):
    if not sid:
        raise ValueError("ID missing for update.")
    if not name:
        raise ValueError("Name is required.")
    if age and not str(age).isdigit():
        raise ValueError("Age must be a number.")
    if phone and not str(phone).isdigit():
        raise ValueError("Phone must contain digits only.")
    dob_db = _parse_dob_for_db(dob_text) if dob_text else None

    conn = _db_conn()
    cur = conn.cursor()
    cur.execute("""
        UPDATE students
        SET name=%s, age=%s, grade=%s, phone=%s, address=%s, dob=%s
        WHERE id=%s
    """, (name, int(age) if age else None, grade or None,
          phone or None, address or None, dob_db, int(sid)))
    conn.commit()
    conn.close()

def delete(sid):
    conn = _db_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM students WHERE id=%s", (int(sid),))
    conn.commit()
    conn.close()
