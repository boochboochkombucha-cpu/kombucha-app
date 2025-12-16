import streamlit as st
import pandas as pd
from pyairtable import Api
from datetime import datetime

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="BoochBooch Wholesale", page_icon="🍺", layout="centered")

# --- CONNECT TO AIRTABLE ---
try:
    api = Api(st.secrets["AIRTABLE_API_KEY"])
    table = api.table(st.secrets["AIRTABLE_BASE_ID"], st.secrets["AIRTABLE_TABLE_NAME"])
except Exception as e:
    st.error(f"Airtable Error: {e}")
    st.stop()

# --- CUSTOM CSS (Translating React Design to Streamlit) ---
st.markdown("""
    <style>
    /* 1. HIDE DEFAULT UI */
    header, footer {visibility: hidden;}
    
    /* 2. MAIN CONTAINER STYLING */
    .stApp {
        background-color: #FAFAF5; /* Light Beige Background */
    }
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 8rem !important; /* Space for fixed bottom nav */
    }

    /* 3. HEADER STYLING */
    .header-container {
        position: sticky;
        top: 0;
        z-index: 100;
        background: rgba(255, 255, 255, 0.5);
        backdrop-filter: blur(10px);
        padding: 20px;
        border-bottom: 1px solid white;
        margin: -1rem -1rem 2rem -1rem; /* Stretch to edges */
    }
    .logo-box {
        width: 40px; 
        height: 40px; 
        background-color: #ffedd5; /* orange-100 */
        border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-size: 20px;
        margin-right: 12px;
    }
    .title-text { font-size: 20px; font-weight: 800; color: #292524; line-height: 1.2; }
    .subtitle-text { font-size: 10px; font-weight: 700; color: #f97316; letter-spacing: 0.1em; text-transform: uppercase; }
    .greeting-text { color: #a8a29e; font-size: 14px; font-weight: 500; margin-top: 8px; }

    /* 4. TABS AS BOTTOM NAVIGATION */
    /* We trick Streamlit tabs to look like the bottom bar */
    .stTabs {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background: rgba(255,255,255,0.9);
        backdrop-filter: blur(10px);
        z-index: 999;
        border-top: 1px solid #e5e5e5;
        padding: 10px 10px 20px 10px;
    }
    .stTabs [data-baseweb="tab-list"] {
        justify-content: space-around;
        gap: 10px;
        background-color: #f5f5f4; /* Stone-100 */
        padding: 5px;
        border-radius: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        flex: 1;
        height: 50px;
        border-radius: 20px;
        border: none;
        background-color: transparent;
        color: #78716c; /* Stone-500 */
        font-weight: 700;
        font-size: 12px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FF4B4B !important;
        color: white !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    /* 5. CARD & BUTTON STYLING */
    .stButton>button {
        width: 100%;
        border-radius: 24px;
        height: 3.5rem;
        font-weight: 700;
        border: none;
        background-color: #FF4B4B;
        color: white;
    }
    .card {
        background: white;
        padding: 16px;
        border-radius: 16px;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
        margin-bottom: 12px;
    }
    </style>
""", unsafe_allow_html=True)

# --- HEADER SECTION ---
now = datetime.now()
hour = now.hour
if hour < 12: greeting = "Good Morning, Let's Brew! ☀️"
elif hour < 18: greeting = "Good Afternoon, Keep Flowing! 🌊"
else: greeting = "Good Evening, Cheers! 🍻"

st.markdown(f"""
    <div class="header-container">
        <div style="display: flex; align-items: center;">
            <div class="logo-box">🍺</div>
            <div>
                <div class="title-text">BoochBooch</div>
                <div class="subtitle-text">Wholesale Portal</div>
            </div>
        </div>
        <div class="greeting-text">{greeting}</div>
    </div>
""", unsafe_allow_html=True)

# --- MAIN CONTENT ---
# Note: Streamlit renders tabs from top to bottom, but our CSS moves them to the bottom!
tab_order, tab_status, tab_admin = st.tabs(["🛒 Order", "🚚 Status", "🔒 Admin"])

