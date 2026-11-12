"""
Vista de la pestaña de Habitaciones - Inventario y Gestión de Estados.
"""
import requests
from tkinter import messagebox
import customtkinter as ctk


class TabHabitacionesView:
    COLORES_ESTADO = {
        "Limpia": "#2E7D32",        # Verde oscuro
        "Sucia": "#C62828",         # Rojo oscuro
        "En Limpieza": "#F9A825",   # Amarillo/Naranja
        "Ocupada": "#1565C0",       # Azul
        "Mantenimiento": "#424242", # Gris
    }

    def __init__(self, tab, app):
        self.tab = tab
        self.app = app
        self.columna_actual = 0
        self.fila_actual = 0
        self.max_columnas = 3

        # Form widgets references
        self.entry_num_hab = None
        self.combo_tipo = None
        self.entry_capacidad = None
        self.entry_precio = None
        self.frame_lista = None

        self.construir()

    def construir(self):
        # --- MÓDULO DE HABITACIONES (BARRA SUPERIOR + GRID) ---
        self.frame_top_hab = ctk.CTkFrame(self.tab, fg_color="transparent")
        self.frame_top_hab.pack(fill="x", padx=20, pady=(10, 5))

        ctk.CTkLabel(
            self.frame_top_hab,
            text="Inventario y Estado de Habitaciones",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(side="left")

        self.btn_refrescar = ctk.CTkButton(
            self.frame_top_hab,
            text="Refrescar Inventario",
            width=150,
            command=self.cargar_habitaciones
        )
        self.btn_refrescar.pack(side="right", padx=5)

        if self.app.id_rol == 1:
            self.btn_nueva_hab = ctk.CTkButton(
                self.frame_top_hab,
                text="+ Nueva Habitación",
                width=160,
                fg_color="#2E7D32",
                hover_color="#1b5e20",
                command=self.abrir_modal_nueva_habitacion
            )
            self.btn_nueva_hab.pack(side="right", padx=5)

        self.frame_lista = ctk.CTkScrollableFrame(self.tab, width=800, height=450)
        self.frame_lista.pack(pady=5, padx=20, fill="both", expand=True)

        self.cargar_habitaciones()

    def abrir_modal_nueva_habitacion(self):
        modal = self.app._crear_modal("Alta de Nueva Habitación", "360x350")

        ctk.CTkLabel(modal, text="Registrar Habitación", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=15)
        self.entry_num_hab = ctk.CTkEntry(modal, width=250, placeholder_text="Número (Ej. 102)")
        self.entry_num_hab.pack(pady=6)
        self.combo_tipo = ctk.CTkComboBox(modal, width=250, values=["Sencilla", "Doble", "Suite"])
        self.combo_tipo.pack(pady=6)
        self.entry_capacidad = ctk.CTkEntry(modal, width=250, placeholder_text="Capacidad (Ej. 2)")
        self.entry_capacidad.pack(pady=6)
        self.entry_precio = ctk.CTkEntry(modal, width=250, placeholder_text="Precio Base (Ej. 1500.00)")
        self.entry_precio.pack(pady=6)

        def guardar():
            if self.crear_habitacion():
                modal.destroy()

        ctk.CTkButton(
            modal,
            text="Guardar Habitación",
            width=200,
            fg_color="#2E7D32",
            hover_color="#1b5e20",
            command=guardar
        ).pack(pady=20)
        self.app._mostrar_modal(modal)

    def crear_habitacion(self):
        try:
            datos = {
                "numero_habitacion": self.entry_num_hab.get(),
                "tipo": self.combo_tipo.get(),
                "capacidad": int(self.entry_capacidad.get()),
                "precio_base": float(self.entry_precio.get())
            }
            respuesta = self.app.http.post(f"{self.app.url_base}/habitaciones/", json=datos)
            if respuesta.status_code == 201:
                messagebox.showinfo("Éxito", "Habitación creada en la base de datos.")
                self.cargar_habitaciones()
                return True
            else:
                messagebox.showerror("Error", f"Fallo al crear: {respuesta.text}")
                return False
        except Exception as e:
            messagebox.showerror("Error", f"Verifica los datos ingresados: {str(e)}")
            return False

    def abrir_modal_editar_habitacion(self, habitacion):
        modal = self.app._crear_modal(f"Editar Habitación {habitacion['numero_habitacion']}", "360x360")

        ctk.CTkLabel(
            modal,
            text=f"Editar Habitación {habitacion['numero_habitacion']}",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=15)

        entry_num = ctk.CTkEntry(modal, width=250, placeholder_text="Número de Habitación")
        entry_num.insert(0, str(habitacion.get("numero_habitacion", "")))
        entry_num.pack(pady=6)

        combo_tipo = ctk.CTkComboBox(modal, width=250, values=["Sencilla", "Doble", "Suite"])
        combo_tipo.set(habitacion.get("tipo", "Sencilla"))
        combo_tipo.pack(pady=6)

        entry_cap = ctk.CTkEntry(modal, width=250, placeholder_text="Capacidad")
        entry_cap.insert(0, str(habitacion.get("capacidad", "")))
        entry_cap.pack(pady=6)

        entry_precio = ctk.CTkEntry(modal, width=250, placeholder_text="Precio Base")
        entry_precio.insert(0, str(habitacion.get("precio_base", "")))
        entry_precio.pack(pady=6)

        def guardar_cambios():
            try:
                datos = {
                    "numero_habitacion": entry_num.get().strip(),
                    "tipo": combo_tipo.get(),
                    "capacidad": int(entry_cap.get()),
                    "precio_base": float(entry_precio.get())
                }
                resp = self.app.http.put(
                    f"{self.app.url_base}/habitaciones/{habitacion['id_habitacion']}",
                    json=datos
                )
                if resp.status_code == 200:
                    messagebox.showinfo("Éxito", "Habitación actualizada correctamente.")
                    modal.destroy()
                    self.cargar_habitaciones()
                else:
                    messagebox.showerror("Error", f"No se pudo actualizar: {resp.text}")
            except Exception as e:
                messagebox.showerror("Error", f"Verifica los datos ingresados: {str(e)}")

        ctk.CTkButton(modal, text="Guardar Cambios", width=200, command=guardar_cambios).pack(pady=20)
        self.app._mostrar_modal(modal)

    def cargar_habitaciones(self):
        try:
            respuesta = self.app.http.get(f"{self.app.url_base}/habitaciones/")
            if respuesta.status_code == 200:
                lista_habs = respuesta.json()
                self.app.cache_habitaciones = lista_habs
                if self.frame_lista is not None and self.frame_lista.winfo_exists():
                    for widget in self.frame_lista.winfo_children():
                        widget.destroy()
                    self.columna_actual = 0
                    self.fila_actual = 0
                    self.max_columnas = 3
                    for hab in lista_habs:
                        self.crear_tarjeta_habitacion(hab)
                if hasattr(self.app, "actualizar_combo_habitaciones_reserva"):
                    self.app.actualizar_combo_habitaciones_reserva(lista_habs)
                if hasattr(self.app, "actualizar_combo_habitaciones_mantenimiento"):
                    self.app.actualizar_combo_habitaciones_mantenimiento(lista_habs)
        except requests.exceptions.ConnectionError:
            pass

    def crear_tarjeta_habitacion(self, habitacion):
        color_fondo = self.COLORES_ESTADO.get(habitacion['estado'], "#424242")
        alto_tarjeta = 185 if self.app.id_rol == 1 else 145

        tarjeta = ctk.CTkFrame(self.frame_lista, fg_color=color_fondo, width=250, height=alto_tarjeta, corner_radius=15)
        tarjeta.grid_propagate(False)
        tarjeta.grid(row=self.fila_actual, column=self.columna_actual, padx=15, pady=15)

        ctk.CTkLabel(
            tarjeta,
            text=f"{habitacion['numero_habitacion']}",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color="white"
        ).pack(pady=(8, 0))

        precio = habitacion.get("precio_base", 0)
        ctk.CTkLabel(
            tarjeta,
            text=f"{habitacion['tipo']} | Cap: {habitacion['capacidad']} | ${precio:.0f}",
            font=ctk.CTkFont(size=12),
            text_color="white"
        ).pack(pady=(0, 6))

        estados_permitidos = ["Limpia", "Sucia", "En Limpieza", "Ocupada", "Mantenimiento"]
        combo_estado = ctk.CTkOptionMenu(
            tarjeta,
            values=estados_permitidos,
            width=170,
            height=28,
            fg_color="#212121",
            button_color="#111111",
            text_color="white",
            command=lambda nuevo_estado, id_hab=habitacion['id_habitacion']: self.actualizar_estado(id_hab, nuevo_estado)
        )
        combo_estado.set(habitacion['estado'])
        combo_estado.pack(pady=4)

        if self.app.id_rol == 1:
            frame_acciones = ctk.CTkFrame(tarjeta, fg_color="transparent")
            frame_acciones.pack(pady=(4, 4))

            ctk.CTkButton(
                frame_acciones,
                text="Editar",
                width=78,
                height=24,
                fg_color="#1E88E5",
                hover_color="#1565C0",
                command=lambda hab_data=habitacion: self.abrir_modal_editar_habitacion(hab_data)
            ).pack(side="left", padx=4)

            en_mantenimiento = habitacion.get("estado") == "Mantenimiento"
            txt_inhabilitar = "Habilitar" if en_mantenimiento else "Inhabilitar"
            estado_destino = "Limpia" if en_mantenimiento else "Mantenimiento"
            color_btn = "#2E7D32" if en_mantenimiento else "#616161"

            ctk.CTkButton(
                frame_acciones,
                text=txt_inhabilitar,
                width=85,
                height=24,
                fg_color=color_btn,
                hover_color="#212121",
                command=lambda id_hab=habitacion["id_habitacion"], est=estado_destino: self.actualizar_estado(id_hab, est)
            ).pack(side="left", padx=4)

        self.columna_actual += 1
        if self.columna_actual >= self.max_columnas:
            self.columna_actual = 0
            self.fila_actual += 1

    def actualizar_estado(self, id_habitacion, nuevo_estado):
        try:
            respuesta = self.app.http.patch(
                f"{self.app.url_base}/habitaciones/{id_habitacion}/estado",
                json={"estado": nuevo_estado}
            )
            if respuesta.status_code == 200:
                self.cargar_habitaciones()
            else:
                messagebox.showerror("Error API", "No se pudo actualizar el estado.")
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Error", "No hay conexión con el servidor.")
