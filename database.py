from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

def get_db():
    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        raise ValueError("MONGO_URI environment variable not set.")

    client = MongoClient(
        mongo_uri,
        tls=True,
        tlsAllowInvalidCertificates=True
    )
    try:
        db = client["api-20v"]
        yield db
    finally:
        client.close()
