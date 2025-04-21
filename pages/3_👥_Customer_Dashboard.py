import streamlit as st
import requests
from utils import load_css


# Custom Sidebar Styling

# Hide default Streamlit sidebar & footer

# Inject custom CSS to hide Streamlit's default UI
# Custom CSS for enhanced styling
@st.cache_data
def load_customer_css(filename='customer-dashboard.css'):
    css = load_css(filename)
    return f"<style>{css}</style>"


if "user_name" in st.session_state:
    name = st.session_state['user_name']
else:
    st.error('For the love of god please register/login to view this page', icon=':material/error:')
    st.stop()

if "retail" not in st.session_state:
    st.session_state.retail = False

if "branch" not in st.session_state:
    st.session_state.branch = False

customer_css = load_customer_css()
st.markdown(customer_css, unsafe_allow_html=True)

BASE_URL = "http://127.0.0.1:5000"

# Main header
st.markdown(f'<div class="main-header">Smart Cashier-less Retail System</div>', unsafe_allow_html=True)
st.markdown(f'<div class="welcome-message">Hi {name}! Welcome to our smart shopping experience.</div>',
            unsafe_allow_html=True)

# Fetch retailers
response = requests.get(f"{BASE_URL}/get_providers")
if response.status_code == 200:
    provider_options = response.json()  # List of provider document names
else:
    provider_options = ["Error fetching retail"]

# Retailer selection section
# st.markdown('<div class="selection-container">', unsafe_allow_html=True)
st.markdown('<div class="selection-header">Select Your Retailer</div>', unsafe_allow_html=True)

retailer_option = st.selectbox("Select retailer:", provider_options)
st.session_state.retail = retailer_option

# Fetch branches dynamically based on selected provider
if retailer_option and retailer_option != "Error fetching providers":

    # st.markdown(f'<div class="selection-result">Selected retailer: {retailer_option}</div>', unsafe_allow_html=True)
    # Fetch branches dynamically based on selected provider
    response_branches = requests.get(f"{BASE_URL}/{retailer_option}/get_branch")

    if response_branches.status_code == 200:
        branch_options = response_branches.json()
    else:
        branch_options = ["No branches found"]

    st.markdown('<div class="selection-header" style="margin-top: 1rem;">Select Branch Location</div>',
                unsafe_allow_html=True)
    selected_branch = st.selectbox("Choose a Branch:", branch_options, label_visibility="collapsed")
    st.session_state.branch = selected_branch

    # if selected_branch:
    # st.markdown(f'<div class="selection-result">Selected branch: {selected_branch}</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Action buttons
col1, col2 = st.columns(2)
with col1:
    if st.button("🔍 Search Products"):
        st.switch_page("pages/4_🔎_Search_Dashboard.py")

with col2:
    if st.button("🛒 View Cart"):
        st.switch_page("pages/5_🛒_Cart_Dashboard")
    st.markdown('</div>', unsafe_allow_html=True)
