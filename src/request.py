import requests
import pandas as pd
from azure.storage.blob import BlobServiceClient
import io
from dotenv import load_dotenv
import os

# --- Charger la variable d'environnement ---
load_dotenv()
connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
if not connection_string:
    raise ValueError("❌ La variable d'environnement AZURE_STORAGE_CONNECTION_STRING n'est pas définie !")

# --- 1. Requête API SBB ---
base_url = "https://data.sbb.ch/api/records/1.0/search/"
params = {
    "dataset": "ist-daten-sbb",
    "rows": 100,
    "sort": "betriebstag",
    "facet": "betriebstag,betreiber_name",
    "produkt_id": "Zug"
}

try:
    response = requests.get(base_url, params=params)
    response.raise_for_status()
except requests.exceptions.RequestException as e:
    print("❌ Erreur lors de la requête API :", e)
    exit()

data = response.json()
records = [record["fields"] for record in data["records"]]

# --- 2. Création du DataFrame ---
df = pd.DataFrame(records)

# Conversion des champs horaires en datetime
df['abfahrtszeit'] = pd.to_datetime(df['abfahrtszeit'])
df['ankunftszeit'] = pd.to_datetime(df['ankunftszeit'])

# Sélection et renommage des colonnes
df_train = df[['betriebstag', 'abfahrtszeit', 'ankunftszeit', 'produkt_id', 'linien_text', 
               'haltestellen_name', 'an_prognose_status', 'abfahrtsverspatung', 'ankunftsverspatung']]

df_train.rename(columns={
    'betriebstag': 'Jour de départ',
    'abfahrtszeit': 'Heure de départ',
    'ankunftszeit': 'Heure d’arrivée',
    'produkt_id': 'ID produit',
    'linien_text': 'Ligne',
    'haltestellen_name': 'Nom des haltes',
    'an_prognose_status': 'Statut départ prévu',
    'abfahrtsverspatung': 'Retard au départ',
    'ankunftsverspatung': 'Retard à l\'arrivée'
}, inplace=True)

# Supprimer les lignes sans heure d'arrivée
df_train = df_train.dropna(subset=['Heure d’arrivée'])

# Filtrer sur la ligne IR75
df_train = df_train[df_train['Ligne'] == "IR75"].reset_index(drop=True)

print("✅ DataFrame filtré :")
print(df_train.head())

# --- 3. Connexion Azure Blob Storage ---
try:
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    # Test connexion : lister les containers
    containers = [c['name'] for c in blob_service_client.list_containers()]
    print("✅ Connexion Azure OK, containers existants :", containers)
except Exception as e:
    print("❌ Problème de connexion :", e)
    exit()

# --- 4. Upload dans Azure Blob Storage ---
container_name = "sbb-data"  # <-- nom exact du container
blob_name = "df_train.csv"   # <-- nom du fichier à créer dans Azure

try:
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

    # Convertir DataFrame en CSV en mémoire
    csv_buffer = io.StringIO()
    df_train.to_csv(csv_buffer, index=False)

    # Upload
    blob_client.upload_blob(csv_buffer.getvalue(), overwrite=True)
    print(f"✅ Fichier '{blob_name}' uploadé avec succès dans le container '{container_name}' !")
except Exception as e:
    print("❌ Erreur lors de l'upload dans Azure :", e)
