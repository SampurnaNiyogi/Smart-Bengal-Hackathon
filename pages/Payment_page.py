import streamlit as st
import os
import time
import requests
import firebase_admin
from firebase_admin import credentials, firestore

from dotenv import load_dotenv

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime

import smtplib
from email.message import EmailMessage

from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# Load environment variables from .env
load_dotenv()
service_account_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

if not service_account_path:
    raise ValueError("GOOGLE_APPLICATION_CREDENTIALS is not set in the .env file")

# Initialize Firebase only if not already initialized
if not firebase_admin._apps:
    cred = credentials.Certificate(service_account_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()

BASE_URL = "http://127.0.0.1:5000"

st.title("💳 Payment Gateway")

if "user_name" not in st.session_state or "checkout_payload" not in st.session_state:
    st.warning("You have not initiated a checkout.")
    st.stop()

user_id = st.session_state["user_name"]
# user_email = st.session_state["user_email"]

# For testing purposes, using a hardcoded email
# In a real-world scenario, you would fetch this from the user's profile
# or session

user_email = "debnathaditya007@gmail.com"
payload = st.session_state["checkout_payload"]

# Get reference to the Firestore document
doc_ref = db.collection('orders').document(user_id)

# Fetch the document
doc = doc_ref.get()

# Initialize variable to store data
history_data = {}

# Extract and store 'history' if the document exists
if doc.exists:
    data = doc.to_dict()
    history_data = data.get('history', {})  # Store just the 'history' part

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

checkout_payload = st.session_state["checkout_payload"]

st.markdown("### Choose Payment Method")
st.radio("Select one:", ["UPI", "Credit Card", "Net Banking", "Wallets"], horizontal=True)


def send_invoice_email(recipient_email, pdf_path, history_data, user_name):
    EMAIL_SENDER = "debnathaditya2005@gmail.com"
    EMAIL_PASSWORD = "wpngulalndxhywjg"

    msg = EmailMessage()
    msg['Subject'] = "🧾 Your Invoice from Demo Branch"
    msg['From'] = EMAIL_SENDER
    msg['To'] = recipient_email

    # Capitalize user name for display
    formatted_name = user_name.capitalize()

    html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6;">
            <h2 style="color: #4CAF50;">Thanks for your order, {formatted_name}! 🛍️</h2>
            <p>Hi {formatted_name},</p>
            <p>We appreciate your purchase at <strong>Demo Branch</strong>. Your invoice is attached to this email.</p>
            <h3>🧾 Order Summary:</h3>
            <table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse;">
                <tr style="background-color: #f2f2f2;">
                    <th>Date</th>
                    <th>Item</th>
                    <th>Quantity</th>
                    <th>Price</th>
                </tr>
    """

    for ts, record in history_data.items():
        for item, details in record['items'].items():
            html += f"""
                <tr>
                    <td>{record['timestamp']}</td>
                    <td>{item.title()}</td>
                    <td>{details['quantity']}</td>
                    <td>₹{details['price']}</td>
                </tr>
            """
        html += f"""
            <tr>
                <td colspan="3" align="right"><strong>Total:</strong></td>
                <td><strong>₹{record['total']}</strong></td>
            </tr>
        """

    html += """
            </table>
            <p>If you have any questions, feel free to reply to this email.</p>
            <br>
            <p>Warm regards,</p>
            <p><strong>Demo Branch Team</strong></p>
        </body>
    </html>
    """

    msg.set_content(f"Hi {formatted_name},\n\nThanks for your order! Your invoice is attached.\n\nDemo Branch")
    msg.add_alternative(html, subtype='html')

    with open(pdf_path, 'rb') as f:
        msg.add_attachment(f.read(), maintype='application', subtype='pdf', filename="invoice.pdf")

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
        smtp.send_message(msg)


def generate_invoice(history_data, output_path="invoice.pdf"):
    doc = SimpleDocTemplate(output_path, pagesize=A4,
                            rightMargin=30, leftMargin=30,
                            topMargin=30, bottomMargin=18)

    styles = getSampleStyleSheet()
    story = []

    # Title
    story.append(Paragraph("<b>🧾 DEMO BRANCH INVOICE</b>", styles["Title"]))
    story.append(Spacer(1, 12))

    # Customer section
    story.append(Paragraph(f"<b>Customer:</b> {user_id}", styles["Normal"]))
    story.append(Paragraph(f"<b>Email:</b> {user_email}", styles["Normal"]))
    story.append(Spacer(1, 12))

    for idx, (timestamp, record) in enumerate(history_data.items(), start=1):
        story.append(Paragraph(f"<b>🗓️ Transaction {idx}:</b> {timestamp}", styles["Heading4"]))
        story.append(Spacer(1, 6))

        data = [["Item", "Quantity", "Price"]]
        for item_name, details in record['items'].items():
            row = [item_name.title(), str(details["quantity"]), f"₹{details['price']}"]
            data.append(row)

        table = Table(data, colWidths=[100, 100, 100])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2E5077")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        story.append(table)
        story.append(Spacer(1, 12))

        story.append(Paragraph(f"<b>Total:</b> ₹{record['total']}", styles["Normal"]))
        story.append(Spacer(1, 24))

    # Footer
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    story.append(Paragraph(f"<i>Generated on {now}</i>", styles["Normal"]))
    story.append(Paragraph("<b>Thank you for shopping with us!</b>", styles["Normal"]))

    doc.build(story)


if st.button("💸 Pay Now", use_container_width=True):
    with st.spinner("Processing Payment..."):
        time.sleep(3)

        response = requests.post(f"{BASE_URL}/{user_id}/final_checkout", json=checkout_payload)

    if response.status_code == 200:
        generate_invoice(history_data, output_path="invoice.pdf")
        send_invoice_email(user_email, "invoice.pdf", history_data, user_id)

        st.toast(f"📧 Invoice sent to {user_email}", icon="✅")

        with open("invoice.pdf", "rb") as f:
            st.download_button(
                label="⬇️ Download Your Invoice",
                data=f,
                file_name="invoice.pdf",
                mime="application/pdf"
            )

        st.success("🎉 Payment successful! Your order has been placed.")
        st.toast("🛍️ You can now view your order history.", icon="📦")
        time.sleep(10)
        st.switch_page("pages/Customer_dashboard.py")
    else:
        st.error("❌ Payment failed.")
        st.toast("⚠️ Please try again.")
        st.text(f"Reason: {response.text}")
if st.button("Cancel Payment", use_container_width=True):
    with st.spinner("Returning to Cart....."):
        time.sleep(4)
    st.switch_page("pages/Cart_dashboard.py")
