import streamlit as st
import time

st.set_page_config(page_title="Cashier-Less Retail Shop", page_icon="🛒")


st.markdown('<div class="main-content">', unsafe_allow_html=True)


# Optional: Add a brand logo
st.markdown("""
<div style="text-align: center;">
    <img src="assets/logo.jpg" alt="Store Logo" width="120">
</div>
""", unsafe_allow_html=True)


st.image("assets/logo2.jpg", width=120)

st.title("Cashier-Less Retail Shop")










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
        color:#E8C999 !important
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
    "<h3 style='text-align: center; color: #9ACBD0;'>Welcome! Get ready for a seamless shopping experience.</h3>",
    unsafe_allow_html=True)
time.sleep(1)

# Ensure the button appears correctly
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("Enjoy Shopping", use_container_width=True):
        st.switch_page("pages/Login.py")
