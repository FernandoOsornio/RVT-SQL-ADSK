from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


# =========================
#  SCHEMA: USUARIO
# =========================
class UsuarioBase(BaseModel):
    nombre: str
    correo: str


class UsuarioCreate(UsuarioBase):
    pass


class UsuarioResponse(UsuarioBase):
    id: int
    fecha_registro: Optional[datetime]

    class Config:
        orm_mode = True


# =========================
#  SCHEMA: ELEMENTO
# =========================
class ElementoBase(BaseModel):
    nombre: str
    omniclass: Optional[str] = None
    parametros: Optional[str] = None
    usuario: Optional[str] = None
    fecha_modificacion: Optional[datetime] = None


class ElementoCreate(ElementoBase):
    pass


class ElementoResponse(ElementoBase):
    id: int

    class Config:
        orm_mode = True


# =========================
#  SCHEMA: TIPO_FAMILIA
# =========================
class TipoFamiliaBase(BaseModel):
    nombre: str
    omniclass: Optional[str] = None
    parametros: Optional[str] = None


class TipoFamiliaCreate(TipoFamiliaBase):
    elementos: List[ElementoCreate] = []


class TipoFamiliaResponse(TipoFamiliaBase):
    id: int
    elementos: List[ElementoResponse] = []

    class Config:
        orm_mode = True


# =========================
#  SCHEMA: FAMILIA
# =========================
class FamiliaBase(BaseModel):
    nombre: str
    omniclass: Optional[str] = None
    parametros: Optional[str] = None


class FamiliaCreate(FamiliaBase):
    tipos_familia: List[TipoFamiliaCreate] = []


class FamiliaResponse(FamiliaBase):
    id: int
    tipos_familia: List[TipoFamiliaResponse] = []

    class Config:
        orm_mode = True


# =========================
#  SCHEMA: CATEGORIA
# =========================
class CategoriaBase(BaseModel):
    nombre: str
    omniclass: Optional[str] = None
    usuario: Optional[str] = None


class CategoriaCreate(CategoriaBase):
    familias: List[FamiliaCreate] = []


class CategoriaResponse(CategoriaBase):
    id: int
    familias: List[FamiliaResponse] = []

    class Config:
        orm_mode = True


# =========================
#  SCHEMA: PROYECTO_USUARIO
# =========================
class ProyectoUsuarioBase(BaseModel):
    horas: Optional[float] = 0.0
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None


class ProyectoUsuarioCreate(ProyectoUsuarioBase):
    usuario_id: int


class ProyectoUsuarioResponse(ProyectoUsuarioBase):
    id: int
    usuario: UsuarioResponse

    class Config:
        orm_mode = True


# =========================
#  SCHEMA: PROYECTO
# =========================
class ProyectoBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    horas: Optional[float] = 0.0
    fuente: Optional[str] = None
    tandem_id: Optional[str] = None
    uuid: Optional[str] = None


class ProyectoCreate(ProyectoBase):
    usuario_id: Optional[int] = None
    categorias: List[CategoriaCreate] = []
    usuarios_proyecto: Optional[List[ProyectoUsuarioCreate]] = []


class ProyectoResponse(ProyectoBase):
    id: int
    fecha_creacion: datetime
    usuario_relacion: Optional[UsuarioResponse]
    categorias: List[CategoriaResponse] = []
    usuarios_proyecto: List[ProyectoUsuarioResponse] = []

    class Config:
        orm_mode = True


# =========================
#  SCHEMA: SYNC REVIT
# =========================
class ProyectoSync(BaseModel):
    nombre: str
    horas: float
    usuario: UsuarioBase
    categorias: List[CategoriaCreate]

    class Config:
        orm_mode = True

class RevitElementoSync(BaseModel):
    tipo: str
    id_sql: int
    revit_id: int

class RevitDeleteSync(BaseModel):
    revit_id: int
    tipo: str