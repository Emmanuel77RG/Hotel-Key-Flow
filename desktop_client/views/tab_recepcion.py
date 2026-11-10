"""
Vista de la pestaña de Recepción y Reservas - Directorio de Huéspedes y Gestión de Estancias.
"""
import requests
from tkinter import messagebox
import customtkinter as ctk

try:
    from modals import abrir_mini_calendario as abrir_mini_calendario_modal
except ImportError:
    from desktop_client.modals import abrir_mini_calendario as abrir_mini_calendario_modal

try:
    from widgets import crear_controles_paginacion
except ImportError:
    from desktop_client.widgets import crear_controles_paginacion


class TabRecepcionView:
    OPCIONES_DOCUMENTO = [
        "Selecciona una opción",
        "INE",
        "Pasaporte",
        "Cartilla Militar",
        "Documento migratorio vigente",
    ]

    def __init__(self, tab, app):
        self.tab = tab
        self.app = app
        self.pag_huespedes = 1
        self.pag_reservas = 1
        self.ITEMS_POR_PAGINA = getattr(app, "ITEMS_POR_PAGINA", 15)
        self._after_busq_huesped = None
        self.mapa_huespedes = {}

        # Referencias a widgets
        self.entry_h_nombre = None
        self.combo_h_doc = None
        self.entry_h_email = None
        self.entry_h_tel = None
        self.entry_h_rfc = None
        self.entry_buscar_huesped = None
        self.frame_lista_huespedes = None
        self.frame_pag_huespedes = None

        self.combo_r_hab = None
        self.entry_r_huesped_id = None
        self.entry_r_hab_id = None
        self.entry_r_f_entrada = None
        self.entry_r_f_salida = None
        self.entry_checkin_id = None
        self.frame_lista_reservas = None
        self.frame_pag_reservas = None

        self.construir()

    def _set_entry_readonly(self, entry_widget, valor: str, placeholder: str = ""):
        if entry_widget is None:
            return
        entry_widget.configure(state="normal")
        entry_widget.delete(0, "end")
        if valor:
            entry_widget.insert(0, valor)
        elif placeholder:
            pass
        entry_widget.configure(state="readonly")

    def construir(self):
        tab_rec = self.tab

        # Frame izquierdo: Registro y Directorio de Huéspedes
        frame_huesped = ctk.CTkFrame(tab_rec)
        frame_huesped.pack(side="left", fill="both", expand=True, padx=(10, 5), pady=10)

        ctk.CTkLabel(frame_huesped, text="Registro de Huésped", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(10, 6))
        self.entry_h_nombre = ctk.CTkEntry(frame_huesped, width=250, placeholder_text="Nombre Completo")
        self.entry_h_nombre.pack(pady=3)
        self.combo_h_doc = ctk.CTkOptionMenu(
            frame_huesped,
            width=250,
            values=self.OPCIONES_DOCUMENTO
        )
        self.combo_h_doc.set("Selecciona una opción")
        self.combo_h_doc.pack(pady=3)
        self.entry_h_email = ctk.CTkEntry(frame_huesped, width=250, placeholder_text="Correo Electrónico")
        self.entry_h_email.pack(pady=3)
        self.entry_h_tel = ctk.CTkEntry(frame_huesped, width=250, placeholder_text="Teléfono")
        self.entry_h_tel.pack(pady=3)
        self.entry_h_rfc = ctk.CTkEntry(frame_huesped, width=250, placeholder_text="RFC (Opcional - Ej. XAXX010101000)")
        self.entry_h_rfc.pack(pady=3)

        frame_btns_h = ctk.CTkFrame(frame_huesped, fg_color="transparent")
        frame_btns_h.pack(pady=6)
        ctk.CTkButton(frame_btns_h, text="Registrar Huésped", width=155, command=self.crear_huesped).pack(side="left", padx=4)
        ctk.CTkButton(frame_btns_h, text="Limpiar", width=85, fg_color="gray40", hover_color="gray30", command=self.limpiar_formulario_huesped).pack(side="left", padx=4)

        frame_hdr_h = ctk.CTkFrame(frame_huesped, fg_color="transparent")
        frame_hdr_h.pack(fill="x", padx=10, pady=(6, 2))
        ctk.CTkLabel(frame_hdr_h, text="Directorio de Huéspedes", font=ctk.CTkFont(size=14, weight="bold")).pack(side="left")
        ctk.CTkButton(frame_hdr_h, text="Refrescar", width=85, height=24, command=lambda: self.cargar_huespedes(forzar_red=True)).pack(side="right")

        frame_busqueda_h = ctk.CTkFrame(frame_huesped, fg_color="transparent")
        frame_busqueda_h.pack(fill="x", padx=10, pady=2)
        self.entry_buscar_huesped = ctk.CTkEntry(
            frame_busqueda_h,
            placeholder_text="Buscar por nombre, documento o RFC...",
            height=26
        )
        self.entry_buscar_huesped.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.entry_buscar_huesped.bind("<KeyRelease>", self._filtrar_huespedes_debounced)
        ctk.CTkButton(
            frame_busqueda_h,
            text="Limpiar",
            width=65,
            height=26,
            fg_color="gray40",
            command=self.limpiar_busqueda_huesped
        ).pack(side="right")

        self.frame_lista_huespedes = ctk.CTkScrollableFrame(frame_huesped, height=180)
        self.frame_lista_huespedes.pack(fill="both", expand=True, padx=8, pady=(5, 2))

        self.frame_pag_huespedes = ctk.CTkFrame(frame_huesped, fg_color="transparent")
        self.frame_pag_huespedes.pack(fill="x", padx=8, pady=(0, 4))

        # Frame derecho: Creación de Reservas, Check-in, Check-out y Listado
        frame_res = ctk.CTkFrame(tab_rec)
        frame_res.pack(side="right", fill="both", expand=True, padx=(5, 10), pady=10)

        ctk.CTkLabel(frame_res, text="Gestión de Reservas", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(10, 4))

        self.combo_r_hab = ctk.CTkOptionMenu(
            frame_res,
            width=320,
            values=["Seleccione una habitación..."],
            command=self.al_seleccionar_combo_habitacion
        )
        self.combo_r_hab.set("Seleccione una habitación...")
        self.combo_r_hab.pack(pady=3)

        frame_inputs_res = ctk.CTkFrame(frame_res, fg_color="transparent")
        frame_inputs_res.pack(pady=2)

        self.entry_r_huesped_id = ctk.CTkEntry(frame_inputs_res, width=155, placeholder_text="ID Huésped (Usar ID)")
        self.entry_r_huesped_id.grid(row=0, column=0, padx=4, pady=3)
        self.entry_r_huesped_id.configure(state="readonly")

        self.entry_r_hab_id = ctk.CTkEntry(frame_inputs_res, width=155, placeholder_text="ID Habitación")
        self.entry_r_hab_id.grid(row=0, column=1, padx=4, pady=3)
        self.entry_r_hab_id.configure(state="readonly")

        # Sub-frame para Entrada con botón de mini-calendario
        frame_f_ent = ctk.CTkFrame(frame_inputs_res, fg_color="transparent")
        frame_f_ent.grid(row=1, column=0, padx=4, pady=3)
        self.entry_r_f_entrada = ctk.CTkEntry(frame_f_ent, width=118, placeholder_text="Entrada")
        self.entry_r_f_entrada.pack(side="left", padx=(0, 3))
        self.entry_r_f_entrada.configure(state="readonly")
        ctk.CTkButton(
            frame_f_ent,
            text="📅",
            width=34,
            command=lambda: self.abrir_mini_calendario(self.entry_r_f_entrada, "Seleccionar Fecha de Entrada", es_entrada=True)
        ).pack(side="left")

        # Sub-frame para Salida con botón de mini-calendario
        frame_f_sal = ctk.CTkFrame(frame_inputs_res, fg_color="transparent")
        frame_f_sal.grid(row=1, column=1, padx=4, pady=3)
        self.entry_r_f_salida = ctk.CTkEntry(frame_f_sal, width=118, placeholder_text="Salida")
        self.entry_r_f_salida.pack(side="left", padx=(0, 3))
        self.entry_r_f_salida.configure(state="readonly")
        ctk.CTkButton(
            frame_f_sal,
            text="📅",
            width=34,
            command=lambda: self.abrir_mini_calendario(self.entry_r_f_salida, "Seleccionar Fecha de Salida", es_entrada=False)
        ).pack(side="left")

        frame_btns_res = ctk.CTkFrame(frame_res, fg_color="transparent")
        frame_btns_res.pack(pady=5)
        ctk.CTkButton(frame_btns_res, text="Crear Reserva", width=155, command=self.crear_reserva).pack(side="left", padx=4)
        ctk.CTkButton(frame_btns_res, text="Limpiar", width=85, fg_color="gray40", hover_color="gray30", command=self.limpiar_formulario_reserva).pack(side="left", padx=4)

        ctk.CTkLabel(frame_res, text="Operación de Recepción (Check-in / Check-out / Cancelar)", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(6, 3))

        frame_op_id = ctk.CTkFrame(frame_res, fg_color="transparent")
        frame_op_id.pack(pady=2)
        self.entry_checkin_id = ctk.CTkEntry(frame_op_id, width=155, placeholder_text="ID de Reserva")
        self.entry_checkin_id.pack(side="left", padx=4)
        self.entry_checkin_id.configure(state="readonly")
        ctk.CTkButton(
            frame_op_id,
            text="Limpiar",
            width=70,
            height=26,
            fg_color="gray40",
            hover_color="gray30",
            command=lambda: self._set_entry_readonly(self.entry_checkin_id, "", "ID de Reserva")
        ).pack(side="left", padx=4)

        frame_btns_op = ctk.CTkFrame(frame_res, fg_color="transparent")
        frame_btns_op.pack(pady=4)
        ctk.CTkButton(
            frame_btns_op,
            text="Check-in & Folio",
            width=125,
            fg_color="#2E7D32",
            hover_color="#1b5e20",
            command=self.ejecutar_checkin
        ).pack(side="left", padx=4)
        ctk.CTkButton(
            frame_btns_op,
            text="Check-out",
            width=110,
            fg_color="#E65100",
            hover_color="#BF360C",
            command=self.ejecutar_checkout
        ).pack(side="left", padx=4)
        ctk.CTkButton(
            frame_btns_op,
            text="Cancelar Reserva",
            width=125,
            fg_color="#C62828",
            hover_color="#8E0000",
            command=self.ejecutar_cancelar_reserva
        ).pack(side="left", padx=4)

        frame_hdr_r = ctk.CTkFrame(frame_res, fg_color="transparent")
        frame_hdr_r.pack(fill="x", padx=10, pady=(6, 2))
        ctk.CTkLabel(frame_hdr_r, text="Reservas Registradas", font=ctk.CTkFont(size=14, weight="bold")).pack(side="left")
        ctk.CTkButton(frame_hdr_r, text="Refrescar", width=85, height=24, command=self.cargar_reservas).pack(side="right")

        self.frame_lista_reservas = ctk.CTkScrollableFrame(frame_res, height=150)
        self.frame_lista_reservas.pack(fill="both", expand=True, padx=8, pady=(5, 2))

        self.frame_pag_reservas = ctk.CTkFrame(frame_res, fg_color="transparent")
        self.frame_pag_reservas.pack(fill="x", padx=8, pady=(0, 4))

        self.cargar_huespedes(forzar_red=not bool(self.app.cache_huespedes))
        self.cargar_reservas()
        self.actualizar_combo_habitaciones_reserva(self.app.cache_habitaciones or None)

    # --- Métodos de Huéspedes ---
    def crear_huesped(self):
        try:
            nombre = self.entry_h_nombre.get().strip()
            if not nombre:
                messagebox.showwarning("Campo obligatorio", "Por favor ingresa el Nombre Completo del huésped.")
                return
            doc_sel = self.combo_h_doc.get()
            doc_valor = "Sin especificar" if doc_sel == "Selecciona una opción" else doc_sel
            rfc_val = self.entry_h_rfc.get().strip() or None
            datos = {
                "nombre_completo": nombre,
                "documento_identidad": doc_valor,
                "email": self.entry_h_email.get().strip(),
                "telefono": self.entry_h_tel.get().strip(),
                "rfc": rfc_val
            }
            respuesta = self.app.http.post(f"{self.app.url_base}/huespedes/", json=datos)
            if respuesta.status_code in [200, 201]:
                h_json = respuesta.json()
                messagebox.showinfo("Éxito", f"Huésped registrado correctamente (ID: #{h_json.get('id_huesped')}).")
                self.limpiar_formulario_huesped()
                self.cargar_huespedes(forzar_red=True)
            elif respuesta.status_code == 422:
                errores = respuesta.json().get("detail", [])
                msg = "El RFC ingresado no tiene un formato fiscal válido."
                if isinstance(errores, list) and errores:
                    msg = errores[0].get("msg", msg)
                messagebox.showerror("RFC Inválido", msg)
            else:
                messagebox.showerror("Error", f"No se pudo registrar: {respuesta.text}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def limpiar_formulario_huesped(self):
        if self.entry_h_nombre:
            self.entry_h_nombre.delete(0, "end")
        if self.combo_h_doc:
            self.combo_h_doc.set("Selecciona una opción")
        if self.entry_h_email:
            self.entry_h_email.delete(0, "end")
        if self.entry_h_tel:
            self.entry_h_tel.delete(0, "end")
        if self.entry_h_rfc:
            self.entry_h_rfc.delete(0, "end")

    def limpiar_busqueda_huesped(self):
        if self.entry_buscar_huesped:
            self.entry_buscar_huesped.delete(0, "end")
            self.pag_huespedes = 1
            self.renderizar_huespedes()

    def _filtrar_huespedes_debounced(self, _event=None):
        self.pag_huespedes = 1
        if self._after_busq_huesped is not None:
            try:
                self.app.after_cancel(self._after_busq_huesped)
            except Exception:
                pass
        self._after_busq_huesped = self.app.after(150, self.renderizar_huespedes)

    def cargar_huespedes(self, forzar_red: bool = True):
        if forzar_red or not self.app.cache_huespedes:
            try:
                resp = self.app.http.get(f"{self.app.url_base}/huespedes/")
                if resp.status_code == 200:
                    self.app.cache_huespedes = resp.json()
                    self.mapa_huespedes = {
                        h["id_huesped"]: (h.get("nombre_completo") or f"Huésped #{h['id_huesped']}")
                        for h in self.app.cache_huespedes
                    }
                    self.app.mapa_huespedes = self.mapa_huespedes
            except requests.exceptions.ConnectionError:
                pass
        self.renderizar_huespedes()

    def _cambiar_pagina_huespedes(self, nueva_pag: int):
        self.pag_huespedes = nueva_pag
        self.renderizar_huespedes()

    def renderizar_huespedes(self):
        if not self.frame_lista_huespedes or not self.frame_lista_huespedes.winfo_exists():
            return
        for widget in self.frame_lista_huespedes.winfo_children():
            widget.destroy()

        filtro = ""
        if self.entry_buscar_huesped:
            filtro = self.entry_buscar_huesped.get().strip().lower()

        huespedes_filtrados = []
        for h in self.app.cache_huespedes:
            nombre = (h.get("nombre_completo") or "").lower()
            doc = (h.get("documento_identidad") or "").lower()
            rfc_h = (h.get("rfc") or "").lower()
            if filtro and filtro not in nombre and filtro not in doc and filtro not in rfc_h:
                continue
            huespedes_filtrados.append(h)

        inicio, fin = crear_controles_paginacion(
            self.frame_pag_huespedes,
            self.pag_huespedes,
            len(huespedes_filtrados),
            self.ITEMS_POR_PAGINA,
            self._cambiar_pagina_huespedes,
        )

        for h in huespedes_filtrados[inicio:fin]:
            fila = ctk.CTkFrame(self.frame_lista_huespedes)
            fila.pack(fill="x", pady=2, padx=2)

            doc_mostrar = h.get("documento_identidad") or "Sin especificar"
            rfc_sufijo = f" | RFC: {h['rfc']}" if h.get("rfc") else ""
            ctk.CTkLabel(
                fila,
                text=f"#{h['id_huesped']} {h['nombre_completo']} ({doc_mostrar}{rfc_sufijo})",
                font=ctk.CTkFont(size=12)
            ).pack(side="left", padx=6, pady=4)

            ctk.CTkButton(
                fila,
                text="Usar ID",
                width=55,
                height=24,
                fg_color="#2E7D32",
                command=lambda hid=h["id_huesped"]: self.seleccionar_huesped_id(hid)
            ).pack(side="right", padx=2, pady=3)

            ctk.CTkButton(
                fila,
                text="Eliminar",
                width=58,
                height=24,
                fg_color="#C62828",
                hover_color="#8E0000",
                command=lambda hid=h["id_huesped"], hnom=h["nombre_completo"]: self.eliminar_huesped_gui(hid, hnom)
            ).pack(side="right", padx=2, pady=3)

            ctk.CTkButton(
                fila,
                text="Editar",
                width=52,
                height=24,
                command=lambda hdata=h: self.abrir_modal_editar_huesped(hdata)
            ).pack(side="right", padx=2, pady=3)

    def eliminar_huesped_gui(self, id_huesped: int, nombre: str):
        confirmar = messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Deseas eliminar al huésped '{nombre}' (#{id_huesped})?\n\nNota: Solo se permite si no tiene reservaciones registradas."
        )
        if not confirmar:
            return
        try:
            resp = self.app.http.delete(f"{self.app.url_base}/huespedes/{id_huesped}")
            if resp.status_code == 200:
                messagebox.showinfo("Éxito", resp.json().get("mensaje", "Huésped eliminado correctamente."))
                if self.entry_r_huesped_id and self.entry_r_huesped_id.get().strip() == str(id_huesped):
                    self._set_entry_readonly(self.entry_r_huesped_id, "", "ID Huésped (Usar ID)")
                self.cargar_huespedes(forzar_red=True)
            else:
                detalle = resp.json().get("detail", resp.text)
                messagebox.showerror("No se puede eliminar", detalle)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def seleccionar_huesped_id(self, id_huesped):
        self._set_entry_readonly(self.entry_r_huesped_id, str(id_huesped), "ID Huésped (Usar ID)")

    def abrir_modal_editar_huesped(self, huesped):
        modal = self.app._crear_modal(f"Editar Huésped #{huesped['id_huesped']}", "350x380")

        ctk.CTkLabel(modal, text=f"Editar Huésped #{huesped['id_huesped']}", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=12)

        e_nombre = ctk.CTkEntry(modal, width=250, placeholder_text="Nombre Completo")
        e_nombre.insert(0, huesped.get("nombre_completo", "") or "")
        e_nombre.pack(pady=5)

        combo_doc = ctk.CTkOptionMenu(modal, width=250, values=self.OPCIONES_DOCUMENTO)
        doc_actual = huesped.get("documento_identidad") or "Selecciona una opción"
        if doc_actual in self.OPCIONES_DOCUMENTO:
            combo_doc.set(doc_actual)
        else:
            combo_doc.set("Selecciona una opción")
        combo_doc.pack(pady=5)

        e_email = ctk.CTkEntry(modal, width=250, placeholder_text="Correo Electrónico")
        e_email.insert(0, huesped.get("email", "") or "")
        e_email.pack(pady=5)

        e_tel = ctk.CTkEntry(modal, width=250, placeholder_text="Teléfono")
        e_tel.insert(0, huesped.get("telefono", "") or "")
        e_tel.pack(pady=5)

        e_rfc = ctk.CTkEntry(modal, width=250, placeholder_text="RFC (Opcional - Ej. XAXX010101000)")
        e_rfc.insert(0, huesped.get("rfc", "") or "")
        e_rfc.pack(pady=5)

        def guardar():
            doc_sel = combo_doc.get()
            doc_val = "Sin especificar" if doc_sel == "Selecciona una opción" else doc_sel
            datos = {
                "nombre_completo": e_nombre.get().strip(),
                "documento_identidad": doc_val,
                "email": e_email.get().strip(),
                "telefono": e_tel.get().strip(),
                "rfc": e_rfc.get().strip() or None,
            }
            try:
                r = self.app.http.put(
                    f"{self.app.url_base}/huespedes/{huesped['id_huesped']}",
                    json=datos
                )
                if r.status_code == 200:
                    messagebox.showinfo("Éxito", "Datos del huésped actualizados.")
                    modal.destroy()
                    self.cargar_huespedes(forzar_red=True)
                    self.cargar_reservas()
                elif r.status_code == 422:
                    errores = r.json().get("detail", [])
                    msg = "El RFC ingresado no tiene un formato fiscal válido."
                    if isinstance(errores, list) and errores:
                        msg = errores[0].get("msg", msg)
                    messagebox.showerror("RFC Inválido", msg)
                else:
                    messagebox.showerror("Error", f"No se pudo actualizar: {r.text}")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        ctk.CTkButton(modal, text="Guardar Cambios", width=180, command=guardar).pack(pady=15)
        self.app._mostrar_modal(modal)

    # --- Métodos de Reservas y Operaciones ---
    def abrir_mini_calendario(self, entry_destino, titulo="Seleccionar Fecha", es_entrada=True, al_seleccionar=None):
        entry_salida = self.entry_r_f_salida if es_entrada else None
        return abrir_mini_calendario_modal(
            padre=self.app,
            entry_destino=entry_destino,
            titulo=titulo,
            es_entrada=es_entrada,
            al_seleccionar=al_seleccionar,
            entry_salida_sugerida=entry_salida,
        )

    def abrir_selector_fecha(self, entry_destino, titulo="Seleccionar Fecha", al_seleccionar=None):
        self.abrir_mini_calendario(entry_destino, titulo=titulo, es_entrada=False, al_seleccionar=al_seleccionar)

    def actualizar_combo_habitaciones_reserva(self, lista_habs=None):
        if not self.combo_r_hab or not self.combo_r_hab.winfo_exists():
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
            opciones = ["Seleccione una habitación..."] + [
                f"ID {h['id_habitacion']} - Hab. {h['numero_habitacion']} ({h['tipo']} - ${float(h.get('precio_base', 0)):.0f} [{h['estado']}])"
                for h in lista_habs
            ]
            self.combo_r_hab.configure(values=opciones)
        except requests.exceptions.ConnectionError:
            pass

    def al_seleccionar_combo_habitacion(self, opcion_seleccionada: str):
        if opcion_seleccionada.startswith("ID "):
            try:
                id_hab = opcion_seleccionada.split(" - ")[0].replace("ID ", "").strip()
                self._set_entry_readonly(self.entry_r_hab_id, id_hab, "ID Habitación")
            except Exception:
                pass
        else:
            self._set_entry_readonly(self.entry_r_hab_id, "", "ID Habitación")

    def limpiar_formulario_reserva(self):
        if self.combo_r_hab:
            self.combo_r_hab.set("Seleccione una habitación...")
        self._set_entry_readonly(self.entry_r_huesped_id, "", "ID Huésped (Usar ID)")
        self._set_entry_readonly(self.entry_r_hab_id, "", "ID Habitación")
        self._set_entry_readonly(self.entry_r_f_entrada, "", "Entrada")
        self._set_entry_readonly(self.entry_r_f_salida, "", "Salida")

    def _cambiar_pagina_reservas(self, nueva_pag: int):
        self.pag_reservas = nueva_pag
        self.renderizar_reservas()

    def cargar_reservas(self):
        try:
            resp = self.app.http.get(f"{self.app.url_base}/reservas/")
            if resp.status_code == 200:
                lista_res = resp.json()
                self.app.cache_reservas = lista_res
                self.renderizar_reservas()
                if hasattr(self.app, "actualizar_combo_reservas_folio"):
                    self.app.actualizar_combo_reservas_folio(lista_res)
                if hasattr(self.app, "actualizar_combo_habitaciones_pos"):
                    self.app.actualizar_combo_habitaciones_pos(lista_res)
        except requests.exceptions.ConnectionError:
            pass

    def renderizar_reservas(self):
        if not self.frame_lista_reservas or not self.frame_lista_reservas.winfo_exists():
            return
        for widget in self.frame_lista_reservas.winfo_children():
            widget.destroy()

        colores_res = {
            "Confirmada": "#64B5F6",
            "Activa": "#66BB6A",
            "Finalizada": "#BDBDBD",
            "Cancelada": "#EF5350",
        }
        reservas = self.app.cache_reservas
        inicio, fin = crear_controles_paginacion(
            self.frame_pag_reservas,
            self.pag_reservas,
            len(reservas),
            self.ITEMS_POR_PAGINA,
            self._cambiar_pagina_reservas,
        )

        for r in reservas[inicio:fin]:
            fila = ctk.CTkFrame(self.frame_lista_reservas)
            fila.pack(fill="x", pady=2, padx=2)

            est = r.get("estado_reserva", "")
            color_txt = colores_res.get(est, "white")
            nombre_huesped = (
                r.get("nombre_huesped")
                or self.mapa_huespedes.get(r.get("id_huesped"))
                or getattr(self.app, "mapa_huespedes", {}).get(r.get("id_huesped"))
                or f"Huésped #{r.get('id_huesped')}"
            )
            hab_txt = r.get("numeros_habitaciones") or "Sin hab."
            texto = (
                f"Reserva #{r['id_reserva']} | {nombre_huesped} | Hab. {hab_txt} | "
                f"{r['fecha_entrada']} -> {r['fecha_salida']} [{est}]"
            )
            ctk.CTkLabel(
                fila,
                text=texto,
                text_color=color_txt,
                font=ctk.CTkFont(size=11, weight="bold")
            ).pack(side="left", padx=6, pady=4)

            ctk.CTkButton(
                fila,
                text="Seleccionar",
                width=75,
                height=24,
                command=lambda rid=r["id_reserva"]: self.seleccionar_reserva_id(rid)
            ).pack(side="right", padx=4, pady=3)

    def seleccionar_reserva_id(self, id_reserva):
        self._set_entry_readonly(self.entry_checkin_id, str(id_reserva), "ID de Reserva")
        if self.app.id_rol in (1, 2):
            self.app._asegurar_pestana("Facturación y Folios")
        if hasattr(self.app, "entry_folio_reserva_id"):
            self.app._set_entry_readonly(self.app.entry_folio_reserva_id, str(id_reserva), "ID Reserva")
            self.app.consultar_folio()
        elif hasattr(self.app, "vista_folios") and hasattr(self.app.vista_folios, "entry_folio_reserva_id"):
            self.app.vista_folios._set_entry_readonly(self.app.vista_folios.entry_folio_reserva_id, str(id_reserva), "ID Reserva")
            self.app.vista_folios.consultar_folio()

    def crear_reserva(self):
        try:
            if not self.entry_r_huesped_id.get().strip():
                messagebox.showwarning("Dato faltante", "Selecciona un huésped de la lista con el botón 'Usar ID'.")
                return
            if not self.entry_r_hab_id.get().strip():
                messagebox.showwarning("Dato faltante", "Selecciona una habitación del menú desplegable.")
                return
            if not self.entry_r_f_entrada.get().strip() or not self.entry_r_f_salida.get().strip():
                messagebox.showwarning("Fechas faltantes", "Selecciona las fechas de Entrada y Salida usando el botón de calendario (📅).")
                return
            datos = {
                "fecha_entrada": self.entry_r_f_entrada.get(),
                "fecha_salida": self.entry_r_f_salida.get(),
                "estado_reserva": "Confirmada",
                "estado_folio": "Abierto",
                "id_huesped": int(self.entry_r_huesped_id.get()),
                "id_habitacion": int(self.entry_r_hab_id.get())
            }
            respuesta = self.app.http.post(f"{self.app.url_base}/reservas/", json=datos)
            if respuesta.status_code in [200, 201]:
                res_json = respuesta.json()
                messagebox.showinfo("Éxito", f"Reserva creada con éxito. ID Asignado: {res_json.get('id_reserva')}")
                self.limpiar_formulario_reserva()
                self.cargar_reservas()
            elif respuesta.status_code == 409:
                detalle = respuesta.json().get("detail", "Inventario no disponible para las fechas seleccionadas")
                messagebox.showerror("Sin Disponibilidad", detalle)
            else:
                messagebox.showerror("Error", f"Fallo al crear reserva: {respuesta.text}")
        except Exception as e:
            messagebox.showerror("Error", f"Verifica que los IDs y fechas sean correctos: {str(e)}")

    def ejecutar_cancelar_reserva(self):
        try:
            reserva_id = self.entry_checkin_id.get().strip()
            if not reserva_id:
                messagebox.showwarning("Advertencia", "Por favor ingresa o selecciona un ID de reserva.")
                return
            confirmar = messagebox.askyesno(
                "Confirmar Cancelación",
                f"¿Deseas cancelar la Reserva #{reserva_id} y liberar las fechas en el inventario?"
            )
            if not confirmar:
                return
            respuesta = self.app.http.patch(f"{self.app.url_base}/reservas/{reserva_id}/cancelar")
            if respuesta.status_code == 200:
                data = respuesta.json()
                messagebox.showinfo("Reserva Cancelada", data.get("mensaje", "Reserva cancelada con éxito."))
                self.cargar_reservas()
            else:
                detalle = respuesta.json().get("detail", respuesta.text)
                messagebox.showerror("No se pudo cancelar", detalle)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def ejecutar_checkin(self):
        try:
            reserva_id = self.entry_checkin_id.get()
            if not reserva_id:
                messagebox.showwarning("Advertencia", "Por favor ingresa un ID de reserva.")
                return
            respuesta = self.app.http.post(f"{self.app.url_base}/reservas/{reserva_id}/checkin")
            if respuesta.status_code == 200:
                data = respuesta.json()
                cargo_gen = data.get("cargo_hospedaje_generado", 0.0)
                messagebox.showinfo(
                    "Éxito",
                    f"¡Check-in realizado y Folio abierto!\n"
                    f"Estado Reserva: {data.get('nuevo_estado_reserva')}\n"
                    f"Estado Folio: {data.get('nuevo_estado_folio')}\n"
                    f"Cargo automático por hospedaje: ${cargo_gen:.2f}"
                )
                if hasattr(self.app, "cargar_habitaciones"):
                    self.app.cargar_habitaciones()
                self.cargar_reservas()
            else:
                messagebox.showerror("Error", f"No se pudo completar el check-in: {respuesta.text}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def ejecutar_checkout(self):
        try:
            reserva_id = self.entry_checkin_id.get()
            if not reserva_id:
                messagebox.showwarning("Advertencia", "Por favor ingresa un ID de reserva.")
                return
            respuesta = self.app.http.post(f"{self.app.url_base}/reservas/{reserva_id}/checkout")
            if respuesta.status_code == 200:
                data = respuesta.json()
                messagebox.showinfo(
                    "Check-out Exitoso",
                    f"{data.get('mensaje')}\n"
                    f"Estado Reserva: {data.get('nuevo_estado_reserva')}\n"
                    f"Estado Folio: {data.get('nuevo_estado_folio')}"
                )
                if hasattr(self.app, "cargar_habitaciones"):
                    self.app.cargar_habitaciones()
                self.cargar_reservas()
            else:
                detalle = respuesta.json().get("detail", respuesta.text)
                messagebox.showerror("No se puede realizar Check-out", detalle)
        except Exception as e:
            messagebox.showerror("Error", str(e))
