from apscheduler.schedulers.background import BackgroundScheduler
from . import database, tandem_client, crud
from sqlalchemy.orm import Session
import httpx
from dotenv import load_dotenv
import os

# ✅ Cargar variables de entorno para el scheduler también
load_dotenv()


def sync_tandem_task():
    """Sincroniza automáticamente proyectos desde Autodesk Tandem hacia SQL Server."""
    print("🔄 Ejecutando sincronización automática con Tandem...")

    token = tandem_client.get_2legged_token()
    headers = {"Authorization": f"Bearer {token}"}
    url = "https://api.tandem.autodesk.com/data/v1/projects"

    session: Session = next(databases.get_db())

    try:
        r = httpx.get(url, headers=headers, timeout=15.0)
        r.raise_for_status()
        data = r.json()

        for p in data.get("results", []):
            nombre = p.get("name")
            descripcion = p.get("description", "")
            tandem_id = p.get("id")

            # Si el proyecto no existe, créalo
            proyecto = session.query(crud.models.Proyecto).filter_by(nombre=nombre).first()
            if not proyecto:
                nuevo = crud.models.Proyecto(
                    nombre=nombre,
                    descripcion=descripcion,
                    tandem_id=tandem_id,
                    fuente="tandem"
                )
                session.add(nuevo)
                session.commit()
                session.refresh(nuevo)
                print(f"✅ Proyecto creado: {nombre}")
            else:
                print(f"➡ Proyecto ya existente: {nombre}")

    except Exception as e:
        print(f"⚠ Error al sincronizar Tandem: {e}")
    finally:
        session.close()


def start_scheduler():
    """Inicia el scheduler en segundo plano."""
    scheduler = BackgroundScheduler()
    scheduler.add_job(sync_tandem_task, "interval", minutes=10)  # ⏱ cada 10 minutos
    scheduler.start()
    print("🕒 Scheduler automático iniciado (cada 10 minutos).")
