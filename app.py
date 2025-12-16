import streamlit as st
import pandas as pd
from pyairtable import Api
from datetime import datetime

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="BoochBooch Wholesale", page_icon="🍺", layout="centered")

# --- CONNECT TO AIRTABLE ---
try:
    # This connects to your database using the secrets you saved earlier
    api = Api(st.secrets["AIRTABLE_API_KEY"])
    table = api.table(st.secrets["AIRTABLE_BASE_ID"], st.secrets["AIRTABLE_TABLE_NAME"])
except Exception as e:
    st.error("⚠️ Connection Error: Could not connect to Airtable. Check your Secrets.")
    st.stop()

# --- MERGED CSS (Your Header Design + Mobile App Styles) ---
st.markdown("""
    <style>
    /* 1. HIDE DEFAULT STREAMLIT UI */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* 2. APP HEADER STYLES (From your latest update) */
    .header-container {
        display: flex;
        align-items: center;
        padding-bottom: 1rem;
        border-bottom: 1px solid #f0f0f0;
        margin-bottom: 1rem;
    }
    .logo {
        width: 40px;
        height: 40px;
        background-color: #ffedd5; /* orange-100 */
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        margin-right: 12px;
    }
    .title-container {
        display: flex;
        flex-direction: column;
    }
    .app-title {
        font-size: 20px;
        font-weight: 800;
        line-height: 1.25;
        color: #292524; /* stone-800 */
        margin: 0;
    }
    .subtitle {
        font-size: 10px;
        font-weight: 700;
        color: #f97316; /* orange-500 */
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin: 0;
    }
    .greeting {
        color: #a8a29e; /* stone-400 */
        font-size: 14px;
        font-weight: 500;
        margin-top: 8px;
        margin-bottom: 20px;
    }

    /* 3. MOBILE UI TWEAKS (Tabs & Buttons) */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 5rem !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
        padding-bottom: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 20px;
        color: #4a4a4a;
        font-weight: 600;
        border: none;
        flex: 1;
    }
    .stTabs [aria-selected="true"] {
        background-color: #f97316 !important; /* Match your Orange logo */
        color: white !important;
    }
    .stButton>button {
        width: 100%;
        border-radius: 50px;
        height: 3.5em;
        font-weight: bold;
        border: none;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.1);
        background-color: #292524; /* Dark Stone color */
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# --- HEADER LOGIC (Dynamic Greeting) ---
now = datetime.now()
hour = now.hour
if hour < 12:
    greeting_text = "Good Morning, Let's Brew! ☀️"
elif hour < 18:
    greeting_text = "Good Afternoon, Keep Flowing! 🌊"
else:
    greeting_text = "Good Evening, Cheers! 🍻"

# Render the Header
st.markdown(f"""
    <div class="header-container">
        <div class="logo">🍺</div>
        <div class="title-container">
            <h1 class="app-title">BoochBooch</h1>
            <p class="subtitle">Wholesale Portal</p>
        </div>
    </div>
    <p class="greeting">{greeting_text}</p>
""", unsafe_allow_html=True)

# --- MAIN APP TABS ---
tab1, tab2, tab3 = st.tabs(["🛒 Order", "🚚 Status", "🔒 Admin"])

# ==========================================
# TAB 1: NEW ORDER FORM
# ==========================================
with tab1:
    with st.form("order_form", clear_on_submit=True):
        st.write("**Create New Order**")
        client_name = st.text_input("🏢 Business Name")
        client_code = st.text_input("🔑 Secret Code", type="password")
        
        c1, c2 = st.columns(2)
        with c1:
            flavor = st.selectbox("Flavor", ["Original", "Peach", "Ginger", "Berry"])
        with c2:
            size = st.selectbox("Size", ["24-Pack", "48-Pack", "Keg"])
            
        qty = st.number_input("Quantity", min_value=1, value=1)
        
        submitted = st.form_submit_button("Submit Order")
        
        if submitted:
            if not client_name or not client_code:
                st.warning("Please enter your Business Name and Code.")
            else:
                # Prepare data for Airtable
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
                try:
                    table.create(new_record)
                    st.success(f"✅ Order Placed for {flavor}!")
                    st.balloons()
                except Exception as e:
                    st.error(f"Error saving to database: {e}")

# ==========================================
# TAB 2: CHECK STATUS
# ==========================================
with tab2:
    with st.expander("🔍 Find my orders", expanded=True):
        search_name = st.text_input("Business Name", key="s_name")
        search_code = st.text_input("Secret Code", type="password", key="s_code")
        
        if st.button("Check Status"):
            if search_name and search_code:
                # Fetch all records
                try:
                    all_records = table.all()
                    # Filter in Python (simple & reliable)
                    my_orders = [r['fields'] for r in all_records 
                                 if r['fields'].get('Client Name') == search_name 
                                 and r['fields'].get('Client Code') == search_code]
                    
                    if my_orders:
                        st.success(f"Found {len(my_orders)} orders.")
                        for order in reversed(my_orders):
                            # Card UI
                            with st.container():
                                st.markdown(f"""
                                <div style="background: white; padding: 15px; border-radius: 10px; border: 1px solid #e5e7eb; margin-bottom: 10px;">
                                    <div style="display: flex; justify-content: space-between;">
                                        <div style="font-weight: bold; font-size: 16px;">{order.get('Flavor')}</div>
                                        <div style="color: #f97316; font-weight: bold;">{order.get('Status', 'Pending')}</div>
                                    </div>
                                    <div style="color: #6b7280; font-size: 14px;">{order.get('Size')} • Qty: {order.get('Quantity')}</div>
                                    <div style="margin-top: 5px; font-size: 12px;">📅 Arrival: {order.get('Arrival Date', 'TBD')}</div>
                                </div>
                                """, unsafe_allow_html=True)
                    else:
                        st.warning("No orders found. Check your spelling.")
                except Exception as e:
                    st.error("Error fetching data.")

# ==========================================
# TAB 3: ADMIN DASHBOARD
# ==========================================
with tab3:
    pwd = st.text_input("Admin Password", type="password")
    
    if pwd == st.secrets["admin_password"]:
        st.success("Unlocked")
        
        # 1. Production Overview
        st.subheader("🏭 Production Plan")
        try:
            raw_data = table.all()
            if raw_data:
                df = pd.DataFrame([r['fields'] for r in raw_data])
                if not df.empty and "Status" in df.columns:
                    pending = df[df["Status"] != "Completed"]
                    
                    if not pending.empty:
                        # Group by Flavor
                        totals = pending.groupby("Flavor")["Quantity"].sum()
                        st.bar_chart(totals)
                        
                        # Big Number Metrics
                        cols = st.columns(len(totals))
                        for i, (flavor, count) in enumerate(totals.items()):
                            cols[i].metric(label=flavor, value=f"{count} Units")
                    else:
                        st.info("No pending orders!")
                
                # 2. Update Orders
                st.divider()
                st.subheader("Update Orders")
                
                # Create a list for the dropdown
                order_map = {r['id']: f"{r['fields'].get('Client Name')} | {r['fields'].get('Flavor')} ({r['fields'].get('Quantity')})" for r in raw_data}
                
                sel_id = st.selectbox("Select Order to Update", options=list(order_map.keys()), format_func=lambda x: order_map[x])
                
                if sel_id:
                    c1, c2 = st.columns(2)
                    with c1: new_stat = st.selectbox("New Status", ["Pending", "In Production", "Shipped", "Completed"])
                    with c2: new_date = st.text_input("Arrival Date", value="Friday")
                    
                    if st.button("Update Order"):
                        table.update(sel_id, {"Status": new_stat, "Arrival Date": new_date})
                        st.success("Order Updated!")
                        st.rerun()
        except Exception as e:
            st.error("Database empty or connection error.")