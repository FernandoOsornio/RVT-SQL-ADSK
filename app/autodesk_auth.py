import os
import requests
from dotenv import load_dotenv

load_dotenv()

APS_CLIENT_ID = os.getenv("APS_CLIENT_ID")
APS_CLIENT_SECRET = os.getenv("APS_CLIENT_SECRET")
APS_TOKEN_URL = os.getenv("APS_TOKEN_URL")
APS_SCOPES = os.getenv("APS_SCOPES")

def get_aps_token():
    """
    Solicita un token de acceso de Autodesk Platform Services (APS).
    """
    data = {
        "client_id": APS_CLIENT_ID,
        "client_secret": APS_CLIENT_SECRET,
        "grant_type": "client_credentials",
        "scope": APS_SCOPES
    }

    response = requests.post(APS_TOKEN_URL, data=data)

    if response.status_code != 200:
        raise Exception(f"Error al obtener token de Autodesk: {response.text}")

    return response.json()
