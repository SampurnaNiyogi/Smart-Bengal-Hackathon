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

try:
    print("Initializing Firebase...")

    # Check if Firebase is already initialized
    if not firebase_admin._apps:
        cred = credentials.Certificate(service_account_path)
        firebase_admin.initialize_app(cred)

    db = firestore.client()
    print("Firebase initialized successfully!")

    # Test Firestore read
    providers_ref = db.collection("provider")
    docs = providers_ref.limit(1).stream()

    provider_list = [doc.id for doc in docs]
    print("Providers found:", provider_list if provider_list else "No providers found.")

except Exception as e:
    print("Firestore Error:", e)
