import streamlit as st
from datetime import datetime
from supabase_client import supabase


st.set_page_config(page_title="TT Inventory System", layout="wide")

st.title("🏓 TT Inventory System")

conn = get_connection()
cursor = conn.cursor()

tabs = st.tabs(["Issue", "Return", "Track"])

# -------- ISSUE --------
employees = supabase.table("employees").select("*").execute().data
inventory = supabase.table("inventory").select("*").execute().data

emp_list = [e["name"] for e in employees]
eq_list = list(set([i["equipment"] for i in inventory]))

emp = st.selectbox("Employee", emp_list)
eq = st.selectbox("Equipment", eq_list)

filtered = [
    i for i in inventory
    if i["equipment"] == eq
]

brands = [i["brand"] for i in filtered]
brand = st.selectbox("Brand", brands)

qty = st.number_input("Quantity", 1, 10, 1)

if st.button("Issue"):
    stock = supabase.table("inventory") \
        .select("*") \
        .eq("equipment", eq) \
        .eq("brand", brand) \
        .execute().data

    if stock and stock[0]["available_stock"] >= qty:

        supabase.table("inventory").update({
            "available_stock": stock[0]["available_stock"] - qty
        }).eq("equipment", eq).eq("brand", brand).execute()

        supabase.table("issued").insert({
            "employee_name": emp,
            "equipment": eq,
            "brand": brand,
            "qty": qty,
            "issue_time": str(datetime.now()),
            "status": "Issued"
        }).execute()

        st.success("Equipment issued successfully")

    else:
        st.error("Equipment currently unavailable, please contact admin")

# -------- RETURN --------
records = supabase.table("issued") \
    .select("*") \
    .eq("status", "Issued") \
    .execute().data

options = [f"{r['employee_name']} | {r['equipment']} | {r['brand']} | Qty:{r['qty']}" for r in records]

selected = st.selectbox("Select item", options)

if st.button("Return"):
    idx = records[options.index(selected)]

    supabase.table("issued").update({
        "status": "Returned",
        "return_time": str(datetime.now())
    }).eq("id", idx["id"]).execute()

    inv = supabase.table("inventory") \
        .select("*") \
        .eq("equipment", idx["equipment"]) \
        .eq("brand", idx["brand"]) \
        .execute().data[0]

    supabase.table("inventory").update({
        "available_stock": inv["available_stock"] + idx["qty"]
    }).eq("equipment", idx["equipment"]).eq("brand", idx["brand"]).execute()

    st.success("Returned successfully")

# -------- TRACK --------
data = supabase.table("issued").select("*").execute().data
st.dataframe(data)