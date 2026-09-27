import json
import os

import firebase_admin
from firebase_admin import credentials, firestore


firebase_service_account = os.getenv("FIREBASE_SERVICE_ACCOUNT")

if firebase_service_account:
    credential_data = json.loads(firebase_service_account)
    cred = credentials.Certificate(credential_data)
else:
    cred = credentials.Certificate("firebase-service-account.json")

firebase_admin.initialize_app(cred)

db = firestore.client()