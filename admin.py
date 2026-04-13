import streamlit as st
import hashlib
from datetime import datetime
from database import get_connection, init_db

init_db()

conn = get_connection()
cursor = conn.cursor()

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

# AUTO CREATE ADMIN
cursor.execute("SELECT * FROM admin_users")
if not cursor.fetchone():
    cursor.execute("""
        INSERT INTO admin_users (username, password_hash, created_at)
        VALUES (?, ?, ?)
    """, ("admin", hash_pw("admin123"), str(datetime.now())))
    conn.commit()

# LOGIN
if "login" not in st.session_state:
    st.session_state.login = False

if not st.session_state.login:
    st.title("Admin Login")

    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        res = cursor.execute(
            "SELECT password_hash FROM admin_users WHERE username=?", (u,)
        ).fetchone()

        if res and res[0] == hash_pw(p):
            st.session_state.login = True
            st.rerun()
        else:
            st.error("Invalid credentials")

    st.stop()

# DASHBOARD
st.sidebar.title("Admin")
menu = st.sidebar.radio("Menu", ["Dashboard", "Add Inventory", "Add Employee", "Logout"])

if menu == "Dashboard":
    st.title("Dashboard")

    total = cursor.execute("SELECT SUM(total_stock) FROM inventory").fetchone()[0] or 0
    avail = cursor.execute("SELECT SUM(available_stock) FROM inventory").fetchone()[0] or 0

    st.metric("Total", total)
    st.metric("Available", avail)

elif menu == "Add Inventory":
    e = st.text_input("Equipment")
    b = st.text_input("Brand")
    t = st.number_input("Stock", 1, 100)

    if st.button("Add"):
        cursor.execute("""
            INSERT INTO inventory VALUES (NULL, ?, ?, ?, ?, ?)
        """, (e, b, t, t, str(datetime.now())))
        conn.commit()
        st.success("Added")

elif menu == "Add Employee":
    n = st.text_input("Name")
    d = st.text_input("Department")

    if st.button("Add"):
        cursor.execute("""
            INSERT INTO employees VALUES (NULL, ?, ?, ?)
        """, (n, d, str(datetime.now())))
        conn.commit()
        st.success("Added")

elif menu == "Logout":
    st.session_state.login = False
    st.rerun()