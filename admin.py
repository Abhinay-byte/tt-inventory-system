import streamlit as st
import hashlib
import pandas as pd
from datetime import datetime
from database import get_connection, init_db

init_db()

conn = get_connection()
cursor = conn.cursor()

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def check_login(u, p):
    res = cursor.execute(
        "SELECT password_hash FROM admin_users WHERE username=?",
        (u,)
    ).fetchone()

    return res and res[0] == hash_pw(p)

st.set_page_config(page_title="Admin Panel", layout="wide")

if "login" not in st.session_state:
    st.session_state.login = False

# ---------------- LOGIN ----------------
if not st.session_state.login:
    st.title("🔐 Admin Login")

    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        if check_login(u, p):
            st.session_state.login = True
            st.rerun()
        else:
            st.error("Invalid credentials")

    st.stop()

st.sidebar.title("Admin Menu")

menu = st.sidebar.radio("Go to", [
    "Dashboard",
    "Add Inventory",
    "Add Employee",
    "Export Data",
    "Reset System",
    "Logout"
])

# ---------------- DASHBOARD ----------------
if menu == "Dashboard":
    st.title("📊 Dashboard")

    total = cursor.execute("SELECT SUM(total_stock) FROM inventory").fetchone()[0] or 0
    avail = cursor.execute("SELECT SUM(available_stock) FROM inventory").fetchone()[0] or 0
    issued = cursor.execute("SELECT COUNT(*) FROM issued WHERE status='Issued'").fetchone()[0]

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Stock", total)
    col2.metric("Available Stock", avail)
    col3.metric("Issued Items", issued)

    st.subheader("⚠ Low Stock Alert")

    low = cursor.execute("""
        SELECT equipment, brand, available_stock
        FROM inventory
        WHERE available_stock < 3
    """).fetchall()

    st.table(low)

# ---------------- ADD INVENTORY ----------------
elif menu == "Add Inventory":
    st.title("➕ Add Inventory")

    e = st.text_input("Equipment")
    b = st.text_input("Brand")
    t = st.number_input("Total Stock", 1, 100, 1)

    if st.button("Add"):
        cursor.execute("""
            INSERT INTO inventory
            VALUES (NULL, ?, ?, ?, ?, ?)
        """, (e, b, t, t, str(datetime.now())))

        conn.commit()
        st.success("Added")

# ---------------- ADD EMPLOYEE ----------------
elif menu == "Add Employee":
    st.title("👥 Add Employee")

    n = st.text_input("Name")
    d = st.text_input("Department")

    if st.button("Add"):
        cursor.execute("""
            INSERT INTO employees
            VALUES (NULL, ?, ?, ?)
        """, (n, d, str(datetime.now())))

        conn.commit()
        st.success("Employee added")

# ---------------- EXPORT ----------------
elif menu == "Export Data":
    st.title("📤 Export")

    issued = pd.read_sql("SELECT * FROM issued", conn)
    inv = pd.read_sql("SELECT * FROM inventory", conn)
    emp = pd.read_sql("SELECT * FROM employees", conn)

    st.download_button("Issued", issued.to_csv(index=False), "issued.csv")
    st.download_button("Inventory", inv.to_csv(index=False), "inventory.csv")
    st.download_button("Employees", emp.to_csv(index=False), "employees.csv")

# ---------------- RESET ----------------
elif menu == "Reset System":
    st.warning("Deletes only issued records")

    if st.button("Reset"):
        cursor.execute("DELETE FROM issued")
        conn.commit()
        st.success("Reset complete")

# ---------------- LOGOUT ----------------
elif menu == "Logout":
    st.session_state.login = False
    st.rerun()