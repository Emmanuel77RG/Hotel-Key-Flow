"""
Script de siembra inicial de roles del sistema Hotel KeyFlow.
Inserta de forma idempotente los 3 roles operativos requeridos:
1: Administrador
2: Recepción
3: Limpieza
"""
import sys
import os

# Asegurar que el directorio raíz del proyecto esté en el PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import SessionLocal
from app.models.usuarios import Rol


ROLES_INICIALES = [
    {
        "id_rol": 1,
        "nombre_rol": "Administrador",
        "descripcion": "Acceso total: gestión de usuarios, auditoría, configuración y reportes ejecutivos.",
    },
    {
        "id_rol": 2,
        "nombre_rol": "Recepción",
        "descripcion": "Operación de front-desk: huéspedes, reservas, check-in, check-out, folios y POS.",
    },
    {
        "id_rol": 3,
        "nombre_rol": "Limpieza",
        "descripcion": "Operación de camarería: actualización de estados de limpieza y reporte de tickets.",
    },
]


def sembrar_roles():
    db = SessionLocal()
    try:
        print("[*] Iniciando siembra de roles...")
        for data_rol in ROLES_INICIALES:
            rol_existente = db.query(Rol).filter(Rol.id_rol == data_rol["id_rol"]).first()
            if not rol_existente:
                nuevo_rol = Rol(
                    id_rol=data_rol["id_rol"],
                    nombre_rol=data_rol["nombre_rol"],
                    descripcion=data_rol["descripcion"],
                )
                db.add(nuevo_rol)
                print(f" [+] Rol creado: {data_rol['id_rol']} - {data_rol['nombre_rol']}")
            else:
                rol_existente.nombre_rol = data_rol["nombre_rol"]
                rol_existente.descripcion = data_rol["descripcion"]
                print(f" [=] Rol verificado/actualizado: {data_rol['id_rol']} - {data_rol['nombre_rol']}")

        db.commit()
        print("[OK] Siembra de roles completada con éxito.")
    except Exception as e:
        db.rollback()
        print(f"[!] Error sembrando roles: {e}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    sembrar_roles()
