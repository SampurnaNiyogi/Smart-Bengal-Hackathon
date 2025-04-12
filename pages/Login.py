import re

import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import time
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Get the JSON key path
service_account_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

if not service_account_path:
    raise ValueError("GOOGLE_APPLICATION_CREDENTIALS is not set in the .env file")

# Initialize Firebase only if not already initialized
if not firebase_admin._apps:
    cred = credentials.Certificate(service_account_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()

if "user_registered" not in st.session_state:
    st.session_state.user_registered = None

if "page" not in st.session_state:
    st.session_state.page = "login"

# Apply custom CSS
def apply_custom_css():
    st.markdown("""
    <style>
        /* Main colors and variables */
        :root {
            --primary-color: #3498db;
            --secondary-color: #2ecc71;
            --accent-color: #f39c12;
            --background-color: #f5f7fa;
            --text-color: #2c3e50;
            --card-bg: #ffffff;
            --error-color: #e74c3c;
            --success-color: #27ae60;
        }
        
        /* Reset Streamlit default styles */
        .st-emotion-cache-ak9fvk, .st-emotion-cache-nlujnt {
            padding-top: 0;
        }
        
        .stButton > button {
            background-color: var(--primary-color);
            color: white;
            border-radius: 8px;
            border: none;
            padding: 12px 20px;
            font-weight: 500;
            width: 100%;
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            background-color: #2980b9;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        
        /* Custom container styles */
        .login-container {
            background-color: transparent;
            border-radius: 8px;
            padding: 10px;
            box-shadow: 0 0px 0px rgba(0, 0, 0, 0);
            max-width: 0px;
            margin: 0 auto;
        }
        
        /* Header styles */
        .logo-header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .logo-icon {
            font-size: 50px;
            color: var(--primary-color);
        }
        
        h1, h2, h3 {
            color: var(--primary-color);
        }
        
        .subtitle {
            color: #7f8c8d;
            font-size: 16px;
        }
        
        /* Input field styles */
        .stTextInput > div > div > input {
            border-radius: 8px;
            padding: 12px 15px;
            border: 1px solid #dfe6e9;
            font-size: 16px;
        }
        
        .stTextInput > div > div > input:focus {
            border-color: var(--primary-color);
            box-shadow: none;
        }
        
        /* Alternative login options */
        .biometric-options {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-top: 20px;
        }
        
        .biometric-btn {
            background: none;
            border: none;
            cursor: pointer;
            display: flex;
            flex-direction: column;
            align-items: center;
            color: #7f8c8d;
        }
        
        .divider {
            display: flex;
            align-items: center;
            margin: 20px 0;
            color: #7f8c8d;
        }
        
        .divider::before, .divider::after {
            content: "";
            flex: 1;
            border-bottom: 1px solid #dfe6e9;
        }
        
        .divider span {
            padding: 0 10px;
            font-size: 14px;
        }
        
        /* Custom buttons layout */
        .buttons-container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-top: 20px;
        }
        
        /* #MainMenu {visibility: hidden;} */  /*
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .block-container {padding-top: 2rem; padding-bottom: 2rem;}
    </style>
    """, unsafe_allow_html=True)


def login_page():
    apply_custom_css()
     # Logo and header
    st.markdown("""
    <div class="logo-header">
        <div class="logo-icon">🛒</div>
        <h1>Smart Retail</h1>
        <p class="subtitle">Shop smarter, faster, easier</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Custom container for login options
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<h2 style="text-align: center;">Welcome</h2>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; margin: 15px 0;">Sign in or create an account to continue</p>', unsafe_allow_html=True)
    
    # Create two columns for buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Sign In"):
            st.session_state.user_registered = "Existing"
            st.rerun()
    
    with col2:
        if st.button("Sign Up"):
            st.session_state.user_registered = "New User"
            st.rerun()
    
    # Divider and biometric options
     # Divider
    st.markdown("""
    <div class="divider"><span>or continue with</span></div>
    """, unsafe_allow_html=True)
    
    # Embed fingerprint image as base64 string
    fingerprint_base64 = """
    <!-- Insert your base64 encoded image string here -->
    """
    st.markdown(f"""
    <div style="display: flex; flex-direction: column; align-items: center;">
        <img src="data:image/png;base64,{fingerprint_base64}" style="width:60px; height:60px; margin-bottom:8px;">
    </div>
    """, unsafe_allow_html=True)
    if st.button("Fingerprint"):
        st.info("Fingerprint authentication coming soon!")
    
   
    st.markdown('</div>', unsafe_allow_html=True)

def validate_name_email(name: str, email: str) -> bool:
    if not name and not email:
        st.error("Both name and email fields are empty")
        return False
    elif not name:
        st.error("Name field is empty")
        return False
    elif not email:
        st.error("Email field is empty")
        return False
    # Cryptic email regex for email validation
    email_regex = re.compile(r"^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$")
    if not email_regex.match(email):
        st.error("Email address is not valid")
        return False
    return True


def add_user(name, email):
    try:
        is_valid = validate_name_email(name, email)
        if not is_valid:
            return False
        users_ref = db.collection("users")
        users_ref.add({"name": name, "email": email})
        st.session_state.user_registered = True
        return True
    except Exception as e:
        st.error(f"Error adding user: {e}")
        return False


def register():
    apply_custom_css()
    
    # Logo and header
    st.markdown("""
    <div class="logo-header">
        <div class="logo-icon">🛒</div>
        <h1>Smart Retail</h1>
        <p class="subtitle">Shop smarter, faster, easier</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Custom container for sign up form
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<h2 style="text-align: center;">Create Account</h2>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; margin: 15px 0;">Join our smart shopping experience</p>', unsafe_allow_html=True)
    
    name = st.text_input("Enter Name")
    email = st.text_input("Enter Email")
    
    if st.button("Sign Up"):
        if add_user(name, email):
            st.success(f"User {name} added successfully!")
            st.session_state.page = "consumer_dashboard"
            st.session_state.user_registered = "Existing"
            status_placeholder = st.empty()
            with status_placeholder.status("Loading......"):
                for i in range(1):
                    time.sleep(1)
            status_placeholder.empty()
            st.rerun()
    # Back button
    if st.button("Back to Login"):
        st.session_state.user_registered = None
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


def authenticate() -> None:
    apply_custom_css()
     # Logo and header
    st.markdown("""
    <div class="logo-header">
        <div class="logo-icon">🛒</div>
        <h1>Smart Retail</h1>
        <p class="subtitle">Shop smarter, faster, easier</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Custom container for sign in form
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<h2 style="text-align: center;">Sign In</h2>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; margin: 15px 0;">Enter your details to continue</p>', unsafe_allow_html=True)

    u_name = st.text_input("Enter Name")
    email = st.text_input("Enter Email")

    if st.button("Sign In"):
        is_valid = validate_name_email(u_name, email)
        if not is_valid:
            return
        user_ref = db.collection("users").where("name", "==", u_name).where("email", "==", email).get()
        if user_ref:
            st.session_state["user_name"] = u_name
            # Centered Loading Text
            status_text = st.empty()
            status_text.markdown("<h3 style='text-align: center;'>Authenticating.....</h3>", unsafe_allow_html=True)

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
            st.switch_page("pages/Customer_dashboard.py")
        else:
            st.error("Incorrect name or email")
    # Back button
    if st.button("Back to Login"):
        st.session_state.user_registered = None
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)


if st.session_state.user_registered is None:
    login_page()
elif st.session_state.user_registered == "New User":
    register()
elif st.session_state.user_registered == "Existing":
    authenticate()
