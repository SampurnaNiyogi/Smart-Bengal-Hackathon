import streamlit as st
import time

st.set_page_config(page_title="Cashier-Less Retail Shop", page_icon="🛒")

# Optional: Add a brand logo
st.markdown("""
<div style="text-align: center;">
    <img src="assets/logo.jpg" alt="Store Logo" width="120">
</div>
""", unsafe_allow_html=True)


st.image("assets/logo2.jpg", width=120)

st.title("Cashier-Less Retail Shop")

import streamlit as st

st.markdown("""
    <style>
    /* Sidebar container */
    [data-testid="stSidebar"] {
        background-color: #0f1117;
        padding-top: 2rem;
    }

    /* Nav list */
    [data-testid="stSidebarNav"] > ul {
        padding-left: 0;
    }

    /* Nav items */
    [data-testid="stSidebarNav"] li {
        list-style-type: none;
        margin-bottom: 10px;
        border-radius: 10px;
        transition: all 0.3s ease;
    }

    [data-testid="stSidebarNav"] li a {
        color: #cfcfcf;
        font-size: 1rem;
        padding: 0.6rem 1rem;
        display: block;
        text-decoration: none;
    }

    [data-testid="stSidebarNav"] li:hover {
        background-color: #262a35;
    }

    /* Highlight for each page */
    [data-testid="stSidebarNav"] a[href$="/🏠_Main"] {
        background-color: #4b5563;
        font-weight: bold;
        color: white;
    }
    [data-testid="stSidebarNav"] a[href$="/🛒_Cart_Dashboard"] {
        background-color: #4a4a70;
        font-weight: bold;
        color: white;
    }
    [data-testid="stSidebarNav"] a[href$="/👤_Customer_Dashboard"] {
        background-color: #3f3f7d;
        font-weight: bold;
        color: white;
    }
    [data-testid="stSidebarNav"] a[href$="/🔐_Login"] {
        background-color: #374151;
        font-weight: bold;
        color: white;
    }
    [data-testid="stSidebarNav"] a[href$="/💳_Payment_Page"] {
        background-color: #3b3c5a;
        font-weight: bold;
        color: white;
    }
    [data-testid="stSidebarNav"] a[href$="/🔍_Search_Dashboard"] {
        background-color: #2f3d4f;
        font-weight: bold;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)



# Custom Button Styling
st.markdown("""
<style>
    div.stButton > button {
        background-color: #3498db;
        color: white;
        padding: 12px;
        font-size: 18px;
        border-radius: 8px;
        width: 100%;
        border: none;
    }
    div.stButton > button:hover {
        background-color: #2980b9;
    }
</style>
""", unsafe_allow_html=True)

# Centered Loading Text
status_text = st.empty()
status_text.markdown("<h3 style='text-align: center;'>Initializing...</h3>", unsafe_allow_html=True)

# Shopping Cart SVG Animation
loading_svg = """
<div style="display: flex; justify-content: center; align-items: center; height: 150px;">
    <svg width="80" height="80" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <g>
            <circle cx="9" cy="20" r="1.5" fill="#3498db">
                <animate attributeName="r" values="1.5;2;1.5" dur="0.6s" repeatCount="indefinite"/>
            </circle>
            <circle cx="17" cy="20" r="1.5" fill="#3498db">
                <animate attributeName="r" values="1.5;2;1.5" dur="0.6s" repeatCount="indefinite"/>
            </circle>
            <path d="M4 4H6L9 15H17L20 8H8" stroke="#3498db" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <animateTransform attributeName="transform" type="translate" values="0 0; 1 -1; 0 0" dur="0.6s" repeatCount="indefinite"/>
            </path>
        </g>
    </svg>
</div>
"""

loading_placeholder = st.empty()
loading_placeholder.markdown(loading_svg, unsafe_allow_html=True)

# Dynamic Loading Text Updates
time.sleep(1)
status_text.markdown("<h3 style='text-align: center;'>Loading...</h3>", unsafe_allow_html=True)
time.sleep(1)
status_text.markdown("<h3 style='text-align: center;'>Almost Done...</h3>", unsafe_allow_html=True)
time.sleep(1)

# Clear loading animations
loading_placeholder.empty()
status_text.empty()

# Display Welcome Message
st.markdown(
    "<h3 style='text-align: center; color: #2ecc71;'>Welcome! Get ready for a seamless shopping experience.</h3>",
    unsafe_allow_html=True)
time.sleep(1)

# Ensure the button appears correctly
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("Enjoy Shopping", use_container_width=True):
        st.switch_page("pages/Login.py")
