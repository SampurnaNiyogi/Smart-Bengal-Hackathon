import firebase_admin
from firebase_admin import credentials, firestore

# Backend API URL
BASE_URL = "http://127.0.0.1:5000"


# Load Firebase credentials (Use a service account JSON file)
if not firebase_admin._apps:
    cred = credentials.Certificate("sbh25-2d8ba-firebase-adminsdk-fbsvc-d4cce1ee41.json")  # Update with your file path
    firebase_admin.initialize_app(cred)

# Initialize Firestore
db = firestore.client()

