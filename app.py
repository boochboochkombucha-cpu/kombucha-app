import streamlit as st
import datetime

# Page configuration
st.set_page_config(page_title="BoochBooch Wholesale Portal", page_icon="🍺", layout="centered")

# Styling to mimic the original look as much as possible using custom CSS
st.markdown("""
    <style>
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
    }
    </style>
""", unsafe_allow_html=True)

# Logic for greeting
now = datetime.datetime.now()
hour = now.hour

if hour < 12:
    greeting_text = "Good Morning, Let's Brew!"
elif hour < 18:
    greeting_text = "Good Afternoon, Keep Flowing!"
else:
    greeting_text = "Good Evening, Cheers!"

# Header
st.markdown(f"""
    <div class="header-container">
        <div class="logo">
            🍺
        </div>
        <div class="title-container">
            <h1 class="app-title">BoochBooch</h1>
            <p class="subtitle">Wholesale Portal</p>
        </div>
    </div>
    <p class="greeting">{greeting_text}</p>
""", unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3 = st.tabs(["🛒 Order", "🚚 Status", "🔒 Admin"])

with tab1:
    st.header("Order")
    st.info("Order component placeholder. The original React component `OrderTab` was missing.")
    # You could add some dummy content here to make it look active
    st.write("Browse our selection of hard kombuchas.")

with tab2:
    st.header("Status")
    st.info("Status component placeholder. The original React component `StatusTab` was missing.")
    st.write("Track your recent orders here.")

with tab3:
    st.header("Admin")
    st.info("Admin component placeholder. The original React component `AdminTab` was missing.")
    st.write("Manage inventory and users.")
