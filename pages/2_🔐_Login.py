import streamlit as st
import time
from utils import *
import requests

# Set page config early
st.set_page_config(page_title="Smart Retail - Login", page_icon="🛒", layout="centered")
# Shopping Cart SVG Animation
loading_svg = f"""
<div style="display: flex; justify-content: center; align-items: center; height: 150px;">
    {load_svg('cart-loading.svg')}
</div>
"""

if "user_registered" not in st.session_state:
    st.session_state.user_registered = None

if "page" not in st.session_state:
    st.session_state.page = "login"

if "fingerprint" not in st.session_state:
    st.session_state.fingerprint = False

if "fingerprint_scan_progress" not in st.session_state:
    st.session_state.fingerprint_scan_progress = 0

BASE_URL = "http://127.0.0.1:5000"

fingerprint_base64 = get_base64_encoded_image("assets/fingerprint.png")

login_css = load_css('login-page.css')


# Apply custom CSS
def apply_custom_css():
    st.markdown(login_css, unsafe_allow_html=True)


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
    st.markdown('<p style="text-align: center; margin: 15px 0;">Sign in or create an account to continue</p>',
                unsafe_allow_html=True)

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
    st.markdown('<div class="divider"><span>or continue with</span></div>', unsafe_allow_html=True)

    # Make the fingerprint image clickable
    col = st.columns([1, 2, 1])[1]  # Centered column
    with col:
        # Initialize
        if "img_button_clicked" not in st.session_state:
            st.session_state.img_button_clicked = False

        # HTML button with fingerprint image
        st.markdown(f"""
                <div class='center-wrapper'>
                    <form method="GET" action="">
                    <button type="submit" name="img_button_clicked" value="1"
                            style="border: none; background: none;">
                        <img src='{fingerprint_base64}'
                             alt="Click me" width="100" class='fingerprint-img' />
                    </button>
                    </form>
                </div>
                """, unsafe_allow_html=True)

        # Detect the query param on rerun
        if "img_button_clicked" in st.query_params:
            st.session_state.img_button_clicked = True
            st.query_params.clear()  # Reset the URL
            st.rerun()

        # Redirect to fingerprint page
        if st.session_state.img_button_clicked:
            st.session_state.img_button_clicked = False
            st.session_state.fingerprint = True
            st.rerun()
    st.markdown("<p style='text-align: center; color: #7f8c8d; margin-top: 10px;'>Tap to use fingerprint</p>",
                unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


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
    st.markdown('<p style="text-align: center; margin: 15px 0;">Join our smart shopping experience</p>',
                unsafe_allow_html=True)

    name = st.text_input("Enter Name")
    email = st.text_input("Enter Email")

    if st.button("Sign Up"):
        response = requests.post(f"{BASE_URL}/add_user", json={"name": name, "email": email})
        result = response.json()

        if result.get("success"):
            st.success(f"✅ User {name} added successfully!")
            st.session_state.page = "consumer_dashboard"
            st.session_state.user_registered = "Existing"

            # Progress-style spinner with status
            status_placeholder = st.empty()
            with status_placeholder.status("Loading..."):
                time.sleep(2)

            status_placeholder.empty()
            st.rerun()

        else:
            st.error(f"❌ {result.get('error', 'Something went wrong')}")

    # Back button
    if st.button("Back to Login"):
        st.session_state.user_registered = "None"
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
    st.markdown('<p style="text-align: center; margin: 15px 0;">Enter your details to continue</p>',
                unsafe_allow_html=True)

    u_name = st.text_input("Enter Name")
    email = st.text_input("Enter Email")

    if st.button("Sign In"):
        response = requests.post(f"{BASE_URL}/login_user", json={"name": u_name, "email": email})
        result = response.json()

        if result.get("success"):
            st.session_state["user_name"] = u_name
            st.session_state["user_email"] = email

            status_text = st.empty()
            status_text.markdown("<h3 style='text-align: center;'>Entering Store.....</h3>", unsafe_allow_html=True)

            loading_placeholder = st.empty()
            loading_placeholder.markdown(loading_svg, unsafe_allow_html=True)
            time.sleep(2)
            st.switch_page("pages/3_👥_Customer_Dashboard.py")
        else:
            st.error(result.get("error"))
    # Back button
    if st.button("Back to Login"):
        st.session_state.user_registered = None
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


def fingerprint_auth():
    apply_custom_css()
    # Logo and header
    st.markdown("""
    <div class="logo-header">
        <div class="logo-icon">🛒</div>
        <h1>Smart Retail</h1>
        <p class="subtitle">Shop smarter, faster, easier</p>
    </div>
    """, unsafe_allow_html=True)

    # Custom container for fingerprint authentication
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<h2 style="text-align: center;">Fingerprint Authentication</h2>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; margin: 15px 0;">Place your finger on the scanner</p>',
                unsafe_allow_html=True)

    # Fingerprint scanning animation
    scan_container = st.empty()
    scan_container.markdown(f"""
        <div class="fingerprint-container">
            <img src='{fingerprint_base64}' class="fingerprint-scan" />
            <div class="scan-line"></div>
        </div>
    """, unsafe_allow_html=True)

    # Progress bar for scan
    progress_bar = st.progress(0)
    status_text = st.empty()
    status_text.markdown("<p style='text-align: center;'>Scanning fingerprint...</p>", unsafe_allow_html=True)

    # Simulate scanning progress
    for i in range(101):
        progress_bar.progress(i)
        if i < 30:
            status_text.markdown("<p style='text-align: center;'>Scanning fingerprint...</p>", unsafe_allow_html=True)
        elif i < 60:
            status_text.markdown("<p style='text-align: center;'>Analyzing print pattern...</p>",
                                 unsafe_allow_html=True)
        elif i < 90:
            status_text.markdown("<p style='text-align: center;'>Verifying ...</p>", unsafe_allow_html=True)
        else:
            status_text.markdown("<p style='text-align: center;'>Authenticating...</p>", unsafe_allow_html=True)

    response = requests.get(f"{BASE_URL}/fingerprint_auth")

    if response.status_code == 200:
        user_details = response.json()
        st.session_state["user_name"] = user_details["user_name"]
        st.session_state["user_email"] = user_details["user_email"]
        st.session_state["fingerprint_id"] = user_details["fingerprint_id"]

        time.sleep(2)
        status_text.markdown("<p style='text-align: center;'>Authentication successful!.....</p>",
                             unsafe_allow_html=True)
        time.sleep(0.05)  # Adjust speed of scan

        # Success message
        st.toast("Authentication successful! Redirecting to store...")

        # Remove scan line after completion
        scan_container.markdown(f"""
            <div class="fingerprint-container">
                <img src='{fingerprint_base64}' class="fingerprint-scan" />
            </div>
        """, unsafe_allow_html=True)

        time.sleep(4)

        loading_placeholder = st.empty()
        loading_placeholder.markdown(loading_svg, unsafe_allow_html=True)

        # Dynamic Loading Text Updates
        time.sleep(1)
        status_text.markdown("<h3 style='text-align: center;'>Entering Store...</h3>", unsafe_allow_html=True)
        time.sleep(1)
        # Clear loading animations
        loading_placeholder.empty()
        status_text.empty()

        # Redirect to dashboard
        st.switch_page("pages/3_👥_Customer_Dashboard.py")
        # Back button (will only show if redirect fails)
        if st.button("Back to Login"):
            st.session_state.fingerprint = False
            st.session_state.user_registered = None
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.error("Authentication failed....  Status code: {response.status_code}, Error: {response.text}")


def main():
    if st.session_state.fingerprint:
        fingerprint_auth()
    elif st.session_state.user_registered is None:
        login_page()
    elif st.session_state.user_registered == "New User":
        register()
    elif st.session_state.user_registered == "Existing":
        authenticate()


main()
