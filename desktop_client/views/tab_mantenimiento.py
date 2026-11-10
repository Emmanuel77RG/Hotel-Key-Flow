"""
Vista de la pestaña de Mantenimiento y Control de Fallas de Habitaciones.
"""
import requests
from tkinter import messagebox
import customtkinter as ctk

try:
    from widgets import crear_controles_paginacion
except ImportError:
    from desktop_client.widgets import crear_controles_paginacion


class TabMantenimientoView:
    CATEGORIAS_MANTENIMIENTO = [
        "Selecciona una categoría",
        "Plomería",
        "Climatización / A/C",
        "Electricidad",
        "Cerrajería",
        "Mobiliario",
        "TV / Redes",
        "General",
    ]
    PRIORIDADES_MANTENIMIENTO = ["Baja", "Media", "Alta", "Crítica"]
    CATALOGO_FALLAS_COMUNES = {
        "Fuga de agua en baño / lavabo": ("Plomería", "Alta"),
        "Inodoro con descarga averiada": ("Plomería", "Crítica"),
        "Aire acondicionado / calefacción no enfría": ("Climatización / A/C", "Alta"),
        "Falla en cerradura electrónica de puerta": ("Cerrajería", "Crítica"),
        "Falla eléctrica o luminaria fundida": ("Electricidad", "Media"),
        "Televisión o señal Wi-Fi sin servicio": ("TV / Redes", "Baja"),
        "Mobiliario, cristal o persiana dañada": ("Mobiliario", "Media"),
    }

    def __init__(self, tab, app):
        self.tab = tab
        self.app = app
        self.pag_tickets = 1
        self.ITEMS_POR_PAGINA = getattr(app, "ITEMS_POR_PAGINA", 15)
        self.mapa_hab_mantenimiento = {}

        self.construir()

    def construir(self):
        # Panel Izquierdo: Formulario para levantar ticket de falla
        frame_izq_m = ctk.CTkFrame(self.tab, width=340)
        frame_izq_m.pack(side="left", fill="y", padx=(10, 5), pady=10)
        frame_izq_m.pack_propagate(False)

        ctk.CTkLabel(
            frame_izq_m,
            text="Reportar Falla / Nuevo Ticket",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(12, 4))

        ctk.CTkLabel(
            frame_izq_m,
            text="Habitación averiada:",
            font=ctk.CTkFont(size=12),
            text_color="gray75"
        ).pack(pady=(2, 1))

        self.mapa_hab_mantenimiento = {}
        self.combo_mant_hab = ctk.CTkOptionMenu(
            frame_izq_m,
            width=295,
            values=["Seleccione una habitación..."]
        )
        self.combo_mant_hab.set("Seleccione una habitación...")
        self.combo_mant_hab.pack(pady=2)

        ctk.CTkLabel(
            frame_izq_m,
            text="Catálogo rápido de fallas comunes (opcional):",
            font=ctk.CTkFont(size=12),
            text_color="gray75"
        ).pack(pady=(6, 1))

        self.combo_falla_rapida = ctk.CTkOptionMenu(
            frame_izq_m,
            width=295,
            values=["Seleccione falla común (opcional)..."] + list(self.CATALOGO_FALLAS_COMUNES.keys()),
            command=self.al_seleccionar_falla_rapida
        )
        self.combo_falla_rapida.set("Seleccione falla común (opcional)...")
        self.combo_falla_rapida.pack(pady=2)

        ctk.CTkLabel(
            frame_izq_m,
            text="Categoría Técnica y Nivel de Prioridad:",
            font=ctk.CTkFont(size=12),
            text_color="gray75"
        ).pack(pady=(6, 1))

        frame_cat_prio = ctk.CTkFrame(frame_izq_m, fg_color="transparent")
        frame_cat_prio.pack(pady=2)

        self.combo_mant_categoria = ctk.CTkOptionMenu(
            frame_cat_prio,
            width=185,
            values=self.CATEGORIAS_MANTENIMIENTO
        )
        self.combo_mant_categoria.set("Selecciona una categoría")
        self.combo_mant_categoria.pack(side="left", padx=(0, 5))

        self.combo_mant_prioridad = ctk.CTkOptionMenu(
            frame_cat_prio,
            width=105,
            values=self.PRIORIDADES_MANTENIMIENTO
        )
        self.combo_mant_prioridad.set("Media")
        self.combo_mant_prioridad.pack(side="left")

        ctk.CTkLabel(
            frame_izq_m,
            text="Descripción detallada de la falla:",
            font=ctk.CTkFont(size=12),
            text_color="gray75"
        ).pack(pady=(6, 1))

        self.entry_mant_desc = ctk.CTkEntry(
            frame_izq_m,
            width=295,
            placeholder_text="Ej. Fuga de agua debajo del lavabo..."
        )
        self.entry_mant_desc.pack(pady=2)

        ctk.CTkLabel(
            frame_izq_m,
            text="Al levantar el ticket, la habitación pasará\nautomáticamente a estado 'Mantenimiento'\nbloqueando su asignación a huéspedes.",
            font=ctk.CTkFont(size=11),
            text_color="#FFB74D",
            justify="center"
        ).pack(pady=(8, 6))

        frame_btns_m = ctk.CTkFrame(frame_izq_m, fg_color="transparent")
        frame_btns_m.pack(pady=6)

        ctk.CTkButton(
            frame_btns_m,
            text="Levantar Ticket",
            width=165,
            fg_color="#E65100",
            hover_color="#BF360C",
            command=self.crear_ticket_mantenimiento_gui
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            frame_btns_m,
            text="Limpiar",
            width=95,
            fg_color="gray40",
            hover_color="gray30",
            command=self.limpiar_form_mantenimiento
        ).pack(side="left", padx=4)

        # Panel Derecho: KPIs, Filtros y Bitácora de Reparaciones
        frame_der_m = ctk.CTkFrame(self.tab)
        frame_der_m.pack(side="right", fill="both", expand=True, padx=(5, 10), pady=10)

        frame_top_m = ctk.CTkFrame(frame_der_m, fg_color="transparent")
        frame_top_m.pack(fill="x", padx=12, pady=(8, 4))

        ctk.CTkLabel(
            frame_top_m,
            text="Bitácora e Historial de Reparaciones",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(side="left")

        ctk.CTkButton(
            frame_top_m,
            text="Refrescar Bitácora",
            width=130,
            height=26,
            command=lambda: self.cargar_tickets_mantenimiento(forzar_red=True)
        ).pack(side="right")

        # Tarjetas KPI de Mantenimiento
        frame_kpis = ctk.CTkFrame(frame_der_m, fg_color="transparent")
        frame_kpis.pack(fill="x", padx=10, pady=2)

        def crear_kpi_box(parent, titulo, color_borde):
            box = ctk.CTkFrame(parent, border_width=1, border_color=color_borde, corner_radius=8)
            box.pack(side="left", fill="x", expand=True, padx=3, pady=2)
            lbl_val = ctk.CTkLabel(box, text="0", font=ctk.CTkFont(size=16, weight="bold"), text_color=color_borde)
            lbl_val.pack(pady=(4, 0))
            ctk.CTkLabel(box, text=titulo, font=ctk.CTkFont(size=10), text_color="gray75").pack(pady=(0, 4))
            return lbl_val

        self.kpi_mant_pendientes = crear_kpi_box(frame_kpis, "Pendientes", "#FFA726")
        self.kpi_mant_reparacion = crear_kpi_box(frame_kpis, "En Reparación", "#29B6F6")
        self.kpi_mant_criticos = crear_kpi_box(frame_kpis, "Críticos Activos", "#EF5350")
        self.kpi_mant_resueltos = crear_kpi_box(frame_kpis, "Resueltos", "#66BB6A")

        # Barra de Filtros y Búsqueda
        frame_filtros_m = ctk.CTkFrame(frame_der_m, fg_color="transparent")
        frame_filtros_m.pack(fill="x", padx=12, pady=4)

        self.combo_filtro_tickets = ctk.CTkOptionMenu(
            frame_filtros_m,
            width=155,
            height=26,
            values=["Todos los estados", "Activos", "Pendiente", "En Reparación", "Resuelto"],
            command=lambda _v: (setattr(self, "pag_tickets", 1), self.renderizar_tickets_mantenimiento())
        )
        self.combo_filtro_tickets.set("Todos los estados")
        self.combo_filtro_tickets.pack(side="left", padx=(0, 4))

        self.combo_filtro_prio = ctk.CTkOptionMenu(
            frame_filtros_m,
            width=145,
            height=26,
            values=["Todas prioridades", "Crítica", "Alta", "Media", "Baja"],
            command=lambda _v: (setattr(self, "pag_tickets", 1), self.renderizar_tickets_mantenimiento())
        )
        self.combo_filtro_prio.set("Todas prioridades")
        self.combo_filtro_prio.pack(side="left", padx=4)

        self.entry_buscar_ticket = ctk.CTkEntry(
            frame_filtros_m,
            placeholder_text="Buscar por habitación, categoría o falla...",
            height=26
        )
        self.entry_buscar_ticket.pack(side="left", fill="x", expand=True, padx=4)
        self.entry_buscar_ticket.bind("<KeyRelease>", self._filtrar_tickets_debounced)

        ctk.CTkButton(
            frame_filtros_m,
            text="Limpiar",
            width=68,
            height=26,
            fg_color="gray40",
            hover_color="gray30",
            command=self.limpiar_filtros_mantenimiento
        ).pack(side="right", padx=(4, 0))

        self.frame_lista_tickets = ctk.CTkScrollableFrame(frame_der_m)
        self.frame_lista_tickets.pack(fill="both", expand=True, padx=10, pady=(2, 4))

        self.frame_paginacion_tickets = ctk.CTkFrame(frame_der_m, fg_color="transparent")
        self.frame_paginacion_tickets.pack(fill="x", padx=10, pady=(0, 6))

        self.actualizar_combo_habitaciones_mantenimiento(self.app.cache_habitaciones or None)
        self.cargar_tickets_mantenimiento(forzar_red=not bool(self.app.cache_tickets))

    def limpiar_filtros_mantenimiento(self):
        self.combo_filtro_tickets.set("Todos los estados")
        self.combo_filtro_prio.set("Todas prioridades")
        self.entry_buscar_ticket.delete(0, "end")
        self.pag_tickets = 1
        self.renderizar_tickets_mantenimiento()

    def _filtrar_tickets_debounced(self, _event=None):
        self.pag_tickets = 1
        if getattr(self.app, "_after_busq_ticket", None) is not None:
            try:
                self.app.after_cancel(self.app._after_busq_ticket)
            except Exception:
                pass
        self.app._after_busq_ticket = self.app.after(150, self.renderizar_tickets_mantenimiento)

    def _cambiar_pagina_tickets(self, nueva_pag: int):
        self.pag_tickets = nueva_pag
        self.renderizar_tickets_mantenimiento()

    def actualizar_combo_habitaciones_mantenimiento(self, lista_habs=None):
        if not hasattr(self, "combo_mant_hab"):
            return
        try:
            if lista_habs is None:
                if self.app.cache_habitaciones:
                    lista_habs = self.app.cache_habitaciones
                else:
                    resp = self.app.http.get(f"{self.app.url_base}/habitaciones/")
                    if resp.status_code == 200:
                        lista_habs = resp.json()
                        self.app.cache_habitaciones = lista_habs
                    else:
                        return
            self.mapa_hab_mantenimiento = {}
            opciones = ["Seleccione una habitación..."]
            for h in lista_habs:
                etiqueta = f"Hab. {h['numero_habitacion']} - {h['tipo']} [{h['estado']}]"
                self.mapa_hab_mantenimiento[etiqueta] = h["id_habitacion"]
                opciones.append(etiqueta)
            self.combo_mant_hab.configure(values=opciones)
        except requests.exceptions.ConnectionError:
            pass

    def al_seleccionar_falla_rapida(self, opcion: str):
        if opcion in self.CATALOGO_FALLAS_COMUNES:
            cat_sug, prio_sug = self.CATALOGO_FALLAS_COMUNES[opcion]
            self.entry_mant_desc.delete(0, "end")
            self.entry_mant_desc.insert(0, opcion)
            self.combo_mant_categoria.set(cat_sug)
            self.combo_mant_prioridad.set(prio_sug)

    def limpiar_form_mantenimiento(self):
        self.combo_mant_hab.set("Seleccione una habitación...")
        self.combo_falla_rapida.set("Seleccione falla común (opcional)...")
        self.combo_mant_categoria.set("Selecciona una categoría")
        self.combo_mant_prioridad.set("Media")
        self.entry_mant_desc.delete(0, "end")

    def crear_ticket_mantenimiento_gui(self):
        hab_sel = self.combo_mant_hab.get()
        id_hab = getattr(self, "mapa_hab_mantenimiento", {}).get(hab_sel)
        if not id_hab:
            messagebox.showwarning("Habitación requerida", "Selecciona una habitación del menú desplegable.")
            return
        desc = self.entry_mant_desc.get().strip()
        if not desc:
            messagebox.showwarning("Descripción requerida", "Ingresa o selecciona la descripción de la falla.")
            return
        cat_sel = self.combo_mant_categoria.get()
        categoria = "General" if cat_sel == "Selecciona una categoría" else cat_sel
        prioridad = self.combo_mant_prioridad.get()
        try:
            datos = {
                "id_habitacion": int(id_hab),
                "categoria": categoria,
                "prioridad": prioridad,
                "descripcion_falla": desc,
            }
            resp = self.app.http.post(f"{self.app.url_base}/mantenimiento/", json=datos)
            if resp.status_code in (200, 201):
                t_json = resp.json()
                messagebox.showinfo(
                    "Ticket Levantado",
                    f"Ticket #{t_json.get('id_ticket')} registrado correctamente.\n"
                    f"Categoría: {t_json.get('categoria')} | Prioridad: {t_json.get('prioridad')}\n"
                    f"La Habitación {t_json.get('numero_habitacion')} pasó a estado 'Mantenimiento'."
                )
                self.limpiar_form_mantenimiento()
                self.app.cargar_habitaciones()
                self.cargar_tickets_mantenimiento(forzar_red=True)
            else:
                detalle = self.app._extraer_detalle_error(resp)
                messagebox.showerror("No se pudo levantar el ticket", detalle)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def cambiar_estado_ticket_gui(self, id_ticket: int, nuevo_estado: str, num_hab: str, nota_resolucion: str = None):
        try:
            payload = {"estado_ticket": nuevo_estado}
            if nota_resolucion is not None:
                payload["nota_resolucion"] = nota_resolucion
            resp = self.app.http.patch(
                f"{self.app.url_base}/mantenimiento/{id_ticket}/estado",
                json=payload
            )
            if resp.status_code == 200:
                if nuevo_estado == "Resuelto":
                    messagebox.showinfo(
                        "Reparación Concluida",
                        f"El Ticket #{id_ticket} (Hab. {num_hab}) fue marcado como 'Resuelto'.\n"
                        f"La habitación pasó a estado 'Sucia' para su limpieza."
                    )
                self.app.cargar_habitaciones()
                self.cargar_tickets_mantenimiento(forzar_red=True)
                return True
            else:
                detalle = self.app._extraer_detalle_error(resp)
                messagebox.showerror("No se pudo actualizar el ticket", detalle)
                return False
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return False

    def abrir_modal_resolver_ticket(self, ticket: dict):
        modal = self.app._crear_modal(f"Resolver Ticket #{ticket['id_ticket']}", "390x280")

        num_hab = str(ticket.get("numero_habitacion") or ticket.get("id_habitacion") or "S/N")
        ctk.CTkLabel(
            modal,
            text=f"Concluir Reparación - Ticket #{ticket['id_ticket']} (Hab. {num_hab})",
            font=ctk.CTkFont(size=15, weight="bold")
        ).pack(pady=(14, 4))

        ctk.CTkLabel(
            modal,
            text=f"Falla reportada: {ticket.get('descripcion_falla', '')}",
            font=ctk.CTkFont(size=12),
            text_color="gray75",
            wraplength=340
        ).pack(pady=(0, 10))

        ctk.CTkLabel(
            modal,
            text="Diagnóstico técnico / Solución aplicada:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(pady=(4, 2))

        entry_nota = ctk.CTkEntry(
            modal,
            width=330,
            placeholder_text="Ej. Se reemplazó empaque y se verificó presión..."
        )
        entry_nota.pack(pady=6)

        def confirmar():
            nota = entry_nota.get().strip() or "Reparación verificada y concluida satisfactoriamente."
            if self.cambiar_estado_ticket_gui(ticket["id_ticket"], "Resuelto", num_hab, nota):
                modal.destroy()

        frame_b = ctk.CTkFrame(modal, fg_color="transparent")
        frame_b.pack(pady=16)
        ctk.CTkButton(
            frame_b,
            text="Confirmar y Liberar Habitación",
            width=205,
            fg_color="#2E7D32",
            hover_color="#1b5e20",
            command=confirmar
        ).pack(side="left", padx=4)
        ctk.CTkButton(
            frame_b,
            text="Cancelar",
            width=90,
            fg_color="gray40",
            hover_color="gray30",
            command=modal.destroy
        ).pack(side="left", padx=4)
        self.app._mostrar_modal(modal)
        entry_nota.focus_set()

    def abrir_modal_editar_ticket(self, ticket: dict):
        modal = self.app._crear_modal(f"Editar Ticket #{ticket['id_ticket']}", "380x320")

        ctk.CTkLabel(
            modal,
            text=f"Editar Ticket #{ticket['id_ticket']} (Hab. {ticket.get('numero_habitacion')})",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(14, 8))

        ctk.CTkLabel(modal, text="Categoría Técnica:", font=ctk.CTkFont(size=12)).pack(pady=(2, 1))
        cats_validas = [c for c in self.CATEGORIAS_MANTENIMIENTO if c != "Selecciona una categoría"]
        combo_cat = ctk.CTkOptionMenu(modal, width=280, values=cats_validas)
        cat_act = ticket.get("categoria") or "General"
        combo_cat.set(cat_act if cat_act in cats_validas else "General")
        combo_cat.pack(pady=3)

        ctk.CTkLabel(modal, text="Prioridad / Severidad:", font=ctk.CTkFont(size=12)).pack(pady=(6, 1))
        combo_prio = ctk.CTkOptionMenu(modal, width=280, values=self.PRIORIDADES_MANTENIMIENTO)
        prio_act = ticket.get("prioridad") or "Media"
        combo_prio.set(prio_act if prio_act in self.PRIORIDADES_MANTENIMIENTO else "Media")
        combo_prio.pack(pady=3)

        ctk.CTkLabel(modal, text="Descripción de la falla:", font=ctk.CTkFont(size=12)).pack(pady=(6, 1))
        entry_desc = ctk.CTkEntry(modal, width=280)
        entry_desc.insert(0, ticket.get("descripcion_falla") or "")
        entry_desc.pack(pady=3)

        def guardar():
            nueva_desc = entry_desc.get().strip()
            if not nueva_desc:
                messagebox.showwarning("Campo obligatorio", "La descripción no puede quedar vacía.")
                return
            try:
                resp = self.app.http.put(
                    f"{self.app.url_base}/mantenimiento/{ticket['id_ticket']}",
                    json={
                        "categoria": combo_cat.get(),
                        "prioridad": combo_prio.get(),
                        "descripcion_falla": nueva_desc,
                    },
                )
                if resp.status_code == 200:
                    messagebox.showinfo("Éxito", f"Ticket #{ticket['id_ticket']} actualizado.")
                    modal.destroy()
                    self.cargar_tickets_mantenimiento(forzar_red=True)
                else:
                    messagebox.showerror("Error", self.app._extraer_detalle_error(resp))
            except Exception as e:
                messagebox.showerror("Error", str(e))

        ctk.CTkButton(modal, text="Guardar Cambios", width=180, command=guardar).pack(pady=16)
        self.app._mostrar_modal(modal)

    def eliminar_ticket_gui(self, ticket: dict):
        id_t = ticket["id_ticket"]
        num_h = ticket.get("numero_habitacion") or "S/N"
        confirmar = messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Deseas eliminar el Ticket #{id_t} de la Habitación {num_h}?\n\n"
            "Si la habitación no tiene otros tickets activos, saldrá del estado 'Mantenimiento'."
        )
        if not confirmar:
            return
        try:
            resp = self.app.http.delete(f"{self.app.url_base}/mantenimiento/{id_t}")
            if resp.status_code == 200:
                self.app.cargar_habitaciones()
                self.cargar_tickets_mantenimiento(forzar_red=True)
            else:
                messagebox.showerror("Error", self.app._extraer_detalle_error(resp))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def cargar_tickets_mantenimiento(self, forzar_red: bool = True):
        if forzar_red or not self.app.cache_tickets:
            try:
                resp = self.app.http.get(f"{self.app.url_base}/mantenimiento/")
                if resp.status_code == 200:
                    self.app.cache_tickets = resp.json()
            except requests.exceptions.ConnectionError:
                pass
        self.renderizar_tickets_mantenimiento()

    def renderizar_tickets_mantenimiento(self):
        if not hasattr(self, "frame_lista_tickets"):
            return
        for w in self.frame_lista_tickets.winfo_children():
            w.destroy()

        filtro_estado = self.combo_filtro_tickets.get() if hasattr(self, "combo_filtro_tickets") else "Todos los estados"
        filtro_prio = self.combo_filtro_prio.get() if hasattr(self, "combo_filtro_prio") else "Todas prioridades"
        texto_busq = self.entry_buscar_ticket.get().strip().lower() if hasattr(self, "entry_buscar_ticket") else ""

        colores_ticket = {
            "Pendiente": "#FFA726",
            "En Reparación": "#29B6F6",
            "Resuelto": "#66BB6A",
        }
        colores_prioridad = {
            "Crítica": "#D32F2F",
            "Alta": "#F57C00",
            "Media": "#1976D2",
            "Baja": "#455A64",
        }

        tickets = self.app.cache_tickets
        pend_cnt = sum(1 for t in tickets if t.get("estado_ticket") == "Pendiente")
        rep_cnt = sum(1 for t in tickets if t.get("estado_ticket") == "En Reparación")
        crit_cnt = sum(
            1 for t in tickets
            if t.get("estado_ticket") != "Resuelto" and t.get("prioridad") == "Crítica"
        )
        res_cnt = sum(1 for t in tickets if t.get("estado_ticket") == "Resuelto")

        if hasattr(self, "kpi_mant_pendientes"):
            self.kpi_mant_pendientes.configure(text=str(pend_cnt))
            self.kpi_mant_reparacion.configure(text=str(rep_cnt))
            self.kpi_mant_criticos.configure(text=str(crit_cnt))
            self.kpi_mant_resueltos.configure(text=str(res_cnt))

        tickets_filtrados = []
        for t in tickets:
            est = t.get("estado_ticket", "Pendiente")
            prio = t.get("prioridad") or "Media"
            cat = t.get("categoria") or "General"

            if filtro_estado == "Activos" and est == "Resuelto":
                continue
            elif filtro_estado in ("Pendiente", "En Reparación", "Resuelto") and est != filtro_estado:
                continue

            if filtro_prio != "Todas prioridades" and prio != filtro_prio:
                continue

            num_hab = str(t.get("numero_habitacion") or t.get("id_habitacion") or "S/N")
            desc = t.get("descripcion_falla") or ""
            nota_res = t.get("nota_resolucion") or ""

            if (
                texto_busq
                and texto_busq not in num_hab.lower()
                and texto_busq not in desc.lower()
                and texto_busq not in cat.lower()
                and texto_busq not in nota_res.lower()
            ):
                continue

            tickets_filtrados.append(t)

        inicio, fin = crear_controles_paginacion(
            self.frame_paginacion_tickets,
            self.pag_tickets,
            len(tickets_filtrados),
            self.ITEMS_POR_PAGINA,
            self._cambiar_pagina_tickets,
        )

        mostrados = 0
        for t in tickets_filtrados[inicio:fin]:
            est = t.get("estado_ticket", "Pendiente")
            prio = t.get("prioridad") or "Media"
            cat = t.get("categoria") or "General"
            num_hab = str(t.get("numero_habitacion") or t.get("id_habitacion") or "S/N")
            desc = t.get("descripcion_falla") or ""
            nota_res = t.get("nota_resolucion") or ""
            reporta = t.get("nombre_usuario_reporta") or "Personal"

            mostrados += 1
            card = ctk.CTkFrame(self.frame_lista_tickets)
            card.pack(fill="x", padx=4, pady=4)

            frame_info = ctk.CTkFrame(card, fg_color="transparent")
            frame_info.pack(side="left", fill="x", expand=True, padx=8, pady=6)

            fila_titulo = ctk.CTkFrame(frame_info, fg_color="transparent")
            fila_titulo.pack(fill="x")

            color_est = colores_ticket.get(est, "white")
            ctk.CTkLabel(
                fila_titulo,
                text=f"Ticket #{t['id_ticket']}  |  Hab. {num_hab}  |  {cat}  |  [{est}]",
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=color_est,
                anchor="w"
            ).pack(side="left")

            color_p = colores_prioridad.get(prio, "#1976D2")
            lbl_prio = ctk.CTkLabel(
                fila_titulo,
                text=f" Prioridad: {prio} ",
                font=ctk.CTkFont(size=10, weight="bold"),
                fg_color=color_p,
                text_color="white",
                corner_radius=5
            )
            lbl_prio.pack(side="left", padx=8)

            ctk.CTkLabel(
                frame_info,
                text=f"Falla: {desc}",
                font=ctk.CTkFont(size=12),
                text_color="white",
                anchor="w"
            ).pack(fill="x", pady=(2, 1))

            if nota_res:
                ctk.CTkLabel(
                    frame_info,
                    text=f"✔ Solución aplicada: {nota_res}",
                    font=ctk.CTkFont(size=11, weight="bold"),
                    text_color="#81C784",
                    anchor="w"
                ).pack(fill="x", pady=(0, 2))

            f_crea = (t.get("fecha_creacion") or "")[:19].replace("T", " ")
            f_res = (t.get("fecha_resolucion") or "")[:19].replace("T", " ")
            meta_txt = f"Reportó: {reporta}  |  Creado: {f_crea}"
            if f_res:
                meta_txt += f"  |  Resuelto: {f_res}"

            ctk.CTkLabel(
                frame_info,
                text=meta_txt,
                font=ctk.CTkFont(size=10),
                text_color="gray65",
                anchor="w"
            ).pack(fill="x")

            frame_acc = ctk.CTkFrame(card, fg_color="transparent")
            frame_acc.pack(side="right", padx=6, pady=6)

            ctk.CTkButton(
                frame_acc,
                text="Eliminar",
                width=62,
                height=25,
                fg_color="#C62828",
                hover_color="#8E0000",
                command=lambda tk_obj=t: self.eliminar_ticket_gui(tk_obj)
            ).pack(side="right", padx=2)

            ctk.CTkButton(
                frame_acc,
                text="Editar",
                width=55,
                height=25,
                command=lambda tk_obj=t: self.abrir_modal_editar_ticket(tk_obj)
            ).pack(side="right", padx=2)

            if est != "Resuelto":
                ctk.CTkButton(
                    frame_acc,
                    text="Resolver",
                    width=75,
                    height=25,
                    fg_color="#2E7D32",
                    hover_color="#1b5e20",
                    command=lambda tk_obj=t: self.abrir_modal_resolver_ticket(tk_obj)
                ).pack(side="right", padx=2)

            if est == "Pendiente":
                ctk.CTkButton(
                    frame_acc,
                    text="En Reparación",
                    width=96,
                    height=25,
                    fg_color="#0277BD",
                    hover_color="#01579B",
                    command=lambda tid=t["id_ticket"], nh=num_hab: self.cambiar_estado_ticket_gui(tid, "En Reparación", nh)
                ).pack(side="right", padx=2)

        if mostrados == 0:
            ctk.CTkLabel(
                self.frame_lista_tickets,
                text="No hay tickets de mantenimiento para el filtro seleccionado.",
                text_color="gray60",
                font=ctk.CTkFont(size=12)
            ).pack(pady=20)
