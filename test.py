from firebase_admin import firestore
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


provider = "Spencer"
branch = "Salt Lake"
product_name = "Bread"

doc_ref = db.collection("provider").document(provider).collection(branch).document(product_name)
doc = doc_ref.get()

if doc.exists:
    print("Product Found:", doc.to_dict())
else:
    print("No product found")
