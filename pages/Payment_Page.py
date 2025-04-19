import time
import requests
import streamlit as st
from utils import load_css

BASE_URL = "http://127.0.0.1:5000"

st.title("💳 Payment Gateway")

if "user_name" not in st.session_state or "checkout_payload" not in st.session_state:
    st.warning("You have not initiated a checkout.")
    st.stop()

@st.cache_data
def load_payment_css(filename='payment-page.css'):
    css = load_css(filename)
    return f'<style>{css}</style>'


payment_css = load_payment_css()
user_id = st.session_state["user_name"]

# Fake UI
st.markdown(payment_css, unsafe_allow_html=True)
st.markdown("""
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
    st.session_state["switch_to_cart"] = False
    st.switch_page("pages/Customer_dashboard.py")

if st.button("💸 Pay Now", use_container_width=True):
    with st.spinner("Processing Payment..."):
        time.sleep(3)

        response = requests.post(f"{BASE_URL}/{user_id}/final_checkout", json=checkout_payload)
        # Contains email, cart details, timestamp, provider and branch
        invoice_payload = {'email': user_email, **(response.json()), **checkout_payload}
    if response.status_code == 200:
        st.success("🎉 Payment successful! Your order has been placed.")
        invoice_send = requests.post(f"{BASE_URL}/{user_id}/send_invoice_email", json=invoice_payload)
        if invoice_send.status_code == 200:
            st.success("✅ Invoice Email Sent")
            st.toast(f"📧 Invoice sent to {user_id}'s email", icon="✅")
            st.toast("🛍️ You can now view your order history.", icon="📦")
            with st.empty():
                for secs in range(5, 0, -1):
                    st.write(f'⏳ Redirecting in {secs} seconds...' if secs
                             else '⌛ Redirecting to Customer dashboard...')
                    time.sleep(1)

            st.session_state["switch_to_home"] = True
            st.rerun()
        else:
            st.error(invoice_send.json()['error'], icon='❌')
    else:
        st.error(f"❌ Payment failed. Reason: {response.json()['error']}")
        st.toast("⚠️ Please try again.")
if st.button("Cancel Payment", use_container_width=True):
    with st.spinner("Returning to Cart....."):
        time.sleep(4)
    st.switch_page("pages/Cart_dashboard.py")
