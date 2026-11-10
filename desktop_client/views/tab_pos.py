"""
Vista de la pestaña de Punto de Venta (POS) - Restaurante y Room Service.
"""
import requests
from tkinter import messagebox
import customtkinter as ctk

try:
    from widgets import crear_controles_paginacion
except ImportError:
    from desktop_client.widgets import crear_controles_paginacion


class TabPOSView:
    CATEGORIAS_POS = [
        "Restaurante / Alimentos",
        "Bebidas / Bar",
        "Room Service",
        "Minibar / Amenidades",
        "Lavandería / Spa",
    ]
    MODALIDADES_POS = [
        "Room Service",
        "Restaurante / Comedor",
        "Bar / Terraza",
        "Minibar",
        "Lavandería / Spa",
    ]
    COLORES_CATEGORIA_POS = {
        "Restaurante / Alimentos": "#E65100",
        "Bebidas / Bar": "#0277BD",
        "Room Service": "#6A1B9A",
        "Minibar / Amenidades": "#00838F",
        "Lavandería / Spa": "#2E7D32",
    }

    def __init__(self, tab, app):
        self.tab = tab
        self.app = app
        self.pag_pos = 1
        self.ITEMS_POR_PAGINA = getattr(app, "ITEMS_POR_PAGINA", 15)
        self.mapa_reservas_pos = {}

        self.construir()

    def construir(self):
        # Panel Izquierdo (60%): Catálogo interactivo de Productos y Servicios
        frame_izq_pos = ctk.CTkFrame(self.tab)
        frame_izq_pos.pack(side="left", fill="both", expand=True, padx=(10, 5), pady=10)

        frame_top_pos = ctk.CTkFrame(frame_izq_pos, fg_color="transparent")
        frame_top_pos.pack(fill="x", padx=12, pady=(8, 4))

        ctk.CTkLabel(
            frame_top_pos,
            text="Menú de Productos y Servicios",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(side="left")

        ctk.CTkButton(
            frame_top_pos,
            text="Refrescar Menú",
            width=120,
            height=28,
            command=lambda: self.cargar_productos_pos(forzar_red=True)
        ).pack(side="right", padx=(4, 0))

        ctk.CTkButton(
            frame_top_pos,
            text="+ Nuevo Producto / Servicio",
            width=185,
            height=28,
            fg_color="#2E7D32",
            hover_color="#1b5e20",
            command=self.abrir_modal_nuevo_producto_pos
        ).pack(side="right", padx=4)

        # Tarjetas KPI del Punto de Venta
        frame_kpis_pos = ctk.CTkFrame(frame_izq_pos, fg_color="transparent")
        frame_kpis_pos.pack(fill="x", padx=10, pady=2)

        def crear_kpi_pos(parent, titulo, color_borde):
            box = ctk.CTkFrame(parent, border_width=1, border_color=color_borde, corner_radius=8)
            box.pack(side="left", fill="x", expand=True, padx=3, pady=2)
            lbl_val = ctk.CTkLabel(box, text="0", font=ctk.CTkFont(size=15, weight="bold"), text_color=color_borde)
            lbl_val.pack(pady=(3, 0))
            ctk.CTkLabel(box, text=titulo, font=ctk.CTkFont(size=10), text_color="gray75").pack(pady=(0, 3))
            return lbl_val

        self.kpi_pos_catalogo = crear_kpi_pos(frame_kpis_pos, "Total en Menú", "#42A5F5")
        self.kpi_pos_disponibles = crear_kpi_pos(frame_kpis_pos, "Disponibles", "#66BB6A")
        self.kpi_pos_items_comanda = crear_kpi_pos(frame_kpis_pos, "Artículos en Comanda", "#FFA726")

        # Barra de Filtros y Búsqueda en Memoria
        frame_filtros_pos = ctk.CTkFrame(frame_izq_pos, fg_color="transparent")
        frame_filtros_pos.pack(fill="x", padx=12, pady=4)

        self.combo_filtro_cat_pos = ctk.CTkOptionMenu(
            frame_filtros_pos,
            width=185,
            height=26,
            values=["Todas las categorías"] + self.CATEGORIAS_POS,
            command=lambda _v: (setattr(self, "pag_pos", 1), self.renderizar_productos_pos())
        )
        self.combo_filtro_cat_pos.set("Todas las categorías")
        self.combo_filtro_cat_pos.pack(side="left", padx=(0, 4))

        self.combo_filtro_disp_pos = ctk.CTkOptionMenu(
            frame_filtros_pos,
            width=135,
            height=26,
            values=["Solo disponibles", "Todos"],
            command=lambda _v: (setattr(self, "pag_pos", 1), self.renderizar_productos_pos())
        )
        self.combo_filtro_disp_pos.set("Solo disponibles")
        self.combo_filtro_disp_pos.pack(side="left", padx=4)

        self.entry_buscar_pos = ctk.CTkEntry(
            frame_filtros_pos,
            placeholder_text="Buscar platillo, bebida o servicio...",
            height=26
        )
        self.entry_buscar_pos.pack(side="left", fill="x", expand=True, padx=4)
        self.entry_buscar_pos.bind("<KeyRelease>", self._filtrar_pos_debounced)

        ctk.CTkButton(
            frame_filtros_pos,
            text="Limpiar",
            width=65,
            height=26,
            fg_color="gray40",
            hover_color="gray30",
            command=self.limpiar_filtros_pos
        ).pack(side="right", padx=(4, 0))

        self.frame_catalogo_pos = ctk.CTkScrollableFrame(frame_izq_pos)
        self.frame_catalogo_pos.pack(fill="both", expand=True, padx=10, pady=(2, 4))

        self.frame_pag_pos = ctk.CTkFrame(frame_izq_pos, fg_color="transparent")
        self.frame_pag_pos.pack(fill="x", padx=10, pady=(0, 6))

        # Panel Derecho (40% fijo): Comanda Activa y Cargo a Habitación (Cuenta Folio)
        frame_der_pos = ctk.CTkFrame(self.tab, width=385)
        frame_der_pos.pack(side="right", fill="y", padx=(5, 10), pady=10)
        frame_der_pos.pack_propagate(False)

        ctk.CTkLabel(
            frame_der_pos,
            text="Comanda y Cargo a Habitación",
            font=ctk.CTkFont(size=17, weight="bold")
        ).pack(pady=(10, 4))

        # Selector de Habitación / Reserva con Folio Abierto
        ctk.CTkLabel(
            frame_der_pos,
            text="Habitación / Huésped destino (Folio Abierto):",
            font=ctk.CTkFont(size=12),
            text_color="gray75"
        ).pack(pady=(2, 1))

        frame_sel_hab_pos = ctk.CTkFrame(frame_der_pos, fg_color="transparent")
        frame_sel_hab_pos.pack(pady=2)

        self.mapa_reservas_pos = {}
        self.combo_pos_habitacion = ctk.CTkOptionMenu(
            frame_sel_hab_pos,
            width=305,
            height=28,
            values=["Seleccione una habitación activa..."]
        )
        self.combo_pos_habitacion.set("Seleccione una habitación activa...")
        self.combo_pos_habitacion.pack(side="left", padx=(0, 4))

        ctk.CTkButton(
            frame_sel_hab_pos,
            text="🔄",
            width=36,
            height=28,
            command=lambda: self.actualizar_combo_habitaciones_pos(forzar_red=True)
        ).pack(side="left")

        # Modalidad de Servicio y Notas de Comanda
        frame_mod_pos = ctk.CTkFrame(frame_der_pos, fg_color="transparent")
        frame_mod_pos.pack(fill="x", padx=16, pady=(4, 2))

        ctk.CTkLabel(
            frame_mod_pos,
            text="Modalidad:",
            font=ctk.CTkFont(size=12),
            text_color="gray75"
        ).pack(side="left")

        self.combo_pos_modalidad = ctk.CTkOptionMenu(
            frame_mod_pos,
            width=260,
            height=26,
            values=self.MODALIDADES_POS
        )
        self.combo_pos_modalidad.set("Room Service")
        self.combo_pos_modalidad.pack(side="right")

        self.entry_pos_notas = ctk.CTkEntry(
            frame_der_pos,
            width=350,
            height=26,
            placeholder_text="Notas de preparación o entrega (opcional)..."
        )
        self.entry_pos_notas.pack(pady=(3, 5))

        # Lista de Productos en la Comanda Activa
        self.frame_carrito_pos = ctk.CTkScrollableFrame(frame_der_pos, height=205)
        self.frame_carrito_pos.pack(fill="both", expand=True, padx=12, pady=4)

        # Resumen Financiero de la Comanda
        frame_totales_pos = ctk.CTkFrame(frame_der_pos, corner_radius=8, border_width=1, border_color="#37474F")
        frame_totales_pos.pack(fill="x", padx=12, pady=4)

        self.lbl_pos_desglose = ctk.CTkLabel(
            frame_totales_pos,
            text="Subtotal: $0.00   |   IVA (16%): $0.00",
            font=ctk.CTkFont(size=11),
            text_color="gray75"
        )
        self.lbl_pos_desglose.pack(pady=(5, 1))

        self.lbl_pos_total = ctk.CTkLabel(
            frame_totales_pos,
            text="TOTAL COMANDA: $0.00 MXN",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#66BB6A"
        )
        self.lbl_pos_total.pack(pady=(1, 6))

        # Botones de Acción de la Comanda
        frame_btns_comanda = ctk.CTkFrame(frame_der_pos, fg_color="transparent")
        frame_btns_comanda.pack(fill="x", padx=12, pady=(4, 10))

        ctk.CTkButton(
            frame_btns_comanda,
            text="🏨 Cargar a la Habitación",
            width=235,
            height=34,
            fg_color="#2E7D32",
            hover_color="#1b5e20",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.enviar_comanda_habitacion_gui
        ).pack(side="left", padx=(0, 6))

        ctk.CTkButton(
            frame_btns_comanda,
            text="Limpiar",
            width=105,
            height=34,
            fg_color="gray40",
            hover_color="gray30",
            command=self.limpiar_comanda_pos
        ).pack(side="right")

        self.actualizar_combo_habitaciones_pos(self.app.cache_reservas or None)
        self.cargar_productos_pos(forzar_red=not bool(self.app.cache_productos_pos))
        self.renderizar_carrito_pos()

    def _filtrar_pos_debounced(self, _event=None):
        self.pag_pos = 1
        if getattr(self.app, "_after_busq_pos", None) is not None:
            try:
                self.app.after_cancel(self.app._after_busq_pos)
            except Exception:
                pass
        self.app._after_busq_pos = self.app.after(150, self.renderizar_productos_pos)

    def limpiar_filtros_pos(self):
        self.combo_filtro_cat_pos.set("Todas las categorías")
        self.combo_filtro_disp_pos.set("Solo disponibles")
        self.entry_buscar_pos.delete(0, "end")
        self.pag_pos = 1
        self.renderizar_productos_pos()

    def _cambiar_pagina_pos(self, nueva_pag: int):
        self.pag_pos = nueva_pag
        self.renderizar_productos_pos()

    def actualizar_combo_habitaciones_pos(self, lista_res=None, forzar_red: bool = False):
        if not hasattr(self, "combo_pos_habitacion"):
            return
        try:
            if forzar_red or lista_res is None:
                if not forzar_red and self.app.cache_reservas:
                    lista_res = self.app.cache_reservas
                else:
                    resp = self.app.http.get(f"{self.app.url_base}/reservas/")
                    if resp.status_code == 200:
                        lista_res = resp.json()
                        self.app.cache_reservas = lista_res
                    else:
                        return

            self.mapa_reservas_pos = {}
            opciones_activas = []
            opciones_confirmadas = []

            for r in lista_res:
                if r.get("estado_folio") != "Abierto":
                    continue
                est_res = r.get("estado_reserva", "")
                if est_res not in ("Activa", "Confirmada"):
                    continue
                nom = (
                    r.get("nombre_huesped")
                    or getattr(self.app, "mapa_huespedes", {}).get(r.get("id_huesped"))
                    or f"Huésped #{r.get('id_huesped')}"
                )
                hab = r.get("numeros_habitaciones") or "S/N"
                etiqueta = f"Hab. {hab} | {nom} (Folio #{r['id_reserva']} - {est_res})"
                self.mapa_reservas_pos[etiqueta] = r
                if est_res == "Activa":
                    opciones_activas.append(etiqueta)
                else:
                    opciones_confirmadas.append(etiqueta)

            todas_opciones = ["Seleccione una habitación activa..."] + opciones_activas + opciones_confirmadas
            seleccion_previa = self.combo_pos_habitacion.get()
            self.combo_pos_habitacion.configure(values=todas_opciones)
            if seleccion_previa in self.mapa_reservas_pos:
                self.combo_pos_habitacion.set(seleccion_previa)
            elif opciones_activas:
                self.combo_pos_habitacion.set(opciones_activas[0])
            else:
                self.combo_pos_habitacion.set("Seleccione una habitación activa...")
        except requests.exceptions.ConnectionError:
            pass

    def cargar_productos_pos(self, forzar_red: bool = True):
        if forzar_red or not self.app.cache_productos_pos:
            try:
                resp = self.app.http.get(f"{self.app.url_base}/pos/productos")
                if resp.status_code == 200:
                    self.app.cache_productos_pos = resp.json()
            except requests.exceptions.ConnectionError:
                pass
        self.renderizar_productos_pos()

    def renderizar_productos_pos(self):
        if not hasattr(self, "frame_catalogo_pos"):
            return
        for w in self.frame_catalogo_pos.winfo_children():
            w.destroy()

        productos = self.app.cache_productos_pos
        total_cat = len(productos)
        disp_cat = sum(1 for p in productos if p.get("disponible", True))

        if hasattr(self, "kpi_pos_catalogo"):
            self.kpi_pos_catalogo.configure(text=str(total_cat))
            self.kpi_pos_disponibles.configure(text=str(disp_cat))

        filtro_cat = self.combo_filtro_cat_pos.get() if hasattr(self, "combo_filtro_cat_pos") else "Todas las categorías"
        filtro_disp = self.combo_filtro_disp_pos.get() if hasattr(self, "combo_filtro_disp_pos") else "Solo disponibles"
        busq = self.entry_buscar_pos.get().strip().lower() if hasattr(self, "entry_buscar_pos") else ""

        prods_filtrados = []
        for p in productos:
            disp = bool(p.get("disponible", True))
            cat = p.get("categoria") or "Restaurante / Alimentos"
            nom = p.get("nombre") or ""

            if filtro_disp == "Solo disponibles" and not disp:
                continue
            if filtro_cat != "Todas las categorías" and cat != filtro_cat:
                continue
            if busq and busq not in nom.lower() and busq not in cat.lower():
                continue

            prods_filtrados.append(p)

        inicio, fin = crear_controles_paginacion(
            self.frame_pag_pos,
            self.pag_pos,
            len(prods_filtrados),
            self.ITEMS_POR_PAGINA,
            self._cambiar_pagina_pos,
        )

        mostrados = 0
        for p in prods_filtrados[inicio:fin]:
            disp = bool(p.get("disponible", True))
            cat = p.get("categoria") or "Restaurante / Alimentos"
            nom = p.get("nombre") or ""
            precio = float(p.get("precio_unitario", 0.0))

            mostrados += 1
            card = ctk.CTkFrame(self.frame_catalogo_pos)
            card.pack(fill="x", padx=4, pady=3)

            frame_info = ctk.CTkFrame(card, fg_color="transparent")
            frame_info.pack(side="left", fill="x", expand=True, padx=8, pady=6)

            fila_sup = ctk.CTkFrame(frame_info, fg_color="transparent")
            fila_sup.pack(fill="x")

            color_cat = self.COLORES_CATEGORIA_POS.get(cat, "#1976D2")
            ctk.CTkLabel(
                fila_sup,
                text=f" {cat} ",
                font=ctk.CTkFont(size=10, weight="bold"),
                fg_color=color_cat,
                text_color="white",
                corner_radius=5
            ).pack(side="left", padx=(0, 6))

            if not disp:
                ctk.CTkLabel(
                    fila_sup,
                    text=" No disponible ",
                    font=ctk.CTkFont(size=10, weight="bold"),
                    fg_color="#C62828",
                    text_color="white",
                    corner_radius=5
                ).pack(side="left", padx=(0, 6))

            ctk.CTkLabel(
                fila_sup,
                text=nom,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color="white" if disp else "gray55",
                anchor="w"
            ).pack(side="left")

            ctk.CTkLabel(
                frame_info,
                text=f"Precio unitario: ${precio:.2f} MXN",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#81C784" if disp else "gray50",
                anchor="w"
            ).pack(fill="x", pady=(2, 0))

            frame_acc = ctk.CTkFrame(card, fg_color="transparent")
            frame_acc.pack(side="right", padx=6, pady=6)

            ctk.CTkButton(
                frame_acc,
                text="Eliminar",
                width=58,
                height=25,
                fg_color="#C62828",
                hover_color="#8E0000",
                command=lambda prod=p: self.eliminar_producto_pos_gui(prod)
            ).pack(side="right", padx=2)

            ctk.CTkButton(
                frame_acc,
                text="Editar",
                width=52,
                height=25,
                command=lambda prod=p: self.abrir_modal_editar_producto_pos(prod)
            ).pack(side="right", padx=2)

            if disp:
                ctk.CTkButton(
                    frame_acc,
                    text="+ Agregar",
                    width=82,
                    height=25,
                    fg_color="#2E7D32",
                    hover_color="#1b5e20",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    command=lambda prod=p: self.agregar_al_carrito_pos(prod)
                ).pack(side="right", padx=3)

        if mostrados == 0:
            ctk.CTkLabel(
                self.frame_catalogo_pos,
                text="No se encontraron productos o servicios para el filtro seleccionado.",
                text_color="gray60",
                font=ctk.CTkFont(size=12)
            ).pack(pady=20)

    def agregar_al_carrito_pos(self, producto: dict):
        pid = producto["id_producto"]
        if pid in self.app.carrito_pos:
            self.app.carrito_pos[pid]["cantidad"] += 1
        else:
            self.app.carrito_pos[pid] = {
                "id_producto": pid,
                "nombre": producto["nombre"],
                "categoria": producto.get("categoria", "Restaurante / Alimentos"),
                "precio_unitario": float(producto["precio_unitario"]),
                "cantidad": 1,
            }
        self.renderizar_carrito_pos()

    def cambiar_cantidad_carrito_pos(self, id_producto: int, delta: int):
        if id_producto not in self.app.carrito_pos:
            return
        nueva_cant = self.app.carrito_pos[id_producto]["cantidad"] + delta
        if nueva_cant <= 0:
            del self.app.carrito_pos[id_producto]
        else:
            self.app.carrito_pos[id_producto]["cantidad"] = nueva_cant
        self.renderizar_carrito_pos()

    def quitar_del_carrito_pos(self, id_producto: int):
        if id_producto in self.app.carrito_pos:
            del self.app.carrito_pos[id_producto]
            self.renderizar_carrito_pos()

    def limpiar_comanda_pos(self):
        self.app.carrito_pos.clear()
        if hasattr(self, "entry_pos_notas"):
            self.entry_pos_notas.delete(0, "end")
        self.renderizar_carrito_pos()

    def renderizar_carrito_pos(self):
        if not hasattr(self, "frame_carrito_pos"):
            return
        for w in self.frame_carrito_pos.winfo_children():
            w.destroy()

        total_articulos = sum(item["cantidad"] for item in self.app.carrito_pos.values())
        if hasattr(self, "kpi_pos_items_comanda"):
            self.kpi_pos_items_comanda.configure(text=str(total_articulos))

        if not self.app.carrito_pos:
            ctk.CTkLabel(
                self.frame_carrito_pos,
                text="La comanda está vacía.\nSelecciona productos del catálogo izquierdo\npulsando '+ Agregar'.",
                text_color="gray60",
                font=ctk.CTkFont(size=12),
                justify="center"
            ).pack(pady=35)
            self.lbl_pos_desglose.configure(text="Subtotal: $0.00   |   IVA (16%): $0.00")
            self.lbl_pos_total.configure(text="TOTAL COMANDA: $0.00 MXN")
            return

        total_general = 0.0
        for pid, item in self.app.carrito_pos.items():
            cant = item["cantidad"]
            precio = float(item["precio_unitario"])
            importe = round(cant * precio, 2)
            total_general = round(total_general + importe, 2)

            fila = ctk.CTkFrame(self.frame_carrito_pos)
            fila.pack(fill="x", padx=2, pady=2)

            info_f = ctk.CTkFrame(fila, fg_color="transparent")
            info_f.pack(side="left", fill="x", expand=True, padx=6, pady=4)

            ctk.CTkLabel(
                info_f,
                text=item["nombre"],
                font=ctk.CTkFont(size=12, weight="bold"),
                anchor="w"
            ).pack(fill="x")

            ctk.CTkLabel(
                info_f,
                text=f"{cant} x ${precio:.2f} = ${importe:.2f}",
                font=ctk.CTkFont(size=11),
                text_color="#81C784",
                anchor="w"
            ).pack(fill="x")

            ctrl_f = ctk.CTkFrame(fila, fg_color="transparent")
            ctrl_f.pack(side="right", padx=4, pady=4)

            ctk.CTkButton(
                ctrl_f,
                text="-",
                width=26,
                height=24,
                fg_color="gray40",
                hover_color="gray30",
                command=lambda p_id=pid: self.cambiar_cantidad_carrito_pos(p_id, -1)
            ).pack(side="left", padx=1)

            ctk.CTkLabel(
                ctrl_f,
                text=str(cant),
                width=22,
                font=ctk.CTkFont(size=12, weight="bold")
            ).pack(side="left", padx=2)

            ctk.CTkButton(
                ctrl_f,
                text="+",
                width=26,
                height=24,
                fg_color="#1976D2",
                hover_color="#1565C0",
                command=lambda p_id=pid: self.cambiar_cantidad_carrito_pos(p_id, 1)
            ).pack(side="left", padx=1)

            ctk.CTkButton(
                ctrl_f,
                text="✕",
                width=26,
                height=24,
                fg_color="#C62828",
                hover_color="#8E0000",
                command=lambda p_id=pid: self.quitar_del_carrito_pos(p_id)
            ).pack(side="left", padx=(4, 0))

        subtotal = round(total_general / 1.16, 2)
        iva = round(total_general - subtotal, 2)
        self.lbl_pos_desglose.configure(text=f"Subtotal: ${subtotal:.2f}   |   IVA (16%): ${iva:.2f}")
        self.lbl_pos_total.configure(text=f"TOTAL COMANDA: ${total_general:.2f} MXN")

    def enviar_comanda_habitacion_gui(self):
        if not self.app.carrito_pos:
            messagebox.showwarning("Comanda vacía", "Agrega al menos un producto o servicio a la comanda antes de cargar a la habitación.")
            return

        etiqueta_hab = self.combo_pos_habitacion.get()
        reserva_sel = getattr(self, "mapa_reservas_pos", {}).get(etiqueta_hab)
        if not reserva_sel:
            messagebox.showwarning(
                "Habitación requerida",
                "Selecciona una habitación / huésped con Cuenta Folio abierta en el menú desplegable."
            )
            return

        id_reserva = reserva_sel["id_reserva"]
        modalidad = self.combo_pos_modalidad.get()
        notas = self.entry_pos_notas.get().strip()
        items_payload = [
            {
                "id_producto": item["id_producto"],
                "nombre": item["nombre"],
                "cantidad": item["cantidad"],
                "precio_unitario": item["precio_unitario"],
            }
            for item in self.app.carrito_pos.values()
        ]

        try:
            payload = {
                "id_reserva": int(id_reserva),
                "modalidad_servicio": modalidad,
                "notas": notas or None,
                "items": items_payload,
            }
            resp = self.app.http.post(f"{self.app.url_base}/pos/cargar-habitacion", json=payload)
            if resp.status_code in (200, 201):
                cargo_creado = resp.json()
                hab_num = reserva_sel.get("numeros_habitaciones") or "S/N"
                nom_huesped = reserva_sel.get("nombre_huesped") or f"Huésped #{reserva_sel.get('id_huesped')}"
                messagebox.showinfo(
                    "Cargo Enviado a la Habitación",
                    f"La comanda fue cargada exitosamente a la Cuenta Folio.\n\n"
                    f"Habitación: {hab_num} ({nom_huesped})\n"
                    f"Folio / Reserva: #{id_reserva}\n"
                    f"Concepto: {cargo_creado.get('descripcion')}\n"
                    f"Monto Cargado: ${float(cargo_creado.get('monto', 0)):.2f} MXN"
                )
                self.limpiar_comanda_pos()
                if hasattr(self.app, "entry_folio_reserva_id") and self.app.entry_folio_reserva_id.get().strip() == str(id_reserva):
                    self.app.consultar_folio()
            else:
                detalle = self.app._extraer_detalle_error(resp)
                messagebox.showerror("No se pudo cargar la comanda", detalle)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def abrir_modal_nuevo_producto_pos(self):
        modal = self.app._crear_modal("Nuevo Producto o Servicio POS", "390x340")

        ctk.CTkLabel(
            modal,
            text="Alta de Producto / Servicio",
            font=ctk.CTkFont(size=17, weight="bold")
        ).pack(pady=(14, 8))

        ctk.CTkLabel(modal, text="Nombre del platillo, bebida o servicio:", font=ctk.CTkFont(size=12)).pack(pady=(4, 1))
        entry_nom = ctk.CTkEntry(modal, width=300, placeholder_text="Ej. Enchiladas Suizas / Lavado en Seco")
        entry_nom.pack(pady=3)

        ctk.CTkLabel(modal, text="Categoría:", font=ctk.CTkFont(size=12)).pack(pady=(6, 1))
        combo_cat = ctk.CTkOptionMenu(modal, width=300, values=self.CATEGORIAS_POS)
        combo_cat.set("Restaurante / Alimentos")
        combo_cat.pack(pady=3)

        ctk.CTkLabel(modal, text="Precio Unitario (MXN):", font=ctk.CTkFont(size=12)).pack(pady=(6, 1))
        entry_precio = ctk.CTkEntry(modal, width=300, placeholder_text="Ej. 195.00")
        entry_precio.pack(pady=3)

        var_disp = ctk.BooleanVar(value=True)
        chk_disp = ctk.CTkCheckBox(modal, text="Disponible inmediatamente para venta", variable=var_disp)
        chk_disp.pack(pady=10)

        def guardar():
            nom = entry_nom.get().strip()
            precio_txt = entry_precio.get().strip()
            if not nom or not precio_txt:
                messagebox.showwarning("Campos obligatorios", "Ingresa el nombre y el precio unitario del producto.")
                return
            try:
                precio = float(precio_txt)
                if precio <= 0:
                    messagebox.showwarning("Precio inválido", "El precio unitario debe ser mayor a $0.00.")
                    return
                resp = self.app.http.post(
                    f"{self.app.url_base}/pos/productos",
                    json={
                        "nombre": nom,
                        "categoria": combo_cat.get(),
                        "precio_unitario": precio,
                        "disponible": bool(var_disp.get()),
                    },
                )
                if resp.status_code in (200, 201):
                    messagebox.showinfo("Producto Registrado", f"'{nom}' fue agregado al catálogo del Punto de Venta.")
                    modal.destroy()
                    self.cargar_productos_pos(forzar_red=True)
                else:
                    messagebox.showerror("Error", self.app._extraer_detalle_error(resp))
            except ValueError:
                messagebox.showerror("Precio inválido", "Ingresa un monto numérico válido (ej. 195.00).")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        ctk.CTkButton(
            modal,
            text="Guardar Producto",
            width=200,
            fg_color="#2E7D32",
            hover_color="#1b5e20",
            command=guardar
        ).pack(pady=10)
        self.app._mostrar_modal(modal)

    def abrir_modal_editar_producto_pos(self, producto: dict):
        modal = self.app._crear_modal(f"Editar Producto #{producto['id_producto']}", "390x340")

        ctk.CTkLabel(
            modal,
            text="Editar Producto / Servicio",
            font=ctk.CTkFont(size=17, weight="bold")
        ).pack(pady=(14, 8))

        ctk.CTkLabel(modal, text="Nombre del producto o servicio:", font=ctk.CTkFont(size=12)).pack(pady=(4, 1))
        entry_nom = ctk.CTkEntry(modal, width=300)
        entry_nom.insert(0, producto.get("nombre") or "")
        entry_nom.pack(pady=3)

        ctk.CTkLabel(modal, text="Categoría:", font=ctk.CTkFont(size=12)).pack(pady=(6, 1))
        combo_cat = ctk.CTkOptionMenu(modal, width=300, values=self.CATEGORIAS_POS)
        cat_act = producto.get("categoria") or "Restaurante / Alimentos"
        combo_cat.set(cat_act if cat_act in self.CATEGORIAS_POS else "Restaurante / Alimentos")
        combo_cat.pack(pady=3)

        ctk.CTkLabel(modal, text="Precio Unitario (MXN):", font=ctk.CTkFont(size=12)).pack(pady=(6, 1))
        entry_precio = ctk.CTkEntry(modal, width=300)
        entry_precio.insert(0, f"{float(producto.get('precio_unitario', 0.0)):.2f}")
        entry_precio.pack(pady=3)

        var_disp = ctk.BooleanVar(value=bool(producto.get("disponible", True)))
        chk_disp = ctk.CTkCheckBox(modal, text="Producto disponible para venta", variable=var_disp)
        chk_disp.pack(pady=10)

        def guardar():
            nom = entry_nom.get().strip()
            precio_txt = entry_precio.get().strip()
            if not nom or not precio_txt:
                messagebox.showwarning("Campos obligatorios", "El nombre y el precio no pueden quedar vacíos.")
                return
            try:
                precio = float(precio_txt)
                if precio <= 0:
                    messagebox.showwarning("Precio inválido", "El precio unitario debe ser mayor a $0.00.")
                    return
                resp = self.app.http.put(
                    f"{self.app.url_base}/pos/productos/{producto['id_producto']}",
                    json={
                        "nombre": nom,
                        "categoria": combo_cat.get(),
                        "precio_unitario": precio,
                        "disponible": bool(var_disp.get()),
                    },
                )
                if resp.status_code == 200:
                    pid = producto["id_producto"]
                    if pid in self.app.carrito_pos:
                        self.app.carrito_pos[pid]["nombre"] = nom
                        self.app.carrito_pos[pid]["precio_unitario"] = precio
                        self.renderizar_carrito_pos()
                    messagebox.showinfo("Producto Actualizado", f"'{nom}' se actualizó correctamente.")
                    modal.destroy()
                    self.cargar_productos_pos(forzar_red=True)
                else:
                    messagebox.showerror("Error", self.app._extraer_detalle_error(resp))
            except ValueError:
                messagebox.showerror("Precio inválido", "Ingresa un monto numérico válido.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        ctk.CTkButton(modal, text="Guardar Cambios", width=200, command=guardar).pack(pady=10)
        self.app._mostrar_modal(modal)

    def eliminar_producto_pos_gui(self, producto: dict):
        pid = producto["id_producto"]
        nom = producto.get("nombre") or f"Producto #{pid}"
        confirmar = messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Deseas eliminar '{nom}' del catálogo del Punto de Venta?"
        )
        if not confirmar:
            return
        try:
            resp = self.app.http.delete(f"{self.app.url_base}/pos/productos/{pid}")
            if resp.status_code == 200:
                if pid in self.app.carrito_pos:
                    del self.app.carrito_pos[pid]
                    self.renderizar_carrito_pos()
                self.cargar_productos_pos(forzar_red=True)
            else:
                messagebox.showerror("Error", self.app._extraer_detalle_error(resp))
        except Exception as e:
            messagebox.showerror("Error", str(e))