# ==========================================
# TAB 1: ORDER
# ==========================================
with tab_order:
    st.markdown("<br>", unsafe_allow_html=True) # Spacing for fixed header
    with st.container():
        st.markdown("### New Order")
        with st.form("order_form", clear_on_submit=True):
            name = st.text_input("Business Name")
            code = st.text_input("Secret Code", type="password")
            
            c1, c2 = st.columns(2)
            with c1: flavor = st.selectbox("Flavor", ["Original", "Peach", "Ginger", "Berry"])
            with c2: size = st.selectbox("Size", ["24-Pack", "48-Pack", "Keg"])
            
            qty = st.number_input("Quantity", min_value=1, value=1)
            submit = st.form_submit_button("Place Order")
            
            if submit:
                if not name or not code:
                    st.warning("Details missing!")
                else:
                    try:
                        table.create({
                            "Client Name": name, "Client Code": code,
                            "Flavor": flavor, "Size": size, "Quantity": qty,
                            "Status": "Pending", "Arrival Date": "TBD",
                            "Order Date": datetime.now().strftime("%Y-%m-%d")
                        })
                        st.success(f"Order for {flavor} placed!")
                        st.balloons()
                    except Exception as e:
                        st.error(f"Airtable Error: {e}")

# ==========================================
# TAB 2: STATUS
# ==========================================
with tab_status:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### Track Orders")
    
    with st.expander("🔐 Login to View", expanded=True):
        s_name = st.text_input("Business Name", key="s_n")
        s_code = st.text_input("Secret Code", type="password", key="s_c")
        
        if st.button("Check Status"):
            try:
                records = table.all()
                my_orders = [r['fields'] for r in records if r['fields'].get('Client Name') == s_name and r['fields'].get('Client Code') == s_code]
                
                if my_orders:
                    st.success(f"Found {len(my_orders)} orders")
                    for o in reversed(my_orders):
                        status_color = "#22c55e" if o.get('Status') == 'Completed' else "#f97316"
                        st.markdown(f"""
                        <div class="card">
                            <div style="display:flex; justify-content:space-between; font-weight:bold;">
                                <span>{o.get('Flavor')}</span>
                                <span style="color:{status_color}">{o.get('Status', 'Pending')}</span>
                            </div>
                            <div style="color:#78716c; font-size:0.9em;">
                                {o.get('Size')} • Qty: {o.get('Quantity')}
                            </div>
                            <div style="margin-top:8px; font-size:0.8em; color:#a8a29e;">
                                📅 Arrival: {o.get('Arrival Date', 'TBD')}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No orders found.")
            except Exception as e:
                st.error(f"Error: {e}")

# ==========================================
# TAB 3: ADMIN
# ==========================================
with tab_admin:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### Admin Dashboard")
    
    pwd = st.text_input("Password", type="password")
    if pwd == st.secrets["admin_password"]:
        try:
            raw = table.all()
            if raw:
                df = pd.DataFrame([r['fields'] for r in raw])
                
                # Production Stats
                if "Status" in df.columns:
                    pending = df[df["Status"] != "Completed"]
                    if not pending.empty:
                        st.markdown("##### 🏭 Production Needs")
                        totals = pending.groupby("Flavor")["Quantity"].sum()
                        st.bar_chart(totals)
                
                # Update Tool
                st.divider()
                st.markdown("##### ✏️ Update Order")
                order_map = {r['id']: f"{r['fields'].get('Client Name')} | {r['fields'].get('Flavor')}" for r in raw}
                sel_id = st.selectbox("Select Order", list(order_map.keys()), format_func=lambda x: order_map[x])
                
                if sel_id:
                    c1, c2 = st.columns(2)
                    with c1: n_stat = st.selectbox("Status", ["Pending", "In Production", "Shipped", "Completed"])
                    with c2: n_date = st.text_input("Arrival Date", value="Friday")
                    
                    if st.button("Update"):
                        table.update(sel_id, {"Status": n_stat, "Arrival Date": n_date})
                        st.success("Updated!")
                        st.rerun()
        except Exception as e:
            st.error(f"Airtable Error: {e}")