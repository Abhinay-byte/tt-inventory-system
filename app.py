import streamlit as st
from datetime import datetime
from database import get_connection, init_db

init_db()

st.set_page_config(page_title="TT Inventory System", layout="wide")

st.title("🏓 TT Inventory System (QR Portal)")

conn = get_connection()
cursor = conn.cursor()

tabs = st.tabs(["Issue Equipment", "Return Equipment", "Track Equipment"])

# ================= ISSUE =================
with tabs[0]:
    st.subheader("Issue Equipment")

    employees = cursor.execute("SELECT name FROM employees").fetchall()
    equipment = cursor.execute("SELECT DISTINCT equipment FROM inventory").fetchall()

    emp = st.selectbox("Employee", [e[0] for e in employees] if employees else [])
    eq = st.selectbox("Equipment", [e[0] for e in equipment] if equipment else [])

    brands = cursor.execute(
        "SELECT brand FROM inventory WHERE equipment=?",
        (eq,)
    ).fetchall() if eq else []

    brand = st.selectbox("Brand", [b[0] for b in brands] if brands else [])

    qty = st.number_input("Quantity", 1, 10, 1)

    if st.button("Issue Equipment"):
        stock = cursor.execute("""
            SELECT available_stock FROM inventory
            WHERE equipment=? AND brand=?
        """, (eq, brand)).fetchone()

        if stock and stock[0] >= qty:
            cursor.execute("""
                UPDATE inventory
                SET available_stock = available_stock - ?
                WHERE equipment=? AND brand=?
            """, (qty, eq, brand))

            cursor.execute("""
                INSERT INTO issued
                (employee_name, equipment, brand, qty, issue_time, return_time, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (emp, eq, brand, qty, str(datetime.now()), None, "Issued"))

            conn.commit()
            st.success("Equipment issued successfully")
        else:
            st.error("Equipment currently unavailable, please contact admin")

# ================= RETURN =================
with tabs[1]:
    st.subheader("Return Equipment")

    records = cursor.execute("""
        SELECT id, employee_name, equipment, brand, qty
        FROM issued
        WHERE status='Issued'
    """).fetchall()

    if records:
        options = [f"{r[1]} | {r[2]} | {r[3]} | Qty:{r[4]}" for r in records]
        selected = st.selectbox("Select Issued Item", options)

        if st.button("Return Equipment"):
            idx = records[options.index(selected)][0]

            rec = cursor.execute("""
                SELECT equipment, brand, qty FROM issued WHERE id=?
            """, (idx,)).fetchone()

            cursor.execute("""
                UPDATE issued
                SET status='Returned', return_time=?
                WHERE id=?
            """, (str(datetime.now()), idx))

            cursor.execute("""
                UPDATE inventory
                SET available_stock = available_stock + ?
                WHERE equipment=? AND brand=?
            """, (rec[2], rec[0], rec[1]))

            conn.commit()
            st.success("Equipment returned successfully")
    else:
        st.info("No issued items found")

# ================= TRACK =================
with tabs[2]:
    st.subheader("Track Equipment")

    data = cursor.execute("""
        SELECT employee_name, equipment, brand, qty, issue_time, return_time, status
        FROM issued
        ORDER BY issue_time DESC
    """).fetchall()

    st.dataframe(data)