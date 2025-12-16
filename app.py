import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="BoochBooch Wholesale", page_icon="🍺", layout="centered")

# --- CONNECT TO GOOGLE SHEETS ---
try:
    # This connects using the [connections.gsheets] secret you just saved
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"Google Connection Error: {e}")
    st.stop()

# --- CUSTOM CSS (YOUR MOBILE DESIGN) ---
st.markdown("""
    <style>
    /* 1. HIDE DEFAULTS */
    header, footer {visibility: hidden;}
    .stApp {background-color: #FAFAF5;}
    .block-container {padding-top: 6rem !important; padding-bottom: 6rem !important;}

    /* 2. HEADER & TABS */
    .header-container {
        position: fixed; top: 0; left: 0; width: 100%;
        background: rgba(255, 255, 255, 0.85); backdrop-filter: blur(12px);
        z-index: 999; border-bottom: 1px solid white; padding: 15px 20px;
    }
    .stTabs {
        position: fixed; bottom: 0; left: 0; width: 100%;
        background: rgba(255, 255, 255, 0.95); border-top: 1px solid #e5e5e5;
        z-index: 999; padding: 10px 0 25px 0;
    }
    .stTabs [data-baseweb="tab-list"] {gap: 8px; background-color: transparent;}
    .stTabs [data-baseweb="tab"] {
        height: 50px; background-color: transparent; border: none;
        color: #78716c; font-size: 12px; font-weight: 600;
    }
    .stTabs [aria-selected="true"] {background-color: #FF4B4B !important; color: white !important;}
    
    /* 3. BUTTONS & CARDS */
    .stButton>button {
        width: 100%; border-radius: 16px; height: 3.5rem; font-weight: 700;
        border: none; background-color: #FF4B4B; color: white;
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
        <div style="display: flex; align-items: center; gap: 12px;">
            <div style="font-size: 20px;">🍺</div>
            <div>
                <div style="font-size: 18px; font-weight: 800; color: #292524;">BoochBooch</div>
                <div style="font-size: 10px; font-weight: 700; color: #f97316;">Wholesale Portal</div>
            </div>
        </div>
        <div style="font-size: 12px; color: #a8a29e; margin-top:5px;">{greeting}</div>
    </div>
""", unsafe_allow_html=True)

# --- TABS ---
tab_order, tab_status, tab_admin = st.tabs(["🛒 Order", "🚚 Status", "🔒 Admin"])

# ================= TAB 1: ORDER =================
with tab_order:
    st.markdown("### New Order")
    with st.container():
        st.markdown('<div style="background:white; padding:20px; border-radius:16px;">', unsafe_allow_html=True)
        with st.form("order_form", clear_on_submit=True):
            name = st.text_input("Business Name")
            code = st.text_input("Secret Code", type="password")
            c1, c2 = st.columns(2)
            with c1: flavor = st.selectbox("Flavor", ["Original", "Peach", "Ginger", "Berry"])
            with c2: size = st.selectbox("Size", ["24-Pack", "48-Pack", "Keg"])
            qty = st.number_input("Quantity", min_value=1, value=1)
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("Place Order"):
                if not name or not code:
                    st.warning("Please enter Name and Code")
                else:
                    new_data = pd.DataFrame([{
                        "Client Name": name, "Client Code": code,
                        "Flavor": flavor, "Size": size, "Quantity": qty,
                        "Status": "Pending", "Arrival Date": "TBD",
                        "Order Date": datetime.now().strftime("%Y-%m-%d")
                    }])
                    try:
                        # READ -> APPEND -> UPDATE
                        df = conn.read(worksheet="Sheet1")
                        updated_df = pd.concat([df, new_data], ignore_index=True)
                        conn.update(worksheet="Sheet1", data=updated_df)
                        st.success(f"Order for {flavor} placed!")
                        st.balloons()
                    except Exception as e:
                        st.error("Could not write to Sheet. Share it with your Service Account Email!")
        st.markdown('</div>', unsafe_allow_html=True)

# ================= TAB 2: STATUS =================
with tab_status:
    st.markdown("### My Orders")
    with st.expander("🔍 Filter Orders", expanded=True):
        s_name = st.text_input("Business Name", key="s_n")
        s_code = st.text_input("Secret Code", type="password", key="s_c")
        if st.button("Check"):
            try:
                df = conn.read(worksheet="Sheet1")
                # Filter Logic
                my_orders = df[
                    (df["Client Name"] == s_name) & 
                    (df["Client Code"].astype(str) == s_code)
                ]
                if not my_orders.empty:
                    st.success(f"Found {len(my_orders)} orders")
                    for index, row in my_orders.iterrows():
                        status_color = "#22c55e" if row['Status'] == 'Completed' else "#f97316"
                        st.markdown(f"""
                        <div style="background:white; padding:16px; border-radius:16px; margin-bottom:12px;">
                            <div style="display:flex; justify-content:space-between;">
                                <b>{row['Flavor']}</b>
                                <span style="color:{status_color}; font-weight:bold;">{row['Status']}</span>
                            </div>
                            <div style="color:#78716c; font-size:14px;">{row['Size']} • Qty: {row['Quantity']}</div>
                            <div style="font-size:12px; color:#a8a29e;">📅 Arrival: {row['Arrival Date']}</div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No orders found.")
            except Exception as e:
                st.error("Could not read Sheet.")

# ================= TAB 3: ADMIN =================
with tab_admin:
    st.markdown("### Admin Dashboard")
    pwd = st.text_input("Password", type="password")
    
    if pwd == st.secrets["admin_password"]:
        try:
            df = conn.read(worksheet="Sheet1")
            pending = df[df["Status"] != "Completed"]
            
            if not pending.empty:
                st.markdown('<div style="background:white; padding:20px; border-radius:16px; margin-bottom:20px;">', unsafe_allow_html=True)
                st.markdown("##### 🏭 Production Needs")
                totals = pending.groupby("Flavor")["Quantity"].sum()
                st.bar_chart(totals)
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div style="background:white; padding:20px; border-radius:16px;">', unsafe_allow_html=True)
            st.info("💡 To update Status/Dates, please edit the Google Sheet directly. It's safer and easier!")
            st.dataframe(df)
            st.markdown('</div>', unsafe_allow_html=True)
        except Exception as e:
            st.error("Error reading data.")
