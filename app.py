import streamlit as st
import pandas as pd
from pyairtable import Api
from datetime import datetime

# --- PAGE CONFIGURATION (Mobile First) ---
st.set_page_config(page_title="BoochBooch Orders", layout="centered", page_icon="🍺")

# --- CONNECT TO AIRTABLE ---
# We use a try/except block to handle errors gracefully
try:
    api = Api(st.secrets["AIRTABLE_API_KEY"])
    table = api.table(st.secrets["AIRTABLE_BASE_ID"], st.secrets["AIRTABLE_TABLE_NAME"])
except Exception as e:
    st.error("⚠️ Connection Error: Could not connect to Airtable. Check your Secrets.")
    st.stop()

# --- CUSTOM CSS (To hide default header and make it look like an app) ---
st.markdown("""
    <style>
    .block-container {padding-top: 1rem; padding-bottom: 0rem;} 
    .stTabs [data-baseweb="tab-list"] {gap: 10px;}
    .stTabs [data-baseweb="tab"] {height: 50px; white-space: pre-wrap; background-color: #f0f2f6; border-radius: 5px;}
    </style>
""", unsafe_allow_html=True)

# --- APP TITLE ---
st.title("🍺 BoochBooch Orders")

# --- NAVIGATION TABS ---
tab1, tab2, tab3 = st.tabs(["🛒 Order", "🚚 Status", "🔒 Admin"])

# ==========================================
# TAB 1: NEW ORDER (CLIENT)
# ==========================================
with tab1:
    st.header("Place New Order")
    
    with st.form("order_form", clear_on_submit=True):
        client_name = st.text_input("Business Name")
        client_code = st.text_input("Your Secret Code", type="password", help="Use the same code every time to track your orders.")
        
        c1, c2 = st.columns(2)
        with c1:
            flavor = st.selectbox("Flavor", ["Original", "Peach", "Ginger", "Berry"])
        with c2:
            size = st.selectbox("Size", ["24-Pack", "48-Pack", "Keg"])
            
        qty = st.number_input("Quantity", min_value=1, value=1)
        
        submitted = st.form_submit_button("Submit Order", use_container_width=True)
        
        if submitted:
            if not client_name or not client_code:
                st.warning("Please enter your Business Name and Code.")
            else:
                # 1. Create Data Dictionary
                new_record = {
                    "Client Name": client_name,
                    "Client Code": client_code,
                    "Flavor": flavor,
                    "Size": size,
                    "Quantity": qty,
                    "Status": "Pending",
                    "Arrival Date": "TBD",
                    "Order Date": datetime.now().strftime("%Y-%m-%d")
                }
                
                # 2. Send to Airtable
                try:
                    table.create(new_record)
                    st.success(f"✅ Order Placed for {flavor}!")
                    st.balloons()
                except Exception as e:
                    st.error(f"Error saving order: {e}")

# ==========================================
# TAB 2: CHECK STATUS (CLIENT)
# ==========================================
with tab2:
    st.header("My Order Status")
    
    # Simple Login to view records
    with st.expander("🔍 Find my orders", expanded=True):
        search_name = st.text_input("Enter Business Name", key="search_name")
        search_code = st.text_input("Enter Secret Code", type="password", key="search_code")
        
        if st.button("Check Status", use_container_width=True):
            if search_name and search_code:
                # Fetch all records and filter in Python (easier for beginners than API filters)
                all_records = table.all()
                my_orders = []
                
                for r in all_records:
                    data = r['fields']
                    # Check if Name and Code match
                    if (data.get('Client Name') == search_name and 
                        data.get('Client Code') == search_code):
                        my_orders.append(data)
                
                if not my_orders:
                    st.info("No orders found. Check your spelling or place a new order.")
                else:
                    st.success(f"Found {len(my_orders)} orders.")
                    # DISPLAY AS CARDS (Mobile Friendly)
                    for order in reversed(my_orders): # Show newest first
                        with st.container(border=True):
                            col_a, col_b = st.columns([3, 1])
                            with col_a:
                                st.markdown(f"**{order.get('Flavor')}** ({order.get('Size')})")
                                st.caption(f"Qty: {order.get('Quantity')}")
                            with col_b:
                                status = order.get('Status', 'Pending')
                                if status == "Pending":
                                    st.warning("⏳")
                                elif status == "Completed":
                                    st.success("✅")
                                else:
                                    st.info("🏭")
                            
                            st.text(f"Status: {status}")
                            st.text(f"Arrival: {order.get('Arrival Date', 'TBD')}")

# ==========================================
# TAB 3: ADMIN DASHBOARD
# ==========================================
with tab3:
    st.header("Admin Access")
    pwd = st.text_input("Password", type="password")
    
    if pwd == st.secrets["admin_password"]:
        st.success("Unlocked")
        
        # --- PRODUCTION SUMMARY ---
        st.subheader("🏭 Production Plan")
        
        # Fetch Data
        raw_data = table.all()
        if raw_data:
            # Convert to Pandas DataFrame for easy Math
            df = pd.DataFrame([r['fields'] for r in raw_data])
            
            # Filter for Pending Orders Only
            if "Status" in df.columns and "Quantity" in df.columns:
                pending_df = df[df["Status"] != "Completed"] # Show everything not done
                
                if not pending_df.empty:
                    # Group by Flavor and Sum Quantity
                    totals = pending_df.groupby("Flavor")["Quantity"].sum()
                    
                    # Display as big metrics
                    cols = st.columns(len(totals))
                    for i, (flavor, count) in enumerate(totals.items()):
                        st.metric(label=flavor, value=f"{count} units")
                else:
                    st.info("No pending production needed.")
            
            # --- MANAGE ORDERS ---
            st.markdown("---")
            st.subheader("Manage Orders")
            
            # Select an order to edit
            order_options = {r['id']: f"{r['fields'].get('Client Name')} - {r['fields'].get('Flavor')}" for r in raw_data}
            selected_id = st.selectbox("Select Order to Update", options=list(order_options.keys()), format_func=lambda x: order_options[x])
            
            if selected_id:
                # Find current status
                current_record = [r for r in raw_data if r['id'] == selected_id][0]['fields']
                
                c1, c2 = st.columns(2)
                with c1:
                    new_status = st.selectbox("Update Status", ["Pending", "In Production", "Completed"], index=0)
                with c2:
                    new_date = st.text_input("Update Arrival Date (YYYY-MM-DD)", value=current_record.get('Arrival Date', ''))
                
                if st.button("Update Order"):
                    table.update(selected_id, {"Status": new_status, "Arrival Date": new_date})
                    st.success("Order Updated!")
                    st.rerun() # Refresh page
        else:
            st.info("Database is empty.")
