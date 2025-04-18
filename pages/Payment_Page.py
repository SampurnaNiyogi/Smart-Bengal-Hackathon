import time

import requests
import streamlit as st

BASE_URL = "http://127.0.0.1:5000"


# Custom Sidebar Styling
st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            background: linear-gradient(145deg, #1f1f2f, #191926);
            padding-top: 2rem;
            transition: all 0.3s ease-in-out;
        }
        [data-testid="stSidebar"]:hover {
            background: linear-gradient(145deg, #292940, #1f1f2f);
        }
        [data-testid="stSidebar"] * {
            color: #f0f0f0 !important;
            font-family: 'Segoe UI', sans-serif;
        }
        .stSelectbox > div {
            padding: 10px 0;
        }
    </style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    page = st.selectbox("📂 Navigate to", [
        "🏠 Main",
        "🛒 Cart Dashboard",
        "👥 Customer Dashboard",
        "🔐 Login",
        "💳 Payment Page",
        "🔎 Search Dashboard",
        "🗺️ Store Map"
    ])

# Route (manual redirect if all logic is in main.py)
if page == "🏠 Main":
    st.title("")
elif page == "🛒 Cart Dashboard":
    st.switch_page("pages/Cart_Dashboard.py")
elif page == "👥 Customer Dashboard":
    st.switch_page("pages/Customer_Dashboard.py")
elif page == "🔐 Login":
    st.switch_page("pages/Login.py")
elif page == "💳 Payment Page":
    st.switch_page("pages/Payment_page.py")
elif page == "🔎 Search Dashboard":
    st.switch_page("pages/Search_Dashboard.py")
elif page == "🗺️ Store Map":
    st.switch_page("pages/Store_map.py")


# Hide default Streamlit sidebar & footer
st.markdown("""
    <style>
        /* Hide top-right hamburger menu */
        #MainMenu {visibility: hidden;}
        
        /* Hide footer */
        footer {visibility: hidden;}
        
        /* Optional: Hide sidebar toggle completely */
        .css-1d391kg {display: none}
    </style>
""", unsafe_allow_html=True)



st.title("💳 Payment Gateway")

if "user_name" not in st.session_state or "checkout_payload" not in st.session_state:
    st.warning("You have not initiated a checkout.")
    st.stop()

user_id = st.session_state["user_name"]


# Fake UI
st.markdown("""
<style>
.payment-box {
    padding: 1.5rem;
    background-color: #2E5077;
    border-radius: 10px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    margin: 2rem 0;
    text-align: center;
}
.pay-button {
    background-color: #27ae60;
    color: white;
    padding: 0.8rem 1.5rem;
    font-size: 1.2rem;
    border-radius: 8px;
    border: none;
}
</style>
<div class="payment-box">
    <h3>Choose Payment Method</h3>
    <p>UPI | Card | Wallet | NetBanking</p>
</div>
""", unsafe_allow_html=True)
if "user_name" not in st.session_state or "checkout_payload" not in st.session_state:
    st.error("⚠️ Missing user session or checkout info.")
    st.stop()

user_id = st.session_state["user_name"]
user_email = st.session_state['user_email']
checkout_payload = st.session_state["checkout_payload"]
st.markdown("### Choose Payment Method")
st.radio("Select one:", ["UPI", "Credit Card", "Net Banking", "Wallets"], horizontal=True)

if st.session_state.get("switch_to_home"):
    with st.spinner("⏳ Redirecting to Cart dashboard..."):
        time.sleep(2.5)
    # Clear flag and switch page
    st.session_state["switch_to_cart"] = False
    st.switch_page("pages/Customer_dashboard.py")

if st.button("💸 Pay Now", use_container_width=True):
    with st.spinner("Processing Payment..."):
        time.sleep(3)

        response = requests.post(f"{BASE_URL}/{user_id}/final_checkout", json=checkout_payload)
        # Contains email, cart details, timestamp, provider and branch
        invoice_payload = {'email': user_email, **(response.json()), **checkout_payload}
    if response.status_code == 200:
        invoice_generate = requests.post(f'{BASE_URL}/{user_id}/generate_invoice',
                                         json=invoice_payload)
        if invoice_generate.status_code == 200:
            with open("invoice.pdf", "rb") as f:
                st.download_button(
                    label="⬇️ Download Your Invoice",
                    data=f,
                    file_name="invoice.pdf",
                    mime="application/pdf"
                )
        else: 
            st.error("Error generating invoice")

        invoice_send = requests.post(f"{BASE_URL}/{user_id}/send_invoice_email", json=invoice_payload)
        st.success("🎉 Payment successful! Your order has been placed.")
        if invoice_send.status_code == 200:
            st.success(f"✅ Invoice Email Sent")
            st.toast(f"📧 Invoice sent to {user_id}'s email", icon="✅")
        else: 
            st.error("Error Sending Invoice Email")

        st.toast("🛍️ You can now view your order history.", icon="📦")
        time.sleep(2)
        st.session_state["switch_to_home"] = True
        st.rerun()
    else:
        st.error("❌ Payment failed.")
        st.toast("⚠️ Please try again.")
if st.button("Cancel Payment", use_container_width=True):
    with st.spinner("Returning to Cart....."):
        time.sleep(4)
    st.switch_page("pages/Cart_dashboard.py")
