import time

import requests
import streamlit as st

BASE_URL = "http://127.0.0.1:5000"

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
        if invoice_send.status_code == 200:
            st.success(f"✅ Invoice Email Sent")
            st.toast(f"📧 Invoice sent to {user_id}'s email", icon="✅")
            st.rerun()
        else: 
            st.error("Error Sending Invoice Email")

        st.success("🎉 Payment successful! Your order has been placed.")
        st.toast("🛍️ You can now view your order history.", icon="📦")
        
        with st.spinner("⏳ Returning to Cart dashboard..."):
            time.sleep(2.5)  # Delay for effect
            st.rerun()
        st.switch_page("pages/Cart_dashboard.py")
    
    else:
        st.error("❌ Payment failed.")
        st.toast("⚠️ Please try again.")
        st.text(f"Reason: {response.text}")
if st.button("Cancel Payment", use_container_width=True):
    with st.spinner("Returning to Cart....."):
        time.sleep(4)
    st.switch_page("pages/Cart_dashboard.py")
