import streamlit as st
from datetime import datetime
import hashlib
from database import supabase

st.set_page_config(page_title="Admin Panel", layout="wide")

# ---------------- AUTH ----------------
def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

# Auto-create admin if not exists
admins = supabase.table("admin_users").select("*").execute().data

if not admins:
    supabase.table("admin_users").insert({
        "username": "admin",
        "password_hash": hash_pw("admin123"),
        "created_at": str(datetime.now())
    }).execute()

# ---------------- LOGIN ----------------
if "login" not in st.session_state:
    st.session_state.login = False

if not st.session_state.login:
    st.title("🔐 Admin Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        res = supabase.table("admin_users") \
            .select("*") \
            .eq("username", username) \
            .execute().data

        if res and res[0]["password_hash"] == hash_pw(password):
            st.session_state.login = True
            st.rerun()
        else:
            st.error("Invalid credentials")

    st.stop()

# ---------------- SIDEBAR ----------------
st.sidebar.title("Admin Panel")

menu = st.sidebar.radio("Menu", [
    "Dashboard",
    "Add Inventory",
    "Add Employee",
    "View Records",
    "Logout"
])

# ---------------- DASHBOARD ----------------
if menu == "Dashboard":
    st.title("📊 Dashboard")

    inventory = supabase.table("inventory").select("*").execute().data
    issued = supabase.table("issued").select("*").execute().data

    total_stock = sum([i["total_stock"] for i in inventory])
    available_stock = sum([i["available_stock"] for i in inventory])
    issued_count = len([i for i in issued if i["status"] == "Issued"])

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Stock", total_stock)
    col2.metric("Available Stock", available_stock)
    col3.metric("Issued Items", issued_count)

    st.subheader("⚠ Low Stock Items")

    low_stock = [
        i for i in inventory if i["available_stock"] < 3
    ]

    st.dataframe(low_stock)

# ---------------- ADD INVENTORY ----------------
elif menu == "Add Inventory":
    st.title("➕ Add Inventory")

    eq = st.text_input("Equipment")
    brand = st.text_input("Brand")
    stock = st.number_input("Stock", 1, 100)

    if st.button("Add"):
        supabase.table("inventory").insert({
            "equipment": eq,
            "brand": brand,
            "total_stock": stock,
            "available_stock": stock,
            "created_at": str(datetime.now())
        }).execute()

        st.success("Inventory added")

# ---------------- ADD EMPLOYEE ----------------
elif menu == "Add Employee":
    st.title("👥 Add Employee")

    name = st.text_input("Name")
    dept = st.text_input("Department")

    if st.button("Add"):
        supabase.table("employees").insert({
            "name": name,
            "department": dept,
            "created_at": str(datetime.now())
        }).execute()

        st.success("Employee added")

# ---------------- VIEW RECORDS ----------------
elif menu == "View Records":
    st.title("📄 Issued Records")

    data = supabase.table("issued").select("*").execute().data

    st.dataframe(data)

# ---------------- LOGOUT ----------------
elif menu == "Logout":
    st.session_state.login = False
    st.rerun()