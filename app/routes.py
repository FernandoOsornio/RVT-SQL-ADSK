from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app import crud, schemas, database
import traceback

router = APIRouter(tags=["Sincronización"], prefix="/sync")


# =========================
#  DEPENDENCIA DE DB
# =========================
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================
#  ENDPOINT PRINCIPAL
# =========================
@router.post("/revit/")
async def sync_desde_revit(request: Request, db: Session = Depends(get_db)):
    try:
        # Recibir JSON
        data = await request.json()
        print("📥 JSON recibido:", data)

        # Validar estructura Pydantic
        proyecto = schemas.ProyectoSync(**data)

        # Procesar sincronización
        resultado = crud.sincronizar_desde_revit(db, proyecto)

        print("✅ Sincronización completada:", resultado)
        return {"status": "ok", "detalle": resultado}

    except Exception as e:
        print(f"[ERROR] {e}")
        traceback.print_exc()
        raise HTTPException(status_code=422, detail=str(e))

# =========================================
# 🔄 SINCRONIZAR DESDE SQL → REVIT
# =========================================
@router.get("/sql/")
def sync_desde_sql(db: Session = Depends(get_db)):
    try:
        print("📤 Enviando datos de SQL Server a Revit...")

        proyectos = crud.obtener_todos_los_proyectos(db)
        print(f"✅ {len(proyectos)} proyectos obtenidos desde SQL")

        return {"status": "ok", "proyectos": proyectos}

    except Exception as e:
        print(f"[ERROR SQL→Revit] {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/revit/ids")
def actualizar_revit_ids(items: list[schemas.RevitElementoSync], db: Session = Depends(get_db)):
    try:
        for item in items:
            crud.actualizar_revit_id(db, item)
        return {"status": "ok", "mensaje": "IDs de Revit actualizados correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/revit/delete")
def eliminar_desde_revit(data: dict, db: Session = Depends(get_db)):
    try:
        revit_id = data.get("revit_id")
        tipo = data.get("tipo")

        if not revit_id or not tipo:
            raise HTTPException(status_code=400, detail="Faltan parámetros (revit_id, tipo)")

        crud.eliminar_por_revit_id(db, tipo, revit_id)

        return {"status": "ok", "mensaje": f"{tipo} con RevitID {revit_id} eliminado correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))