from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from app import models, schemas


# ======================================================
# 🔹 Obtener o crear usuario
# ======================================================
def obtener_o_crear_usuario(db: Session, usuario_data: schemas.UsuarioBase):
    usuario = db.query(models.Usuario).filter(models.Usuario.correo == usuario_data.correo).first()
    if not usuario:
        usuario = models.Usuario(
            nombre=usuario_data.nombre,
            correo=usuario_data.correo,
            fecha_registro=datetime.now()
        )
        db.add(usuario)
        db.commit()
        db.refresh(usuario)
    return usuario


# ======================================================
# 🔹 Obtener o crear proyecto
# ======================================================
def obtener_o_crear_proyecto(db: Session, nombre_proyecto: str, usuario_id: int, horas: float = 0.0):
    proyecto = db.query(models.Proyecto).filter(models.Proyecto.nombre == nombre_proyecto).first()
    if not proyecto:
        proyecto = models.Proyecto(
            nombre=nombre_proyecto,
            usuario_id=usuario_id,
            horas=horas,
            fecha_creacion=datetime.now()
        )
        db.add(proyecto)
        db.commit()
        db.refresh(proyecto)
    else:
        # Si ya existe, actualizamos horas
        proyecto.horas = horas
        db.commit()
    return proyecto


# ======================================================
# 🔹 Registrar relación proyecto-usuario (tiempo trabajado)
# ======================================================
def registrar_participacion_usuario(db: Session, proyecto_id: int, usuario_id: int, horas: float):
    participacion = (
        db.query(models.ProyectoUsuario)
        .filter(
            models.ProyectoUsuario.proyecto_id == proyecto_id,
            models.ProyectoUsuario.usuario_id == usuario_id
        )
        .first()
    )

    if not participacion:
        participacion = models.ProyectoUsuario(
            proyecto_id=proyecto_id,
            usuario_id=usuario_id,
            horas=horas,
            fecha_inicio=datetime.now(),
            fecha_fin=datetime.now()
        )
        db.add(participacion)
    else:
        participacion.horas += horas
        participacion.fecha_fin = datetime.now()

    db.commit()
    db.refresh(participacion)
    return participacion


# ======================================================
# 🔹 Crear jerarquía completa desde Revit
# ======================================================
def sincronizar_desde_revit(db: Session, proyecto_sync: schemas.ProyectoSync):
    try:

        # 1️⃣ Usuario principal
        usuario = obtener_o_crear_usuario(db, proyecto_sync.usuario)

        # 2️⃣ Proyecto
        proyecto = obtener_o_crear_proyecto(
            db, proyecto_sync.nombre, usuario.id, proyecto_sync.horas
        )

        # 3️⃣ Registrar participación
        registrar_participacion_usuario(db, proyecto.id, usuario.id, proyecto_sync.horas)

        # 4️⃣ Limpiar categorías anteriores (opcional)
        db.query(models.Categoria).filter(models.Categoria.proyecto_id == proyecto.id).delete()
        db.commit()

        # 5️⃣ Crear jerarquía completa
        for cat_data in proyecto_sync.categorias:
            categoria = models.Categoria(
                nombre=cat_data.nombre,
                omniclass=cat_data.omniclass,
                usuario=usuario.nombre,
                proyecto_id=proyecto.id
            )
            db.add(categoria)
            db.commit()
            db.refresh(categoria)

            for fam_data in cat_data.familias:
                familia = models.Familia(
                    nombre=fam_data.nombre,
                    omniclass=fam_data.omniclass,
                    parametros=fam_data.parametros,
                    categoria_id=categoria.id
                )
                db.add(familia)
                db.commit()
                db.refresh(familia)

                for tipo_data in fam_data.tipos_familia:
                    tipo = models.TipoFamilia(
                        nombre=tipo_data.nombre,
                        omniclass=tipo_data.omniclass,
                        parametros=tipo_data.parametros,
                        familia_id=familia.id
                    )
                    db.add(tipo)
                    db.commit()
                    db.refresh(tipo)

                    for elem_data in tipo_data.elementos:
                        elemento = models.Elemento(
                            nombre=elem_data.nombre,
                            omniclass=elem_data.omniclass,
                            parametros=elem_data.parametros,
                            usuario=usuario.nombre,
                            fecha_modificacion=datetime.now(),
                            tipo_familia_id=tipo.id
                        )
                        db.add(elemento)
                        db.commit()

        return {
            "proyecto": proyecto.nombre,
            "usuario": usuario.nombre,
            "categorias_insertadas": len(proyecto_sync.categorias),
            "fecha_sync": datetime.now().isoformat()
        }

    except SQLAlchemyError as e:
        db.rollback()
        raise Exception(f"Error en sincronización SQL: {str(e)}")

    except Exception as e:
        db.rollback()
        raise Exception(f"Error general: {str(e)}")



