from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, firestore

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
    cred = credentials.Certificate(service_account_path)  # Ensure correct path
    firebase_admin.initialize_app(cred)

db = firestore.client()

app = Flask(__name__)


@app.route('/<provider>/<branch>/<product_name>/get_product', methods=['GET'])
def get_products(provider, branch, product_name):
    products_ref = db.collection("provider").document(provider).collection(branch).document(product_name)
    doc = products_ref.get()

    if doc.exists:
        return jsonify(doc.to_dict())  # ✅ Convert Firestore document to dictionary
    else:
        return jsonify({"error": "No products found"}), 404  # ✅ Ensure error is JSON
    
    
# Fetch product location from a specific branch
@app.route('/get_location/<provider>/<branch>', methods=['GET'])
def get_location(provider, branch):
    doc_ref = db.collection("provider").document(provider).collection(branch).document("location")
    doc = doc_ref.get()

    if doc.exists:
        return jsonify(doc.to_dict())
    else:
        return jsonify({"error": "Location data not found"}), 404

# Add a new product to a branch (Provider)
@app.route('/<provider>/<branch>/add_product', methods=['POST'])
def add_product(provider, branch):
    data = request.json
    db.collection("provider").document(provider).collection(branch).document().set(data)
    return jsonify({"message": "Product added successfully!"})

# Get Retailers Option
@app.route('/get_providers', methods=['GET'])
def get_providers():
    providers_ref = db.collection('provider')
    docs = providers_ref.stream()
    provider_list = [doc.id for doc in docs]  # Get document IDs (Provider Names)
    return jsonify(provider_list)

# Fetch all branches for a selected provider
@app.route('/<provider>/get_branch', methods=['GET'])
def get_branches(provider):
    try:
        # Reference to the provider document
        provider_doc = db.collection("provider").document(provider)
        
        # Get all subcollections (branches) under the selected provider
        branches = provider_doc.collections()
        
        # Extract collection names
        branch_list = [branch.id for branch in branches]  

        if not branch_list:
            return jsonify({"error": "No branches found"}), 404

        return jsonify(branch_list)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@app.route('/test_firestore', methods=['GET'])
def test_firestore():
    try:
        providers_ref = db.collection('provider')
        docs = providers_ref.limit(1).stream()  # Fetch only 1 document

        provider_list = [doc.id for doc in docs]
        return jsonify(provider_list if provider_list else ["No Data"])
    except Exception as e:
        return jsonify({"error": str(e)})
    

if __name__ == '__main__':
    app.run(debug=True, port=5000)
