from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, NVARCHAR
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


# =========================
#  TABLA: USUARIOS
# =========================
class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    correo = Column(String, unique=True, nullable=False)
    fecha_registro = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    proyectos = relationship("Proyecto", back_populates="usuario_relacion")
    proyectos_asignados = relationship("ProyectoUsuario", back_populates="usuario")


# =========================
#  TABLA: PROYECTOS
# =========================
class Proyecto(Base):
    __tablename__ = "proyectos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    descripcion = Column(String, nullable=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)  # 🔗 relación con usuarios
    horas = Column(Float, default=0.0)
    fuente = Column(String, nullable=True)
    tandem_id = Column(String, nullable=True)
    uuid = Column(String, nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    usuario_relacion = relationship("Usuario", back_populates="proyectos")
    categorias = relationship("Categoria", back_populates="proyecto", cascade="all, delete-orphan")
    usuarios_proyecto = relationship("ProyectoUsuario", back_populates="proyecto", cascade="all, delete-orphan")


# =========================
#  TABLA: CATEGORIAS
# =========================
class Categoria(Base):
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    omniclass = Column(String, nullable=True)
    usuario = Column(String, nullable=True)
    proyecto_id = Column(Integer, ForeignKey("proyectos.id"), nullable=False)

    # Relaciones
    proyecto = relationship("Proyecto", back_populates="categorias")
    familias = relationship("Familia", back_populates="categoria", cascade="all, delete-orphan")


# =========================
#  TABLA: FAMILIAS
# =========================
class Familia(Base):
    __tablename__ = "familias"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    omniclass = Column(String, nullable=True)
    parametros = Column(NVARCHAR, nullable=True)
    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=False)
    revit_id = Column(Integer, nullable=True)  # 👈 agregado
    # Relaciones
    categoria = relationship("Categoria", back_populates="familias")
    tipos_familia = relationship("TipoFamilia", back_populates="familia", cascade="all, delete-orphan")


# =========================
#  TABLA: TIPOS DE FAMILIA
# =========================
class TipoFamilia(Base):
    __tablename__ = "tipos_familia"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    omniclass = Column(String, nullable=True)
    parametros = Column(NVARCHAR, nullable=True)
    familia_id = Column(Integer, ForeignKey("familias.id"), nullable=False)
    revit_id = Column(Integer, nullable=True)  # 👈 agregado


    # Relaciones
    familia = relationship("Familia", back_populates="tipos_familia")
    elementos = relationship("Elemento", back_populates="tipo_familia", cascade="all, delete-orphan")


# =========================
#  TABLA: ELEMENTOS
# =========================
class Elemento(Base):
    __tablename__ = "elementos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    omniclass = Column(String, nullable=True)
    parametros = Column(NVARCHAR, nullable=True)
    usuario = Column(String, nullable=True)
    fecha_modificacion = Column(DateTime, default=datetime.utcnow)
    tipo_familia_id = Column(Integer, ForeignKey("tipos_familia.id"), nullable=False)
    revit_id = Column(Integer, nullable=True)  # 👈 agregado
    # Relaciones
    tipo_familia = relationship("TipoFamilia", back_populates="elementos")


# =========================
#  TABLA: PROYECTO_USUARIOS
# =========================
class ProyectoUsuario(Base):
    __tablename__ = "proyecto_usuarios"

    id = Column(Integer, primary_key=True, index=True)
    proyecto_id = Column(Integer, ForeignKey("proyectos.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    horas = Column(Float, default=0.0)
    fecha_inicio = Column(DateTime, default=datetime.utcnow)
    fecha_fin = Column(DateTime, nullable=True)

    # Relaciones
    proyecto = relationship("Proyecto", back_populates="usuarios_proyecto")
    usuario = relationship("Usuario", back_populates="proyectos_asignados")

class AuditoriaSync(Base):
    __tablename__ = "auditoria_sync"

    id = Column(Integer, primary_key=True, index=True)
    usuario = Column(String(255))
    proyecto = Column(String(255))
    entidad = Column(String(100))
    revit_id = Column(Integer, nullable=True)
    accion = Column(String(50))
    fecha_hora = Column(DateTime, server_default=func.now())
    detalle = Column(Text)