# ====================================================
# 🔄 Sincronización SQL → Revit
# ====================================================

def obtener_todos_los_proyectos(db: Session):
    proyectos = db.query(models.Proyecto).all()
    resultado = []

    for p in proyectos:
        proyecto_dict = {
            "id": p.id,
            "nombre": p.nombre,
            "fecha_creacion": p.fecha_creacion.isoformat() if p.fecha_creacion else None,
            "horas": p.horas,
            "usuario": {
                "id": p.usuario.id if p.usuario else None,
                "nombre": p.usuario.nombre if p.usuario else None,
                "correo": p.usuario.correo if p.usuario else None,
            } if p.usuario else None,
            "categorias": [],
        }

        # Categorías
        for c in p.categorias:
            cat_dict = {
                "id": c.id,
                "nombre": c.nombre,
                "omniclass": c.omniclass,
                "familias": [],
            }

            # Familias
            for f in c.familias:
                fam_dict = {
                    "id": f.id,
                    "nombre": f.nombre,
                    "omniclass": f.omniclass,
                    "tipos_familia": [],
                }

                # Tipos de familia
                for t in f.tipos_familia:
                    tipo_dict = {
                        "id": t.id,
                        "nombre": t.nombre,
                        "omniclass": t.omniclass,
                        "elementos": [],
                    }

                    # Elementos
                    for e in t.elementos:
                        tipo_dict["elementos"].append({
                            "id": e.id,
                            "nombre": e.nombre,
                            "omniclass": e.omniclass,
                        })

                    fam_dict["tipos_familia"].append(tipo_dict)

                cat_dict["familias"].append(fam_dict)

            proyecto_dict["categorias"].append(cat_dict)

        resultado.append(proyecto_dict)

    return resultado


def actualizar_revit_id(db: Session, item):
    tabla = None
    if item.tipo == "familia":
        tabla = models.Familia
    elif item.tipo == "tipo":
        tabla = models.TipoFamilia
    elif item.tipo == "elemento":
        tabla = models.Elemento
    else:
        raise Exception(f"Tipo no reconocido: {item.tipo}")

    registro = db.query(tabla).filter(tabla.id == item.id_sql).first()
    if registro:
        registro.revit_id = item.revit_id
        db.commit()

def eliminar_por_revit_id(db: Session, tipo: str, revit_id: int):
    tabla = None
    if tipo == "familia":
        tabla = models.Familia
    elif tipo == "tipo":
        tabla = models.TipoFamilia
    elif tipo == "elemento":
        tabla = models.Elemento
    else:
        raise Exception(f"Tipo no reconocido: {tipo}")

    registro = db.query(tabla).filter(tabla.revit_id == revit_id).first()
    if registro:
        db.delete(registro)
        db.commit()

        registrar_auditoria(
            db=db,
            usuario=usuario or "Desconocido",
            proyecto=proyecto or "Sin proyecto",
            entidad=tipo.capitalize(),
            revit_id=revit_id,
            accion="ELIMINAR",
            detalle={"nombre": getattr(registro, "nombre", None)}
        )
    else:
        print(f"⚠️ No se encontró {tipo} con RevitID {revit_id}")

def registrar_auditoria(db, usuario, proyecto, entidad, revit_id, accion, detalle=None):
    registro = models.AuditoriaSync(
        usuario=usuario,
        proyecto=proyecto,
        entidad=entidad,
        revit_id=revit_id,
        accion=accion,
        detalle=json.dumps(detalle or {}, ensure_ascii=False)
    )
    db.add(registro)
    db.commit()