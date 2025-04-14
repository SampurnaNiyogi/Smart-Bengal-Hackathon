from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, firestore
import re

from dotenv import load_dotenv
import os

from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime

import smtplib
from email.message import EmailMessage

from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import uuid
import random
# Load environment variables from .env
load_dotenv()

# Get the JSON key path
service_account_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

if not service_account_path:
    raise ValueError("GOOGLE_APPLICATION_CREDENTIALS is not set in the .env file")

# Initialize Firebase only if not already initialized
if not firebase_admin._apps:
    cred = credentials.Certificate(service_account_path)  # Ensure correct path
    firebase_admin.initialize_app(cred)

db = firestore.client()

app = Flask(__name__)

#test Flask
@app.route('/')
def home():
    return "Hello from Flask backend!"

# Firestore connection
@app.get('/test_firestore')
def test_firestore():
    try:
        providers_ref = db.collection('provider')
        docs = providers_ref.limit(1).stream()  # Fetch only 1 document

        provider_list = [doc.id for doc in docs]
        return jsonify(provider_list if provider_list else ["No Data"])
    except Exception as e:
        return jsonify({"error": str(e)})

def validate_name_email(name: str, email: str) -> str:
    # Validation logic for name and email
    if not name and not email:
        return "Both name and email fields are empty"
    elif not name:
        return "Name field is empty"
    elif not email:
        return "Email field is empty"
    
    # Email regex validation
    email_regex = re.compile(r"^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$")
    if not email_regex.match(email):
        return "Email address is not valid"
    
    return None  # No errors found


@app.post("/add_user")
def add_user():
    try:
        data = request.get_json()
        name = data.get("name", "").strip()
        email = data.get("email", "").strip()

        # Validation
        validation_error = validate_name_email(name, email)
        if validation_error:
            return jsonify({"success": False, "error": validation_error}), 400

        # Firestore user creation
        fingerprint_id = str(uuid.uuid4())[:8]
        user_ref = db.collection("users").document(email)  # Use email as unique key
        user_ref.set({
            "name": name,
            "email": email,
            "fingerprint_id": fingerprint_id
        })

        return jsonify({"success": True, "fingerprint_id": fingerprint_id}), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/login_user', methods=['POST'])
def login_user():
    data = request.get_json()  # Get data from request

    # Extract name and email
    name = data.get('name')
    email = data.get('email')

    # Validate inputs
    validation_error = validate_name_email(name, email)
    if validation_error:
        return jsonify({"success": False, "error": validation_error}), 400

    # Check if user exists in Firestore
    user_ref = db.collection('users').where('name', '==', name).where('email', '==', email).get()
    
    if user_ref:
        # User found
        return jsonify({"success": True}), 200
    else:
        # User not found
        return jsonify({"success": False, "error": "User not found"}), 404
    
@app.get('/fingerprint_auth')
def fingerprint_auth():
    try:
        # Fetch all users with fingerprint IDs
        users = db.collection("users").get()
                 
        fingerprint_users = [user.to_dict() for user in users if "fingerprint_id" in user.to_dict()]

        if not fingerprint_users:
            return jsonify({"error": "No fingerprint-enabled users found."}), 404
        # Pick one user randomly for now (simulate fingerprint match)
        matched_user = random.choice(fingerprint_users)
        
        details = {"user_name":  matched_user["name"], "user_email" : matched_user["email"],"fingerprint_id" : matched_user["fingerprint_id"]}
        return jsonify(details), 200
    
    except Exception as e:
        return jsonify({"error": "Internal Server Error...."}), 500
    

# Get Retailers Option
@app.get('/get_providers')
def get_providers():
    providers_ref = db.collection('provider')
    docs = providers_ref.stream()
    provider_list = [doc.id for doc in docs]  # Get document IDs (Provider Names)
    return jsonify(provider_list)


# Get branch Option
@app.get('/<provider>/get_branch')
def get_branches(provider):
    doc = db.collection("provider").document(provider).get()
    if not doc.exists:
        return jsonify({"error": "Retailer not found"}), 404

    data = doc.to_dict()
    branch_names = list(data.keys())  # Top-level fields like 'Ruby', 'Salt Lake'
    return jsonify(branch_names)


# Get Product
@app.get('/<provider>/<branch>/<product_name>/get_product')
def get_product(provider, branch, product_name):
    doc_ref = db.collection("provider").document(provider)
    doc = doc_ref.get()

    if not doc.exists:
        return jsonify({"error": "Retailer not found"}), 404

    data = doc.to_dict()
    try:
        product_data = data[branch][product_name]  # {'product_name' : {quantity: int , price: float}}
        return jsonify(product_data)  # {quantity: int , price: float}
    except KeyError:
        return jsonify({"error": "Product not found"}), 404


# Add to cart
@app.post('/<retail>/<branch>/<user_id>/add_to_cart')
def add_to_cart(user_id, retail, branch):
    data = request.json  # Expected: {"product_name": "apple", "quantity": 2, ...}

    product_ref = db.collection("provider").document(retail)
    current_product = product_ref.get().to_dict() or {}

    cart_ref = db.collection("carts").document(user_id)
    current_cart = cart_ref.get().to_dict() or {}

    # Add or update product in the cart
    product_name = data.get("product_name")

    try:
        current_stock = current_product[branch][product_name]['quantity']
        product_price = current_product[branch][product_name]['price']
    except KeyError:
        return jsonify({"error": "Product not found"}), 404

    if current_stock < data['quantity']:
        return jsonify({"error": "Not enough stock available"}), 404

    if not product_name:
        return jsonify({"error": "Product name is required"}), 400

    # Update product entry
    if product_name in current_cart:
        current_cart[product_name]['quantity'] += data.get("quantity", 1)
    else:
        current_cart[product_name] = {
            "quantity": data.get("quantity", 1),
            "price": product_price

        }
    current_product[branch][product_name]['quantity'] -= data.get("quantity", 1)
    product_ref.update({f"{branch}.{product_name}.quantity": current_stock - data.get("quantity")})
    cart_ref.set(current_cart)
    return jsonify({"message": f"{product_name} added to cart"})


