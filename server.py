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


#Get Product
@app.get('/<provider>/<branch>/<product_name>/get_product')
def get_product(provider, branch, product_name):
    doc_ref = db.collection("provider").document(provider)
    doc = doc_ref.get()

    if not doc.exists:
        return jsonify({"error": "Retailer not found"}), 404

    data = doc.to_dict()
    try:
        product_data = data[branch][product_name]    #{'product_name' : {quantity: int , price: float}}
        return jsonify(product_data)
    except KeyError:
        return jsonify({"error": "Product not found"}), 404


#Add to cart
@app.post('/<retail>/<branch>/<user_id>/add_to_cart')
def add_to_cart(user_id,retail,branch):
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
    current_product[branch][product_name]['quantity'] -=  data.get("quantity", 1)
    product_ref.update({f"{branch}.{product_name}.quantity": current_stock - data.get("quantity")})
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
    
        return jsonify({"message": "Checkout successful!"})

#After checkout with payment
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
    cart_ref.set({})

    return jsonify({"message": "Ordered successful!y", "order": order_data})


if __name__ == '__main__':
    app.run(debug=True, port=5000)
