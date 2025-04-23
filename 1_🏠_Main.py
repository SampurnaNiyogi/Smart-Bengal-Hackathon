import time
import streamlit as st
from utils import get_base64_encoded_image, load_svg

st.set_page_config(page_title="Cashier-Less Retail Shop", page_icon="🛒")

# Shopping Cart SVG Animation
loading_svg = f"""
<div style="display: flex; justify-content: center; align-items: center; height: 150px;">
    {load_svg('cart-loading.svg')}
</div>
"""

st.markdown('<div class="main-content">', unsafe_allow_html=True)

logo = get_base64_encoded_image('assets/logo.jpg')
# Optional: Add a brand logo
st.markdown(f"""
<div style="text-align: center;">
    <img src='{logo}' alt="Store Logo" width="120">
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
        st.switch_page("pages/2_🔐_Login.py")
