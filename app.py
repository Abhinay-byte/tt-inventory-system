import streamlit as st
from datetime import datetime
from database import get_connection, init_db

init_db()

st.set_page_config(page_title="TT Inventory System", layout="wide")

st.title("🏓 TT Inventory System")

conn = get_connection()
cursor = conn.cursor()

tabs = st.tabs(["Issue", "Return", "Track"])

# -------- ISSUE --------
with tabs[0]:
    st.subheader("Issue Equipment")

    employees = [e[0] for e in cursor.execute("SELECT name FROM employees").fetchall()]
    equipment = [e[0] for e in cursor.execute("SELECT DISTINCT equipment FROM inventory").fetchall()]

    if not employees or not equipment:
        st.warning("Please contact admin to setup employees and inventory")
        st.stop()

    emp = st.selectbox("Employee", employees)
    eq = st.selectbox("Equipment", equipment)

    brands = [b[0] for b in cursor.execute(
        "SELECT brand FROM inventory WHERE equipment=?", (eq,)
    ).fetchall()]

    brand = st.selectbox("Brand", brands)
    qty = st.number_input("Quantity", 1, 20, 1)

    if st.button("Issue"):
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
                (employee_name, equipment, brand, qty, issue_time, status)
                VALUES (?, ?, ?, ?, ?, 'Issued')
            """, (emp, eq, brand, qty, str(datetime.now())))

            conn.commit()
            st.success("✅ Issued successfully")
        else:
            st.error("❌ Equipment currently unavailable, please contact admin")

# -------- RETURN --------
with tabs[1]:
    st.subheader("Return Equipment")

    records = cursor.execute("""
        SELECT id, employee_name, equipment, brand, qty
        FROM issued WHERE status='Issued'
    """).fetchall()

    if not records:
        st.info("No issued items")
    else:
        options = [f"{r[1]} | {r[2]} | {r[3]} | Qty:{r[4]}" for r in records]
        selected = st.selectbox("Select Item", options)

        if st.button("Return"):
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
            st.success("✅ Returned successfully")

# -------- TRACK --------
with tabs[2]:
    st.subheader("Tracking")

    data = cursor.execute("""
        SELECT employee_name, equipment, brand, qty, issue_time, return_time, status
        FROM issued ORDER BY issue_time DESC
    """).fetchall()

    st.dataframe(data, use_container_width=True)