from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, firestore

from dotenv import load_dotenv
import os


from datetime import datetime


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

#Get Product
@app.get('/<provider>/<branch>/<product_name>/get_product')
def get_product(provider, branch, product_name):
    doc_ref = db.collection("provider").document(provider)
    doc = doc_ref.get()

    if not doc.exists:
        return jsonify({"error": "Retailer not found"}), 404

    data = doc.to_dict()
    try:
        product_data = data[branch][product_name]
        return jsonify(product_data)
    except KeyError:
        return jsonify({"error": "Product not found"}), 404


# Get branch Option
@app.get('/<provider>/get_branch')
def get_branches(provider):
    doc = db.collection("provider").document(provider).get()
    if not doc.exists:
        return jsonify({"error": "Retailer not found"}), 404

    data = doc.to_dict()
    branch_names = list(data.keys())  # Top-level fields like 'Ruby', 'Salt Lake'
    return jsonify(branch_names)


# Get Retailers Option
@app.get('/get_providers')
def get_providers():
    providers_ref = db.collection('provider')
    docs = providers_ref.stream()
    provider_list = [doc.id for doc in docs]  # Get document IDs (Provider Names)
    return jsonify(provider_list)


#Firestore connection
@app.get('/test_firestore')
def test_firestore():
    try:
        providers_ref = db.collection('provider')
        docs = providers_ref.limit(1).stream()  # Fetch only 1 document

        provider_list = [doc.id for doc in docs]
        return jsonify(provider_list if provider_list else ["No Data"])
    except Exception as e:
        return jsonify({"error": str(e)})


#Add to cart
@app.post('/<user_id>/add_to_cart')
def add_to_cart(user_id):
    data = request.json  # Expected: {"product_name": "apple", "quantity": 2, ...}
    
    cart_ref = db.collection("carts").document(user_id)
    current_cart = cart_ref.get().to_dict() or {}

    # Add or update product in the cart
    product_name = data.get("product_name")
    
    if not product_name:
        return jsonify({"error": "Product name is required"}), 400

    # Merge or initialize product entry
    if product_name in current_cart:
        current_cart[product_name]['quantity'] += data.get("quantity", 1)
    else:
        current_cart[product_name] = {
            "quantity": data.get("quantity", 1),
            "price": data.get("price", 0.0)
        }

    cart_ref.set(current_cart)
    return jsonify({"message": f"{product_name} added to cart"})


#View Cart Details
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

    # Deduct quantities
    for product, item in cart.items():
        provider_data[branch][product]["quantity"] -= item["quantity"]

    # Save updated stock
    provider_ref.set(provider_data)

    # Save order to history
    total = sum(item["price"] * item["quantity"] for item in cart.values())
    order_data = {
        "items": cart,
        "total": total,
        "timestamp": datetime.utcnow()
    }

    db.collection("orders").document(user_id).collection("history").add(order_data)

    # Clear the cart
    cart_ref.set({})

    return jsonify({"message": "Checkout successful!", "order": order_data})


if __name__ == '__main__':
    app.run(debug=True, port=5000)
