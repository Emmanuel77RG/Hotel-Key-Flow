from sqlalchemy.orm import Session
from app.models.pos import ProductoPOS
from app.schemas.pos import ProductoPOSCrear, ProductoPOSActualizar

CATALOGO_INICIAL_POS = [
    {"nombre": "Desayuno Buffet Continental", "categoria": "Restaurante / Alimentos", "precio_unitario": 280.00, "disponible": True},
    {"nombre": "Chilaquiles KeyFlow con Arrachera", "categoria": "Restaurante / Alimentos", "precio_unitario": 235.00, "disponible": True},
    {"nombre": "Club Sándwich Clásico con Papas", "categoria": "Room Service", "precio_unitario": 210.00, "disponible": True},
    {"nombre": "Hamburguesa Angus Gourmet", "categoria": "Room Service", "precio_unitario": 265.00, "disponible": True},
    {"nombre": "Corte Rib Eye 350g con Guarnición", "categoria": "Restaurante / Alimentos", "precio_unitario": 540.00, "disponible": True},
    {"nombre": "Pasta Alfredo con Camarones", "categoria": "Restaurante / Alimentos", "precio_unitario": 310.00, "disponible": True},
    {"nombre": "Café Americano / Espresso Doble", "categoria": "Bebidas / Bar", "precio_unitario": 65.00, "disponible": True},
    {"nombre": "Jugo Natural / Limonada Mineral", "categoria": "Bebidas / Bar", "precio_unitario": 75.00, "disponible": True},
    {"nombre": "Cerveza Artesanal de la Casa", "categoria": "Bebidas / Bar", "precio_unitario": 110.00, "disponible": True},
    {"nombre": "Copa de Vino Tinto Reserva", "categoria": "Bebidas / Bar", "precio_unitario": 185.00, "disponible": True},
    {"nombre": "Botella de Agua Alcalina 600ml", "categoria": "Minibar / Amenidades", "precio_unitario": 55.00, "disponible": True},
    {"nombre": "Mix de Nueces y Almendras Premium", "categoria": "Minibar / Amenidades", "precio_unitario": 95.00, "disponible": True},
    {"nombre": "Servicio de Lavandería y Planchado (Por Prenda)", "categoria": "Lavandería / Spa", "precio_unitario": 130.00, "disponible": True},
    {"nombre": "Masaje Relajante y Acceso a Spa (60 min)", "categoria": "Lavandería / Spa", "precio_unitario": 750.00, "disponible": True},
]


def sembrar_catalogo_inicial(db: Session) -> None:
    cantidad = db.query(ProductoPOS).count()
    if cantidad == 0:
        try:
            for item in CATALOGO_INICIAL_POS:
                db.add(ProductoPOS(**item))
            db.commit()
        except Exception:
            db.rollback()


def obtener_productos(db: Session, solo_disponibles: bool = False):
    sembrar_catalogo_inicial(db)
    consulta = db.query(ProductoPOS)
    if solo_disponibles:
        consulta = consulta.filter(ProductoPOS.disponible == True)
    return consulta.order_by(ProductoPOS.categoria, ProductoPOS.nombre).all()


def obtener_producto(db: Session, id_producto: int):
    return db.query(ProductoPOS).filter(ProductoPOS.id_producto == id_producto).first()


def crear_producto(db: Session, producto: ProductoPOSCrear):
    db_prod = ProductoPOS(**producto.model_dump())
    db.add(db_prod)
    db.commit()
    db.refresh(db_prod)
    return db_prod


def actualizar_producto(db: Session, id_producto: int, datos: ProductoPOSActualizar):
    db_prod = obtener_producto(db, id_producto)
    if not db_prod:
        return None
    campos = datos.model_dump(exclude_unset=True)
    for clave, valor in campos.items():
        setattr(db_prod, clave, valor)
    db.commit()
    db.refresh(db_prod)
    return db_prod


def eliminar_producto(db: Session, id_producto: int) -> bool:
    db_prod = obtener_producto(db, id_producto)
    if not db_prod:
        return False
    db.delete(db_prod)
    db.commit()
    return True