# View Cart Details
@app.get('/<user_id>/get_cart')
def get_cart(user_id):
    cart_ref = db.collection("carts").document(user_id)
    doc = cart_ref.get()

    if doc.exists:
        return jsonify(doc.to_dict())
    else:
        return jsonify({})  # Empty cart


@app.post('/<user_id>/update_cart_item')
def update_cart_item(user_id):
    data = request.json  # expects: { "product_name": "bread", "quantity": 3 }

    product = data.get("product_name")
    new_qty = data.get("quantity")

    if not product or new_qty is None:
        return jsonify({"error": "Missing product or quantity"}), 400

    cart_ref = db.collection("carts").document(user_id)
    cart = cart_ref.get().to_dict() or {}

    if product not in cart:
        return jsonify({"error": "Item not in cart"}), 404

    if new_qty <= 0:
        del cart[product]  # remove item
    else:
        cart[product]["quantity"] = new_qty

    cart_ref.set(cart)
    return jsonify({"message": "Cart updated"})


@app.post('/<user_id>/checkout')
def checkout(user_id):
    data = request.json

    provider = data.get("provider", "")
    branch = data.get("branch", "")
    if not provider or not branch:
        return jsonify({"error": "Missing provider or branch"}), 400

    # Fetch cart
    cart_ref = db.collection("carts").document(user_id)
    cart = cart_ref.get().to_dict()

    if not cart:
        return jsonify({"error": "Cart is empty"}), 400

    # Fetch provider data
    provider_ref = db.collection("provider").document(provider)
    provider_doc = provider_ref.get()
    if not provider_doc.exists:
        return jsonify({"error": "Provider not found"}), 404

    provider_data = provider_doc.to_dict()

    if branch not in provider_data:
        return jsonify({"error": "Branch not found"}), 404

    # Validate stock
    for product, item in cart.items():
        stock = provider_data[branch].get(product, {}).get("quantity", 0)
        if item["quantity"] > stock:
            return jsonify({
                "error": f"Only {stock} '{product}' available in stock."
            }), 400

        return jsonify({"message": "Checkout successful!"})


# After checkout with payment
@app.post('/<user_id>/final_checkout')
def final_checkout(user_id):
    data = request.json
    provider = data.get("provider", "")
    branch = data.get("branch", "")

    if not provider or not branch:
        return jsonify({"error": "Missing provider or branch"}), 400

    # Fetch cart
    cart_ref = db.collection("carts").document(user_id)
    cart = cart_ref.get().to_dict()

    if not cart:
        return jsonify({"error": "Cart is empty"}), 400

    # Finalize order (assumes stock already adjusted earlier)
    total = sum(item["price"] * item["quantity"] for item in cart.values())
    timeStamp = datetime.utcnow()
    order_data = {
        "items": cart,
        "total": total,
        "timestamp": timeStamp
    }

    # Save to order history
    order_ref = db.collection("orders").document(user_id)
    curr_order = order_ref.get().to_dict() or {}
    if 'history' not in curr_order:
        curr_order['history'] = {}
    curr_order['history'][str(timeStamp)] = order_data

    # Write and clear
    order_ref.set(curr_order)
    cart_ref.delete()

    return jsonify({"message": "Ordered successful!y", "order": order_data})


@app.post('/<user_id>/send_invoice_email')
def send_invoice_email(user_id):
    # Fethched from user_email 

    # For testing purposes, using a hardcoded email
    # In a real-world scenario, you would fetch this from the user's profile
    # or session
    user_email = "debnathaditya007@gmail.com"
    pdf_path = "invoice.pdf"
    EMAIL_SENDER = "debnathaditya2005@gmail.com"
    EMAIL_PASSWORD = "wpngulalndxhywjg"
    doc_ref = db.collection('orders').document(user_id)   # Get reference to the Firestore document
    doc = doc_ref.get()  # Fetch the document
    if doc.exists:
        data = doc.to_dict()
        history_data = data.get('history', {})  # Store just the 'history' part
    msg = EmailMessage()
    msg['Subject'] = "🧾 Your Invoice from Demo Branch"
    msg['From'] = EMAIL_SENDER
    msg['To'] = user_email
    
    # Capitalize user name for display
    formatted_name = user_id.capitalize()
    
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
    return jsonify({"message": "Invoice Email sent successful!"})


@app.post('/<user_id>/generate_invoice')
def generate_invoice(user_id, output_path="invoice.pdf"):
    # Fethched from user_email 

    # For testing purposes, using a hardcoded email
    # In a real-world scenario, you would fetch this from the user's profile
    # or session
    user_email = "debnathaditya007@gmail.com"
    
    doc_ref = db.collection('orders').document(user_id)   # Get reference to the Firestore document
    doc = doc_ref.get()  # Fetch the document
    if doc.exists:
        data = doc.to_dict()
        history_data = data.get('history', {})  # Store just the 'history' part
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
    return jsonify("message")




if __name__ == '__main__':
    app.run(debug=True, port=5000)
