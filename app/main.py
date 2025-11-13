from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app import database, models
from app.routes import sync

# ==============================================
# 🔧 Inicialización de la aplicación
# ==============================================
app = FastAPI(
    title="Revit ↔ SQL Sync API",
    description="Sincroniza proyectos, usuarios y elementos desde Revit hacia SQL Server.",
    version="2.0.0"
)

# ==============================================
# 🌐 Configuración CORS (para pruebas locales)
# ==============================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # puedes limitar a ['http://localhost:5000']
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==============================================
# 🧩 Crear tablas automáticamente si no existen
# ==============================================
models.Base.metadata.create_all(bind=database.engine)

# ==============================================
# 📦 Registrar rutas
# ==============================================
app.include_router(sync.router)

# ==============================================
# 🩵 Endpoint raíz de prueba
# ==============================================
@app.get("/")
def root():
    return {"status": "API corriendo correctamente", "version": "2.0.0"}
