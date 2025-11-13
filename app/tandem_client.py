import os
import requests
from fastapi import HTTPException
from dotenv import load_dotenv
load_dotenv()


AUTODESK_AUTH_URL = "https://developer.api.autodesk.com/authentication/v2/token"

CLIENT_ID = os.getenv("AUTODESK_CLIENT_ID")
CLIENT_SECRET = os.getenv("AUTODESK_CLIENT_SECRETT")


def get_2legged_token():
    """
    Obtiene un token 2-legged (client_credentials) de Autodesk APS.
    Este token se usa para operaciones de servidor a servidor.
    """
    if not CLIENT_ID or not CLIENT_SECRET:
        raise HTTPException(status_code=500, detail="CLIENT_ID o CLIENT_SECRET no configurados en el entorno")

    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "client_credentials",
        "scope": "data:read data:write bucket:create bucket:read"
    }

    response = requests.post(AUTODESK_AUTH_URL, data=data)

    if response.status_code != 200:
        raise HTTPException(status_code=400, detail=f"Error al obtener token APS: {response.text}")

    return response.json().get("access_token")

def create_tandem_project(name: str, description: str = ""):
    """
    Crea un proyecto en Autodesk Tandem usando el token APS.
    """
    token = get_2legged_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    url = "https://developer.api.autodesk.com/tandem/v1/projects"
    payload = {
        "name": name,
        "description": description
    }

    r = httpx.post(url, json=payload, headers=headers, timeout=10.0)
    r.raise_for_status()
    return r.json()