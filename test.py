import firebase_admin
from firebase_admin import credentials, firestore

try:
    print("Initializing Firebase...")

    # Check if Firebase is already initialized
    if not firebase_admin._apps:
        cred = credentials.Certificate("/Users/adityadebnath/Documents/sbh25-2d8ba-firebase-adminsdk-fbsvc-fc8ef9b782.json ")
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
