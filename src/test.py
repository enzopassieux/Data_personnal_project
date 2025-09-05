from azure.storage.blob import BlobServiceClient
import os
from dotenv import load_dotenv

load_dotenv()
connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

try:
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    account_props = blob_service_client.get_service_properties()
    print("✅ Connexion Azure OK")
except Exception as e:
    print("❌ Problème de connexion :", e)
