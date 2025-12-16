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

# --- CUSTOM CSS (THE MOBILE LAYOUT) ---
st.markdown("""
    <style>
    /* 1. RESET STREAMLIT DEFAULTS */
    header, footer {visibility: hidden;}
    .stApp {
        background-color: #FAFAF5; /* Light Beige */
    }
    
    /* 2. MAIN CONTENT PADDING (To avoid overlap with fixed header/footer) */
    .block-container {
        padding-top: 6rem !important; /* Space for Header */
        padding-bottom: 6rem !important; /* Space for Bottom Nav */
    }

    /* 3. STICKY HEADER (Glassmorphism) */
    .header-container {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(12px);
        z-index: 999;
        border-bottom: 1px solid white;
        padding: 15px 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    .header-content {
        max-width: 700px; /* Match Streamlit's 'centered' layout width */
        margin: 0 auto;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    
    /* 4. FIXED BOTTOM NAVIGATION BAR */
    /* This hacks the standard Streamlit tabs to move them to the bottom */
    .stTabs {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background: rgba(255, 255, 255, 0.95);
        border-top: 1px solid #e5e5e5;
        z-index: 999;
        padding: 10px 0 25px 0; /* Extra padding for iPhone home bar */
    }
    .stTabs [data-baseweb="tab-list"] {
        max-width: 700px;
        margin: 0 auto;
        gap: 8px;
        background-color: transparent;
        padding: 0 10px;
    }
    .stTabs [data-baseweb="tab"] {
        flex: 1;
        height: 50px;
        background-color: transparent;
        border: none;
        color: #78716c; /* Gray text */
        font-size: 12px;
        font-weight: 600;
        flex-direction: column; /* Stack icon and text if possible */
        border-radius: 12px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FF4B4B !important;
        color: white !important;
    }

    /* 5. COMPONENTS STYLING */
    .stButton>button {
        width: 100%;
        border-radius: 16px;
        height: 3.5rem;
        font-weight: 700;
        border: none;
        box-shadow: 0 4px 6px -1px rgba(255, 75, 75, 0.2);
        background-color: #FF4B4B;
        color: white;
    }
    
    /* Cards */
    div[data-testid="stVerticalBlock"] > div[style*="background-color"] {
        border-radius: 16px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

# --- HEADER SECTION (HTML) ---
now = datetime.now()
hour = now.hour
if hour < 12: greeting = "Good Morning, Let's Brew! ☀️"
elif hour < 18: greeting = "Good Afternoon, Keep Flowing! 🌊"
else: greeting = "Good Evening, Cheers! 🍻"

st.markdown(f"""
    <div class="header-container">
        <div class="header-content">
            <div style="display: flex; align-items: center; gap: 12px;">
                <div style="width: 40px; height: 40px; background: #ffedd5; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 20px;">🍺</div>
                <div>
                    <div style="font-size: 18px; font-weight: 800; color: #292524; line-height: 1;">BoochBooch</div>
                    <div style="font-size: 10px; font-weight: 700; color: #f97316; letter-spacing: 1px; text-transform: uppercase;">Wholesale Portal</div>
                </div>
            </div>
            <div style="font-size: 12px; font-weight: 500; color: #a8a29e;">{greeting}</div>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- NAVIGATION & CONTENT ---
# We use emojis in tabs to act as Icons
tab_order, tab_status, tab_admin = st.tabs(["🛒 Order", "🚚 Status", "🔒 Admin"])

# ==========================================
# TAB 1: ORDER
# ==========================================
with tab_order:
    st.markdown("### New Order")
    with st.container():
        # Add a white background card effect
        st.markdown('<div style="background:white; padding:20px; border-radius:16px; box-shadow:0 1px 3px rgba(0,0,0,0.05);">', unsafe_allow_html=True)
        
        with st.form("order_form", clear_on_submit=True):
            name = st.text_input("Business Name", placeholder="e.g. Cafe A")
            code = st.text_input("Secret Code", type="password")
            
            c1, c2 = st.columns(2)
            with c1: flavor = st.selectbox("Flavor", ["Original", "Peach", "Ginger", "Berry"])
            with c2: size = st.selectbox("Size", ["24-Pack", "48-Pack", "Keg"])
            
            qty = st.number_input("Quantity", min_value=1, value=1)
            
            st.markdown("<br>", unsafe_allow_html=True)
            submit = st.form_submit_button("Place Order")
            
            if submit:
                if not name or not code:
                    st.warning("Please enter Name and Code")
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
        
        st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# TAB 2: STATUS
# ==========================================
with tab_status:
    st.markdown("### My Orders")
    
    with st.expander("🔍 Filter Orders", expanded=True):
        s_name = st.text_input("Business Name", key="s_n")
        s_code = st.text_input("Secret Code", type="password", key="s_c")
        
        if st.button("Check"):
            try:
                records = table.all()
                my_orders = [r['fields'] for r in records if r['fields'].get('Client Name') == s_name and r['fields'].get('Client Code') == s_code]
                
                if my_orders:
                    st.success(f"Found {len(my_orders)} orders")
                    for o in reversed(my_orders):
                        # CUSTOM CARD UI
                        status_color = "#22c55e" if o.get('Status') == 'Completed' else "#f97316"
                        st.markdown(f"""
                        <div style="background:white; padding:16px; border-radius:16px; margin-bottom:12px; box-shadow:0 1px 2px rgba(0,0,0,0.05);">
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                                <span style="font-weight:700; font-size:16px;">{o.get('Flavor')}</span>
                                <span style="background:{status_color}20; color:{status_color}; padding:4px 8px; border-radius:8px; font-size:12px; font-weight:700;">
                                    {o.get('Status', 'Pending')}
                                </span>
                            </div>
                            <div style="color:#78716c; font-size:14px; margin-bottom:4px;">
                                {o.get('Size')} • Qty: {o.get('Quantity')}
                            </div>
                            <div style="font-size:12px; color:#a8a29e;">
                                📅 Expected: {o.get('Arrival Date', 'TBD')}
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
    st.markdown("### Admin Dashboard")
    
    pwd = st.text_input("Password", type="password")
    
    if pwd == st.secrets["admin_password"]:
        try:
            raw = table.all()
            if raw:
                df = pd.DataFrame([r['fields'] for r in raw])
                
                # Stats Card
                if "Status" in df.columns:
                    pending = df[df["Status"] != "Completed"]
                    if not pending.empty:
                        st.markdown('<div style="background:white; padding:20px; border-radius:16px; margin-bottom:20px;">', unsafe_allow_html=True)
                        st.markdown("##### 🏭 Production Needs")
                        totals = pending.groupby("Flavor")["Quantity"].sum()
                        st.bar_chart(totals)
                        st.markdown('</div>', unsafe_allow_html=True)
                
                # Update Card
                st.markdown('<div style="background:white; padding:20px; border-radius:16px;">', unsafe_allow_html=True)
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
                st.markdown('</div>', unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Airtable Error: {e}")