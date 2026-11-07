import calendar
from datetime import date, datetime, timedelta
import os
import uuid
import customtkinter as ctk
from PIL import Image
import requests
from tkinter import messagebox
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image as RLImage,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

class PanelPrincipal(ctk.CTk):
    def __init__(self, token, id_rol):
        super().__init__()
        self.title("Hotel KeyFlow")
        
        self.token = token
        self.id_rol = id_rol
        self.headers = {"Authorization": f"Bearer {self.token}"}
        self.url_base = "http://127.0.0.1:8000"
        
        # --- DICCIONARIO DE COLORES PARA LA MÁQUINA DE ESTADOS ---
        self.COLORES_ESTADO = {
            "Limpia": "#2E7D32",        # Verde oscuro
            "Sucia": "#C62828",         # Rojo oscuro
            "En Limpieza": "#F9A825",   # Amarillo/Naranja
            "Ocupada": "#1565C0",       # Azul
            "Mantenimiento": "#424242"  # Gris
        }
        
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=20, pady=(12, 6))
        
        ruta_assets = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
        self.ruta_logo_dark = os.path.join(ruta_assets, "logo_dark.png")
        self.ruta_logo_light = os.path.join(ruta_assets, "logo_light.png")
        if os.path.exists(self.ruta_logo_dark):
            img_dark = Image.open(self.ruta_logo_dark)
            img_light = Image.open(self.ruta_logo_light) if os.path.exists(self.ruta_logo_light) else img_dark
            self.logo_header_ctk = ctk.CTkImage(light_image=img_light, dark_image=img_dark, size=(168, 66))
            self.label_titulo = ctk.CTkLabel(self.header_frame, text="", image=self.logo_header_ctk)
        else:
            self.label_titulo = ctk.CTkLabel(self.header_frame, text="KeyFlow", font=ctk.CTkFont(size=26, weight="bold"))
        self.label_titulo.pack(side="left")
        
        self.btn_logout = ctk.CTkButton(self.header_frame, text="Cerrar Sesión", width=120, fg_color="#C62828", hover_color="#b71c1c", command=self.cerrar_sesion)
        self.btn_logout.pack(side="right")

        nombres_roles = {1: "Administrador", 2: "Recepción", 3: "Limpieza"}
        nombre_rol_actual = nombres_roles.get(self.id_rol, f"Rol {self.id_rol}")
        self.label_rol_actual = ctk.CTkLabel(
            self.header_frame,
            text=f"Rol activo: {nombre_rol_actual}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#64B5F6"
        )
        self.label_rol_actual.pack(side="right", padx=20)
        
        self.tabview = ctk.CTkTabview(self, width=900, height=550)
        self.tabview.pack(pady=10, padx=20, fill="both", expand=True)
        
        # Pestaña de Usuarios (Protegida por Rol Administrador: RF-ADM-002 y RF-ADM-003)
        if self.id_rol == 1:
            self.tabview.add("Usuarios")
            self.construir_pestana_admin()
            
        self.tabview.add("Habitaciones")
        if self.id_rol in (1, 2):
            self.tabview.add("Recepción y Reservas")
            self.construir_pestana_recepcion()
            self.tabview.add("Facturación y Folios")
            self.construir_pestana_folios()
            self.tabview.add("Punto de Venta")
            self.crear_placeholder(self.tabview.tab("Punto de Venta"), "Módulo de Punto de Venta (Restaurante y Room Service)\n\n(En desarrollo - Sprint 6)")
        self.tabview.add("Mantenimiento")
        self.crear_placeholder(self.tabview.tab("Mantenimiento"), "Módulo de Gestión de Tickets de Mantenimiento\n\n(En desarrollo - Sprint 5)")
        if self.id_rol in (1, 2):
            self.tabview.add("Reportes")
            self.crear_placeholder(self.tabview.tab("Reportes"), "Módulo de Reportes Operativos y Corte de Caja\n\n(En desarrollo - Sprint 7)")
        
        # --- MÓDULO DE HABITACIONES (BARRA SUPERIOR + GRID) ---
        tab_hab = self.tabview.tab("Habitaciones")
        self.frame_top_hab = ctk.CTkFrame(tab_hab, fg_color="transparent")
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

        if self.id_rol == 1:
            self.btn_nueva_hab = ctk.CTkButton(
                self.frame_top_hab,
                text="+ Nueva Habitación",
                width=160,
                fg_color="#2E7D32",
                hover_color="#1b5e20",
                command=self.abrir_modal_nueva_habitacion
            )
            self.btn_nueva_hab.pack(side="right", padx=5)

        self.frame_lista = ctk.CTkScrollableFrame(tab_hab, width=800, height=450)
        self.frame_lista.pack(pady=5, padx=20, fill="both", expand=True)
        
        self.cargar_habitaciones()

    def construir_pestana_admin(self):
        tab_admin = self.tabview.tab("Usuarios")

        # Columna Izquierda: Formulario de Alta de Personal
        frame_izq = ctk.CTkFrame(tab_admin, width=300)
        frame_izq.pack(side="left", fill="y", padx=(10, 5), pady=10)
        frame_izq.pack_propagate(False)
        
        # Columna Derecha: Lista amplia de Personal Registrado (RF-ADM-003)
        frame_der = ctk.CTkFrame(tab_admin)
        frame_der.pack(side="right", fill="both", expand=True, padx=(5, 10), pady=10)
        
        # Formulario Usuario en Columna Izquierda
        ctk.CTkLabel(frame_izq, text="Alta de Personal", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(25, 15))
        self.entry_nombre_user = ctk.CTkEntry(frame_izq, width=240, placeholder_text="Nombre Completo")
        self.entry_nombre_user.pack(pady=8)
        self.entry_email_user = ctk.CTkEntry(frame_izq, width=240, placeholder_text="Correo Electrónico")
        self.entry_email_user.pack(pady=8)
        self.entry_pass_user = ctk.CTkEntry(frame_izq, width=240, placeholder_text="Contraseña", show="*")
        self.entry_pass_user.pack(pady=8)
        self.combo_rol = ctk.CTkOptionMenu(frame_izq, width=240, values=["2 (Recepción)", "3 (Limpieza)", "1 (Administrador)"])
        self.combo_rol.set("2 (Recepción)")
        self.combo_rol.pack(pady=8)
        ctk.CTkButton(frame_izq, text="Registrar Usuario", width=240, command=self.crear_usuario).pack(pady=(15, 6))
        ctk.CTkButton(frame_izq, text="Limpiar", width=240, fg_color="gray40", hover_color="gray30", command=self.limpiar_formulario_usuario).pack(pady=4)

        # Encabezado y Lista de Personal en Columna Derecha
        frame_header_der = ctk.CTkFrame(frame_der, fg_color="transparent")
        frame_header_der.pack(fill="x", padx=12, pady=(12, 5))
        ctk.CTkLabel(
            frame_header_der,
            text="Personal Registrado",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(side="left")
        ctk.CTkButton(
            frame_header_der,
            text="Refrescar Personal",
            width=140,
            command=self.cargar_usuarios
        ).pack(side="right")

        self.frame_lista_usuarios = ctk.CTkScrollableFrame(frame_der)
        self.frame_lista_usuarios.pack(fill="both", expand=True, padx=10, pady=(5, 10))
        self.cargar_usuarios()

    def abrir_modal_nueva_habitacion(self):
        modal = ctk.CTkToplevel(self)
        modal.title("Alta de Nueva Habitación")
        modal.geometry("360x350")
        modal.grab_set()

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

        ctk.CTkButton(modal, text="Guardar Habitación", width=200, fg_color="#2E7D32", hover_color="#1b5e20", command=guardar).pack(pady=20)

    def crear_habitacion(self):
        try:
            datos = {
                "numero_habitacion": self.entry_num_hab.get(),
                "tipo": self.combo_tipo.get(),
                "capacidad": int(self.entry_capacidad.get()),
                "precio_base": float(self.entry_precio.get())
            }
            respuesta = requests.post(f"{self.url_base}/habitaciones/", json=datos, headers=self.headers)
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
        modal = ctk.CTkToplevel(self)
        modal.title(f"Editar Habitación {habitacion['numero_habitacion']}")
        modal.geometry("360x360")
        modal.grab_set()

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
                resp = requests.put(
                    f"{self.url_base}/habitaciones/{habitacion['id_habitacion']}",
                    json=datos,
                    headers=self.headers
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

    def crear_usuario(self):
        try:
            datos = {
                "nombre": self.entry_nombre_user.get(),
                "email": self.entry_email_user.get(),
                "password": self.entry_pass_user.get(),
                "id_rol": int(self.combo_rol.get()[0])
            }
            respuesta = requests.post(f"{self.url_base}/usuarios/", json=datos, headers=self.headers)
            if respuesta.status_code == 200:
                messagebox.showinfo("Éxito", "Personal registrado exitosamente.")
                self.limpiar_formulario_usuario()
                self.cargar_usuarios()
            else:
                messagebox.showerror("Error", f"Fallo al registrar: {respuesta.text}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def limpiar_formulario_usuario(self):
        self.entry_nombre_user.delete(0, "end")
        self.entry_email_user.delete(0, "end")
        self.entry_pass_user.delete(0, "end")
        self.combo_rol.set("2 (Recepción)")

    def cargar_usuarios(self):
        if not hasattr(self, "frame_lista_usuarios"):
            return
        for widget in self.frame_lista_usuarios.winfo_children():
            widget.destroy()

        nombres_roles = {1: "Admin", 2: "Recepción", 3: "Limpieza"}
        try:
            respuesta = requests.get(f"{self.url_base}/usuarios/", headers=self.headers)
            if respuesta.status_code == 200:
                for u in respuesta.json():
                    fila = ctk.CTkFrame(self.frame_lista_usuarios)
                    fila.pack(fill="x", pady=3, padx=3)

                    rol_txt = nombres_roles.get(u.get("id_rol"), str(u.get("id_rol")))
                    activo = u.get("estado_activo", True)
                    estado_txt = "Activo" if activo else "Inactivo"
                    color_estado = "#66BB6A" if activo else "#EF5350"

                    lbl = ctk.CTkLabel(
                        fila,
                        text=f"#{u['id_usuario']} {u['nombre']} ({u['email']}) - {rol_txt} [{estado_txt}]",
                        text_color=color_estado,
                        font=ctk.CTkFont(size=12, weight="bold")
                    )
                    lbl.pack(side="left", padx=8, pady=5)

                    btn_estado_txt = "Desactivar" if activo else "Activar"
                    btn_estado_color = "#C62828" if activo else "#2E7D32"
                    ctk.CTkButton(
                        fila,
                        text=btn_estado_txt,
                        width=75,
                        height=26,
                        fg_color=btn_estado_color,
                        command=lambda uid=u["id_usuario"], act=not activo: self.cambiar_estado_usuario(uid, act)
                    ).pack(side="right", padx=4, pady=4)

                    ctk.CTkButton(
                        fila,
                        text="Editar",
                        width=60,
                        height=26,
                        command=lambda user_data=u: self.abrir_modal_editar_usuario(user_data)
                    ).pack(side="right", padx=4, pady=4)
        except requests.exceptions.ConnectionError:
            pass

    def cambiar_estado_usuario(self, id_usuario, nuevo_estado):
        try:
            respuesta = requests.patch(
                f"{self.url_base}/usuarios/{id_usuario}/estado",
                json={"estado_activo": nuevo_estado},
                headers=self.headers
            )
            if respuesta.status_code == 200:
                accion = "activado" if nuevo_estado else "desactivado (baja lógica)"
                messagebox.showinfo("Éxito", f"Usuario #{id_usuario} {accion} correctamente.")
                self.cargar_usuarios()
            else:
                messagebox.showerror("Error", f"No se pudo cambiar el estado: {respuesta.text}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def abrir_modal_editar_usuario(self, usuario):
        modal = ctk.CTkToplevel(self)
        modal.title(f"Editar Empleado #{usuario['id_usuario']}")
        modal.geometry("360x360")
        modal.grab_set()

        ctk.CTkLabel(modal, text=f"Editar a {usuario['nombre']}", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)

        entry_nombre = ctk.CTkEntry(modal, width=260, placeholder_text="Nombre Completo")
        entry_nombre.insert(0, usuario.get("nombre", ""))
        entry_nombre.pack(pady=5)

        entry_email = ctk.CTkEntry(modal, width=260, placeholder_text="Correo Electrónico")
        entry_email.insert(0, usuario.get("email", ""))
        entry_email.pack(pady=5)

        opciones_rol = ["1 (Administrador)", "2 (Recepción)", "3 (Limpieza)"]
        combo_rol_edit = ctk.CTkComboBox(modal, width=260, values=opciones_rol)
        rol_actual = usuario.get("id_rol", 2)
        for op in opciones_rol:
            if op.startswith(str(rol_actual)):
                combo_rol_edit.set(op)
                break
        combo_rol_edit.pack(pady=5)

        entry_pass = ctk.CTkEntry(modal, width=260, placeholder_text="Nueva contraseña (opcional)", show="*")
        entry_pass.pack(pady=5)

        def guardar_cambios():
            datos = {
                "nombre": entry_nombre.get(),
                "email": entry_email.get(),
                "id_rol": int(combo_rol_edit.get()[0])
            }
            if entry_pass.get().strip():
                datos["password"] = entry_pass.get().strip()
            try:
                resp = requests.put(
                    f"{self.url_base}/usuarios/{usuario['id_usuario']}",
                    json=datos,
                    headers=self.headers
                )
                if resp.status_code == 200:
                    messagebox.showinfo("Éxito", "Datos del usuario actualizados.")
                    modal.destroy()
                    self.cargar_usuarios()
                else:
                    messagebox.showerror("Error", f"No se pudo actualizar: {resp.text}")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        ctk.CTkButton(modal, text="Guardar Cambios", width=200, command=guardar_cambios).pack(pady=15)

    def crear_placeholder(self, tab, texto):
        lbl = ctk.CTkLabel(tab, text=texto, font=ctk.CTkFont(size=22, weight="bold"), text_color="gray50")
        lbl.place(relx=0.5, rely=0.5, anchor="center")

    def cargar_habitaciones(self):
        for widget in self.frame_lista.winfo_children():
            widget.destroy()
            
        # Variables para controlar la cuadrícula (Grid)
        self.columna_actual = 0
        self.fila_actual = 0
        self.max_columnas = 3 # Mostrará 3 tarjetas por fila
        
        try:
            respuesta = requests.get(f"{self.url_base}/habitaciones/", headers=self.headers)
            if respuesta.status_code == 200:
                lista_habs = respuesta.json()
                for hab in lista_habs:
                    self.crear_tarjeta_habitacion(hab)
                if hasattr(self, "actualizar_combo_habitaciones_reserva"):
                    self.actualizar_combo_habitaciones_reserva(lista_habs)
        except requests.exceptions.ConnectionError:
            pass

    def crear_tarjeta_habitacion(self, habitacion):
        # Seleccionamos el color del fondo basado en el estado
        color_fondo = self.COLORES_ESTADO.get(habitacion['estado'], "#424242")
        alto_tarjeta = 185 if self.id_rol == 1 else 145
        
        # Tarjeta con tamaño fijo
        tarjeta = ctk.CTkFrame(self.frame_lista, fg_color=color_fondo, width=250, height=alto_tarjeta, corner_radius=15)
        tarjeta.grid_propagate(False) # Evita que la tarjeta se encoja
        tarjeta.grid(row=self.fila_actual, column=self.columna_actual, padx=15, pady=15)
        
        # Número de Habitación gigante
        ctk.CTkLabel(tarjeta, text=f"{habitacion['numero_habitacion']}", font=ctk.CTkFont(size=32, weight="bold"), text_color="white").pack(pady=(8, 0))
        
        # Subtítulo con tipo, capacidad y precio base
        precio = habitacion.get("precio_base", 0)
        ctk.CTkLabel(
            tarjeta,
            text=f"{habitacion['tipo']} | Cap: {habitacion['capacidad']} | ${precio:.0f}",
            font=ctk.CTkFont(size=12),
            text_color="white"
        ).pack(pady=(0, 6))
        
        # OptionMenu: Al elegir una opción, ejecuta actualizar_estado automáticamente
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

        # Controles exclusivos para el Administrador: Editar e Inhabilitar/Habilitar
        if self.id_rol == 1:
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
        
        # Lógica matemática para saltar a la siguiente fila cuando se llenen las 3 columnas
        self.columna_actual += 1
        if self.columna_actual >= self.max_columnas:
            self.columna_actual = 0
            self.fila_actual += 1

    def actualizar_estado(self, id_habitacion, nuevo_estado):
        # Esta función ahora se ejecuta de forma "silenciosa" en el fondo
        try:
            respuesta = requests.patch(f"{self.url_base}/habitaciones/{id_habitacion}/estado", json={"estado": nuevo_estado}, headers=self.headers)
            if respuesta.status_code == 200:
                self.cargar_habitaciones() # Refresca el panel entero para actualizar el color
            else:
                messagebox.showerror("Error API", "No se pudo actualizar el estado.")
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Error", "No hay conexión con el servidor.")
    
    def cerrar_sesion(self):
        respuesta = messagebox.askyesno("Cerrar Sesión", "¿Estás seguro de que deseas salir?")
        if respuesta:
            self.destroy() # Destruye el panel y borra el token de la memoria
            
            # Importación local para evitar el error de importación circular
            from login_gui import VentanaLogin
            app_login = VentanaLogin()
            app_login.mainloop()

    OPCIONES_DOCUMENTO = [
        "Selecciona una opción",
        "INE",
        "Pasaporte",
        "Cartilla Militar",
        "Documento migratorio vigente",
    ]

    def _set_entry_readonly(self, entry_widget, valor: str, placeholder: str = ""):
        entry_widget.configure(state="normal")
        entry_widget.delete(0, "end")
        if valor:
            entry_widget.insert(0, valor)
        elif placeholder:
            entry_widget.configure(placeholder_text=placeholder)
        entry_widget.configure(state="readonly")

    def construir_pestana_recepcion(self):
        tab_rec = self.tabview.tab("Recepción y Reservas")
        
        # Frame izquierdo: Registro y Directorio de Huéspedes (RF-RES-001)
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
        ctk.CTkButton(frame_hdr_h, text="Refrescar", width=85, height=24, command=self.cargar_huespedes).pack(side="right")

        frame_busqueda_h = ctk.CTkFrame(frame_huesped, fg_color="transparent")
        frame_busqueda_h.pack(fill="x", padx=10, pady=2)
        self.entry_buscar_huesped = ctk.CTkEntry(
            frame_busqueda_h,
            placeholder_text="Buscar por nombre, documento o RFC...",
            height=26
        )
        self.entry_buscar_huesped.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.entry_buscar_huesped.bind("<KeyRelease>", lambda _e: self.cargar_huespedes())
        ctk.CTkButton(
            frame_busqueda_h,
            text="Limpiar",
            width=65,
            height=26,
            fg_color="gray40",
            command=self.limpiar_busqueda_huesped
        ).pack(side="right")

        self.frame_lista_huespedes = ctk.CTkScrollableFrame(frame_huesped, height=180)
        self.frame_lista_huespedes.pack(fill="both", expand=True, padx=8, pady=5)
        
        # Frame derecho: Creación de Reservas, Check-in, Check-out y Listado (RF-RES-002 a RF-RES-005)
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
        self.frame_lista_reservas.pack(fill="both", expand=True, padx=8, pady=5)

        self.cargar_huespedes()
        self.cargar_reservas()
        self.actualizar_combo_habitaciones_reserva()

    def construir_pestana_folios(self):
        tab_fol = self.tabview.tab("Facturación y Folios")
        self.saldo_folio_actual = 0.0

        # Panel Izquierdo: Consulta y Estado de Cuenta Folio (RF-FAC-001 y RF-FAC-002)
        frame_izq_f = ctk.CTkFrame(tab_fol)
        frame_izq_f.pack(side="left", fill="both", expand=True, padx=(10, 5), pady=10)

        ctk.CTkLabel(
            frame_izq_f,
            text="Estado de Cuenta Folio",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(10, 4))

        self.combo_folio_reserva = ctk.CTkOptionMenu(
            frame_izq_f,
            width=340,
            values=["Seleccione una reserva..."],
            command=self.al_seleccionar_combo_folio
        )
        self.combo_folio_reserva.set("Seleccione una reserva...")
        self.combo_folio_reserva.pack(pady=3)

        frame_busq_f = ctk.CTkFrame(frame_izq_f, fg_color="transparent")
        frame_busq_f.pack(pady=3)
        self.entry_folio_reserva_id = ctk.CTkEntry(
            frame_busq_f,
            width=125,
            placeholder_text="ID Reserva"
        )
        self.entry_folio_reserva_id.pack(side="left", padx=4)
        self.entry_folio_reserva_id.configure(state="readonly")

        ctk.CTkButton(
            frame_busq_f,
            text="Consultar / Refrescar",
            width=145,
            command=self.consultar_folio
        ).pack(side="left", padx=4)
        ctk.CTkButton(
            frame_busq_f,
            text="Limpiar",
            width=70,
            fg_color="gray40",
            hover_color="gray30",
            command=self.limpiar_consulta_folio
        ).pack(side="left", padx=4)

        self.frame_resumen_folio = ctk.CTkFrame(frame_izq_f)
        self.frame_resumen_folio.pack(fill="x", padx=10, pady=6)

        self.label_resultado_folio = ctk.CTkLabel(
            self.frame_resumen_folio,
            text="Seleccione una reserva para visualizar su Estado de Cuenta Folio.",
            font=ctk.CTkFont(size=12),
            text_color="gray70",
            justify="left"
        )
        self.label_resultado_folio.pack(padx=10, pady=(8, 2))

        self.label_saldo_destacado = ctk.CTkLabel(
            self.frame_resumen_folio,
            text="Saldo Pendiente: $0.00",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="gray60"
        )
        self.label_saldo_destacado.pack(padx=10, pady=(2, 8))

        ctk.CTkLabel(
            frame_izq_f,
            text="Desglose de Movimientos (Cargos y Pagos)",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(pady=(4, 2))

        self.frame_movimientos_folio = ctk.CTkScrollableFrame(frame_izq_f, height=200)
        self.frame_movimientos_folio.pack(fill="both", expand=True, padx=10, pady=(2, 10))

        # Panel Derecho: Cargos Manuales, Registro de Pagos y Timbrado PAC (RF-FAC-003 a RF-FAC-005)
        frame_der_f = ctk.CTkFrame(tab_fol)
        frame_der_f.pack(side="right", fill="both", expand=True, padx=(5, 10), pady=10)

        # --- Sub-sección 1: Cargos Manuales / Extras ---
        frame_sec_cargo = ctk.CTkFrame(frame_der_f)
        frame_sec_cargo.pack(fill="x", padx=10, pady=(8, 4))

        ctk.CTkLabel(
            frame_sec_cargo,
            text="1. Agregar Cargo Manual / Extra",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(6, 3))

        self.combo_concepto_cargo = ctk.CTkOptionMenu(
            frame_sec_cargo,
            width=310,
            values=[
                "Seleccione concepto rápido (opcional)...",
                "Consumo de Servibar / Minibar",
                "Daño o reposición en habitación",
                "Penalización por salida tardía (Late Check-out)",
                "Servicio de Lavandería / Tintorería",
                "Cargo por persona adicional",
            ],
            command=self.al_seleccionar_concepto_cargo
        )
        self.combo_concepto_cargo.set("Seleccione concepto rápido (opcional)...")
        self.combo_concepto_cargo.pack(pady=2)

        frame_inp_cargo = ctk.CTkFrame(frame_sec_cargo, fg_color="transparent")
        frame_inp_cargo.pack(pady=2)
        self.entry_cargo_desc = ctk.CTkEntry(frame_inp_cargo, width=195, placeholder_text="Descripción del cargo")
        self.entry_cargo_desc.pack(side="left", padx=3)
        self.entry_cargo_monto = ctk.CTkEntry(frame_inp_cargo, width=110, placeholder_text="Monto ($)")
        self.entry_cargo_monto.pack(side="left", padx=3)

        frame_btn_cargo = ctk.CTkFrame(frame_sec_cargo, fg_color="transparent")
        frame_btn_cargo.pack(pady=(3, 6))
        ctk.CTkButton(
            frame_btn_cargo,
            text="Agregar Cargo",
            width=145,
            fg_color="#E65100",
            hover_color="#BF360C",
            command=self.registrar_cargo_manual
        ).pack(side="left", padx=4)
        ctk.CTkButton(
            frame_btn_cargo,
            text="Limpiar",
            width=80,
            fg_color="gray40",
            hover_color="gray30",
            command=self.limpiar_form_cargo
        ).pack(side="left", padx=4)

        # --- Sub-sección 2: Registro de Pagos ---
        frame_sec_pago = ctk.CTkFrame(frame_der_f)
        frame_sec_pago.pack(fill="x", padx=10, pady=4)

        ctk.CTkLabel(
            frame_sec_pago,
            text="2. Registrar Pago a Cuenta Folio",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(6, 3))

        self.combo_metodo_pago = ctk.CTkOptionMenu(
            frame_sec_pago,
            width=310,
            values=[
                "Selecciona una opción",
                "Efectivo",
                "Tarjeta (Terminal PinPad)",
            ]
        )
        self.combo_metodo_pago.set("Selecciona una opción")
        self.combo_metodo_pago.pack(pady=2)

        frame_inp_pago = ctk.CTkFrame(frame_sec_pago, fg_color="transparent")
        frame_inp_pago.pack(pady=2)
        self.entry_pago_monto = ctk.CTkEntry(frame_inp_pago, width=155, placeholder_text="Monto a pagar ($)")
        self.entry_pago_monto.pack(side="left", padx=3)
        ctk.CTkButton(
            frame_inp_pago,
            text="Usar Saldo Total",
            width=150,
            fg_color="#1565C0",
            hover_color="#0D47A1",
            command=self.usar_saldo_pendiente_pago
        ).pack(side="left", padx=3)

        frame_btn_pago = ctk.CTkFrame(frame_sec_pago, fg_color="transparent")
        frame_btn_pago.pack(pady=(3, 6))
        ctk.CTkButton(
            frame_btn_pago,
            text="Registrar Pago",
            width=145,
            fg_color="#2E7D32",
            hover_color="#1b5e20",
            command=self.registrar_pago_folio
        ).pack(side="left", padx=4)
        ctk.CTkButton(
            frame_btn_pago,
            text="Limpiar",
            width=80,
            fg_color="gray40",
            hover_color="gray30",
            command=self.limpiar_form_pago
        ).pack(side="left", padx=4)

        # --- Sub-sección 3: Emisión de Factura Electrónica ---
        frame_sec_fac = ctk.CTkFrame(frame_der_f)
        frame_sec_fac.pack(fill="x", padx=10, pady=(4, 8))

        ctk.CTkLabel(
            frame_sec_fac,
            text="3. Emisión de Factura Electrónica",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(6, 3))

        frame_inp_fac = ctk.CTkFrame(frame_sec_fac, fg_color="transparent")
        frame_inp_fac.pack(pady=2)
        self.entry_fac_rfc = ctk.CTkEntry(frame_inp_fac, width=150, placeholder_text="RFC (Ej. XAXX010101000)")
        self.entry_fac_rfc.pack(side="left", padx=3)
        self.entry_fac_razon = ctk.CTkEntry(frame_inp_fac, width=155, placeholder_text="Razón Social (Opcional)")
        self.entry_fac_razon.pack(side="left", padx=3)

        frame_btn_fac = ctk.CTkFrame(frame_sec_fac, fg_color="transparent")
        frame_btn_fac.pack(pady=(3, 6))
        ctk.CTkButton(
            frame_btn_fac,
            text="Timbrar Factura",
            width=145,
            command=self.timbrar_factura_gui
        ).pack(side="left", padx=4)
        ctk.CTkButton(
            frame_btn_fac,
            text="Limpiar",
            width=80,
            fg_color="gray40",
            hover_color="gray30",
            command=self.limpiar_form_factura
        ).pack(side="left", padx=4)

        self.actualizar_combo_reservas_folio()

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
            respuesta = requests.post(f"{self.url_base}/huespedes/", json=datos, headers=self.headers)
            if respuesta.status_code in [200, 201]:
                h_json = respuesta.json()
                messagebox.showinfo("Éxito", f"Huésped registrado correctamente (ID: #{h_json.get('id_huesped')}).")
                self.limpiar_formulario_huesped()
                self.cargar_huespedes()
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
        self.entry_h_nombre.delete(0, "end")
        self.combo_h_doc.set("Selecciona una opción")
        self.entry_h_email.delete(0, "end")
        self.entry_h_tel.delete(0, "end")
        if hasattr(self, "entry_h_rfc"):
            self.entry_h_rfc.delete(0, "end")

    def limpiar_busqueda_huesped(self):
        if hasattr(self, "entry_buscar_huesped"):
            self.entry_buscar_huesped.delete(0, "end")
            self.cargar_huespedes()

    def actualizar_combo_habitaciones_reserva(self, lista_habs=None):
        if not hasattr(self, "combo_r_hab"):
            return
        try:
            if lista_habs is None:
                resp = requests.get(f"{self.url_base}/habitaciones/", headers=self.headers)
                if resp.status_code == 200:
                    lista_habs = resp.json()
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
        # Extrae el ID numérico del formato "ID X - Hab. Y..."
        if opcion_seleccionada.startswith("ID "):
            try:
                id_hab = opcion_seleccionada.split(" - ")[0].replace("ID ", "").strip()
                self._set_entry_readonly(self.entry_r_hab_id, id_hab, "ID Habitación")
            except Exception:
                pass
        else:
            self._set_entry_readonly(self.entry_r_hab_id, "", "ID Habitación")

    def cargar_huespedes(self):
        if not hasattr(self, "frame_lista_huespedes"):
            return
        for widget in self.frame_lista_huespedes.winfo_children():
            widget.destroy()

        filtro = ""
        if hasattr(self, "entry_buscar_huesped"):
            filtro = self.entry_buscar_huesped.get().strip().lower()

        try:
            resp = requests.get(f"{self.url_base}/huespedes/", headers=self.headers)
            if resp.status_code == 200:
                self.mapa_huespedes = {}
                for h in resp.json():
                    self.mapa_huespedes[h["id_huesped"]] = h.get("nombre_completo") or f"Huésped #{h['id_huesped']}"
                    nombre = (h.get("nombre_completo") or "").lower()
                    doc = (h.get("documento_identidad") or "").lower()
                    rfc_h = (h.get("rfc") or "").lower()
                    if filtro and filtro not in nombre and filtro not in doc and filtro not in rfc_h:
                        continue

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
        except requests.exceptions.ConnectionError:
            pass

    def eliminar_huesped_gui(self, id_huesped: int, nombre: str):
        confirmar = messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Deseas eliminar al huésped '{nombre}' (#{id_huesped})?\n\nNota: Solo se permite si no tiene reservaciones registradas."
        )
        if not confirmar:
            return
        try:
            resp = requests.delete(f"{self.url_base}/huespedes/{id_huesped}", headers=self.headers)
            if resp.status_code == 200:
                messagebox.showinfo("Éxito", resp.json().get("mensaje", "Huésped eliminado correctamente."))
                if self.entry_r_huesped_id.get().strip() == str(id_huesped):
                    self._set_entry_readonly(self.entry_r_huesped_id, "", "ID Huésped (Usar ID)")
                self.cargar_huespedes()
            else:
                detalle = resp.json().get("detail", resp.text)
                messagebox.showerror("No se puede eliminar", detalle)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def seleccionar_huesped_id(self, id_huesped):
        self._set_entry_readonly(self.entry_r_huesped_id, str(id_huesped), "ID Huésped (Usar ID)")

    def abrir_modal_editar_huesped(self, huesped):
        modal = ctk.CTkToplevel(self)
        modal.title(f"Editar Huésped #{huesped['id_huesped']}")
        modal.geometry("350x380")
        modal.grab_set()

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
                r = requests.put(
                    f"{self.url_base}/huespedes/{huesped['id_huesped']}",
                    json=datos,
                    headers=self.headers
                )
                if r.status_code == 200:
                    messagebox.showinfo("Éxito", "Datos del huésped actualizados.")
                    modal.destroy()
                    self.cargar_huespedes()
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

    def abrir_mini_calendario(self, entry_destino, titulo="Seleccionar Fecha", es_entrada=True):
        modal = ctk.CTkToplevel(self)
        modal.title(titulo)
        modal.geometry("320x330")
        modal.resizable(False, False)
        modal.grab_set()

        # Determinar mes/año inicial a partir del campo o la fecha actual
        hoy = date.today()
        valor_actual = entry_destino.get().strip()
        fecha_base = hoy
        if valor_actual:
            try:
                fecha_base = datetime.strptime(valor_actual, "%Y-%m-%d").date()
            except ValueError:
                fecha_base = hoy

        estado_cal = {"anio": fecha_base.year, "mes": fecha_base.month}
        nombres_meses = [
            "", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]

        frame_nav = ctk.CTkFrame(modal, fg_color="transparent")
        frame_nav.pack(fill="x", padx=12, pady=(10, 4))

        lbl_mes_anio = ctk.CTkLabel(frame_nav, text="", font=ctk.CTkFont(size=15, weight="bold"))

        frame_dias = ctk.CTkFrame(modal)
        frame_dias.pack(fill="both", expand=True, padx=12, pady=4)

        def seleccionar_dia(dia_num: int):
            fecha_elegida = date(estado_cal["anio"], estado_cal["mes"], dia_num)
            self._set_entry_readonly(entry_destino, fecha_elegida.strftime("%Y-%m-%d"))
            # Si eligió fecha de entrada y la salida está vacía o es menor/igual, sugerir +1 noche automáticamente
            if es_entrada:
                sal_txt = self.entry_r_f_salida.get().strip()
                sugerir = False
                if not sal_txt:
                    sugerir = True
                else:
                    try:
                        if datetime.strptime(sal_txt, "%Y-%m-%d").date() <= fecha_elegida:
                            sugerir = True
                    except ValueError:
                        sugerir = True
                if sugerir:
                    manana = fecha_elegida + timedelta(days=1)
                    self._set_entry_readonly(self.entry_r_f_salida, manana.strftime("%Y-%m-%d"))
            modal.destroy()

        def renderizar_mes():
            for w in frame_dias.winfo_children():
                w.destroy()
            lbl_mes_anio.configure(text=f"{nombres_meses[estado_cal['mes']]} {estado_cal['anio']}")

            dias_semana = ["Lu", "Ma", "Mi", "Ju", "Vi", "Sá", "Do"]
            for idx, d_nom in enumerate(dias_semana):
                ctk.CTkLabel(
                    frame_dias,
                    text=d_nom,
                    width=34,
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color="#64B5F6"
                ).grid(row=0, column=idx, padx=2, pady=3)

            cal_matriz = calendar.monthcalendar(estado_cal["anio"], estado_cal["mes"])
            for fila_idx, semana in enumerate(cal_matriz, start=1):
                for col_idx, dia in enumerate(semana):
                    if dia == 0:
                        ctk.CTkLabel(frame_dias, text="", width=34).grid(row=fila_idx, column=col_idx, padx=2, pady=2)
                    else:
                        es_hoy = (
                            dia == hoy.day
                            and estado_cal["mes"] == hoy.month
                            and estado_cal["anio"] == hoy.year
                        )
                        color_btn = "#2E7D32" if es_hoy else "#1F6AA5"
                        ctk.CTkButton(
                            frame_dias,
                            text=str(dia),
                            width=34,
                            height=28,
                            fg_color=color_btn,
                            command=lambda d=dia: seleccionar_dia(d)
                        ).grid(row=fila_idx, column=col_idx, padx=2, pady=2)

        def mes_anterior():
            if estado_cal["mes"] == 1:
                estado_cal["mes"] = 12
                estado_cal["anio"] -= 1
            else:
                estado_cal["mes"] -= 1
            renderizar_mes()

        def mes_siguiente():
            if estado_cal["mes"] == 12:
                estado_cal["mes"] = 1
                estado_cal["anio"] += 1
            else:
                estado_cal["mes"] += 1
            renderizar_mes()

        ctk.CTkButton(frame_nav, text="◀", width=36, height=26, command=mes_anterior).pack(side="left")
        lbl_mes_anio.pack(side="left", expand=True)
        ctk.CTkButton(frame_nav, text="▶", width=36, height=26, command=mes_siguiente).pack(side="right")

        frame_footer = ctk.CTkFrame(modal, fg_color="transparent")
        frame_footer.pack(fill="x", padx=12, pady=(2, 8))
        ctk.CTkButton(
            frame_footer,
            text="Seleccionar Hoy",
            width=130,
            height=26,
            fg_color="#2E7D32",
            command=lambda: (
                estado_cal.update({"anio": hoy.year, "mes": hoy.month}),
                seleccionar_dia(hoy.day)
            )
        ).pack(side="left", padx=4)
        ctk.CTkButton(
            frame_footer,
            text="Cerrar",
            width=90,
            height=26,
            fg_color="gray40",
            command=modal.destroy
        ).pack(side="right", padx=4)

        renderizar_mes()

    def limpiar_formulario_reserva(self):
        self.combo_r_hab.set("Seleccione una habitación...")
        self._set_entry_readonly(self.entry_r_huesped_id, "", "ID Huésped (Usar ID)")
        self._set_entry_readonly(self.entry_r_hab_id, "", "ID Habitación")
        self._set_entry_readonly(self.entry_r_f_entrada, "", "Entrada")
        self._set_entry_readonly(self.entry_r_f_salida, "", "Salida")

    def cargar_reservas(self):
        if not hasattr(self, "frame_lista_reservas"):
            return
        for widget in self.frame_lista_reservas.winfo_children():
            widget.destroy()

        colores_res = {
            "Confirmada": "#64B5F6",
            "Activa": "#66BB6A",
            "Finalizada": "#BDBDBD",
            "Cancelada": "#EF5350",
        }
        try:
            resp = requests.get(f"{self.url_base}/reservas/", headers=self.headers)
            if resp.status_code == 200:
                lista_res = resp.json()
                for r in lista_res:
                    fila = ctk.CTkFrame(self.frame_lista_reservas)
                    fila.pack(fill="x", pady=2, padx=2)

                    est = r.get("estado_reserva", "")
                    color_txt = colores_res.get(est, "white")
                    nombre_huesped = (
                        r.get("nombre_huesped")
                        or getattr(self, "mapa_huespedes", {}).get(r.get("id_huesped"))
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
                if hasattr(self, "actualizar_combo_reservas_folio"):
                    self.actualizar_combo_reservas_folio(lista_res)
        except requests.exceptions.ConnectionError:
            pass

    def seleccionar_reserva_id(self, id_reserva):
        self._set_entry_readonly(self.entry_checkin_id, str(id_reserva), "ID de Reserva")
        if hasattr(self, "entry_folio_reserva_id"):
            self._set_entry_readonly(self.entry_folio_reserva_id, str(id_reserva), "ID Reserva")
            self.consultar_folio()

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
            respuesta = requests.post(f"{self.url_base}/reservas/", json=datos, headers=self.headers)
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
            respuesta = requests.patch(f"{self.url_base}/reservas/{reserva_id}/cancelar", headers=self.headers)
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
            respuesta = requests.post(f"{self.url_base}/reservas/{reserva_id}/checkin", headers=self.headers)
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
                self.cargar_habitaciones()
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
            respuesta = requests.post(f"{self.url_base}/reservas/{reserva_id}/checkout", headers=self.headers)
            if respuesta.status_code == 200:
                data = respuesta.json()
                messagebox.showinfo(
                    "Check-out Exitoso",
                    f"{data.get('mensaje')}\n"
                    f"Estado Reserva: {data.get('nuevo_estado_reserva')}\n"
                    f"Estado Folio: {data.get('nuevo_estado_folio')}"
                )
                self.cargar_habitaciones()
                self.cargar_reservas()
            else:
                detalle = respuesta.json().get("detail", respuesta.text)
                messagebox.showerror("No se puede realizar Check-out", detalle)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def actualizar_combo_reservas_folio(self, lista_res=None):
        if not hasattr(self, "combo_folio_reserva"):
            return
        try:
            if lista_res is None:
                resp = requests.get(f"{self.url_base}/reservas/", headers=self.headers)
                if resp.status_code == 200:
                    lista_res = resp.json()
                else:
                    return
            opciones = ["Seleccione una reserva..."]
            for r in lista_res:
                nom = r.get("nombre_huesped") or getattr(self, "mapa_huespedes", {}).get(r.get("id_huesped")) or f"Huésped #{r.get('id_huesped')}"
                hab = r.get("numeros_habitaciones") or "Sin hab."
                opciones.append(f"Reserva #{r['id_reserva']} | {nom} | Hab. {hab} [{r.get('estado_reserva')}]")
            self.combo_folio_reserva.configure(values=opciones)
        except requests.exceptions.ConnectionError:
            pass

    def al_seleccionar_combo_folio(self, opcion: str):
        if opcion.startswith("Reserva #"):
            try:
                id_res = opcion.split(" | ")[0].replace("Reserva #", "").strip()
                self._set_entry_readonly(self.entry_folio_reserva_id, id_res, "ID Reserva")
                self.consultar_folio()
            except Exception:
                pass
        else:
            self.limpiar_consulta_folio()

    def limpiar_consulta_folio(self):
        if hasattr(self, "combo_folio_reserva"):
            self.combo_folio_reserva.set("Seleccione una reserva...")
        self._set_entry_readonly(self.entry_folio_reserva_id, "", "ID Reserva")
        self.saldo_folio_actual = 0.0
        self.label_resultado_folio.configure(
            text="Seleccione una reserva para visualizar su Estado de Cuenta Folio.",
            text_color="gray70"
        )
        self.label_saldo_destacado.configure(text="Saldo Pendiente: $0.00", text_color="gray60")
        for w in self.frame_movimientos_folio.winfo_children():
            w.destroy()

    def _extraer_detalle_error(self, resp) -> str:
        try:
            data = resp.json()
            if isinstance(data, dict):
                return str(data.get("detail", resp.text))
            return str(data)
        except Exception:
            return resp.text or f"Error HTTP {resp.status_code}"

    def consultar_folio(self):
        try:
            reserva_id = self.entry_folio_reserva_id.get().strip()
            if not reserva_id:
                messagebox.showwarning("Advertencia", "Seleccione una reserva del menú desplegable.")
                return
            respuesta = requests.get(f"{self.url_base}/reservas/{reserva_id}", headers=self.headers)
            if respuesta.status_code == 200:
                data = respuesta.json()
                nom_h = data.get("nombre_huesped") or f"Huésped #{data.get('id_huesped')}"
                rfc_h = data.get("rfc_huesped") or ""
                habs = data.get("numeros_habitaciones") or "Sin hab."
                total_cargos = float(data.get("total_cargos", 0.0))
                total_pagos = float(data.get("total_pagos", 0.0))
                saldo = float(data.get("saldo_pendiente", 0.0))
                self.saldo_folio_actual = saldo

                if hasattr(self, "combo_folio_reserva"):
                    prefijo = f"Reserva #{data.get('id_reserva')} |"
                    for op in self.combo_folio_reserva.cget("values"):
                        if op.startswith(prefijo):
                            self.combo_folio_reserva.set(op)
                            break

                if hasattr(self, "entry_fac_rfc"):
                    self.entry_fac_rfc.delete(0, "end")
                    if rfc_h:
                        self.entry_fac_rfc.insert(0, rfc_h)
                if hasattr(self, "entry_fac_razon"):
                    self.entry_fac_razon.delete(0, "end")
                    if data.get("nombre_huesped"):
                        self.entry_fac_razon.insert(0, data.get("nombre_huesped"))

                texto = (
                    f"Reserva #{data.get('id_reserva')}  |  Huésped: {nom_h}  |  Habitación: {habs}\n"
                    f"Estado Reserva: {data.get('estado_reserva')}  |  Estado Folio: {data.get('estado_folio')}\n"
                    f"Estancia: {data.get('fecha_entrada')} al {data.get('fecha_salida')}\n"
                    f"Total Cargos: ${total_cargos:.2f}   |   Total Pagos: ${total_pagos:.2f}"
                )
                self.label_resultado_folio.configure(text=texto, text_color="white")

                color_saldo = "#66BB6A" if saldo <= 0 else "#FFA726"
                estado_liq = "(LIQUIDADO)" if saldo <= 0 and total_cargos > 0 else ""
                self.label_saldo_destacado.configure(
                    text=f"Saldo Pendiente: ${saldo:.2f} {estado_liq}",
                    text_color=color_saldo
                )

                for w in self.frame_movimientos_folio.winfo_children():
                    w.destroy()

                cargos = data.get("cargos", [])
                pagos = data.get("pagos", [])
                if not cargos and not pagos:
                    ctk.CTkLabel(
                        self.frame_movimientos_folio,
                        text="Sin cargos ni pagos registrados aún (realice el Check-in para abrir el folio).",
                        text_color="gray60",
                        font=ctk.CTkFont(size=11)
                    ).pack(pady=10)
                else:
                    for c in cargos:
                        fila_c = ctk.CTkFrame(self.frame_movimientos_folio)
                        fila_c.pack(fill="x", padx=3, pady=2)
                        ctk.CTkLabel(
                            fila_c,
                            text=f"[CARGO] {c.get('descripcion')}",
                            font=ctk.CTkFont(size=11)
                        ).pack(side="left", padx=6, pady=3)
                        ctk.CTkLabel(
                            fila_c,
                            text=f"+ ${float(c.get('monto', 0)):.2f}",
                            text_color="#FF8A65",
                            font=ctk.CTkFont(size=11, weight="bold")
                        ).pack(side="right", padx=6, pady=3)

                    for p in pagos:
                        fila_p = ctk.CTkFrame(self.frame_movimientos_folio)
                        fila_p.pack(fill="x", padx=3, pady=2)
                        ctk.CTkLabel(
                            fila_p,
                            text=f"[PAGO] {p.get('metodo_pago')}",
                            font=ctk.CTkFont(size=11)
                        ).pack(side="left", padx=6, pady=3)
                        ctk.CTkLabel(
                            fila_p,
                            text=f"- ${float(p.get('monto', 0)):.2f}",
                            text_color="#81C784",
                            font=ctk.CTkFont(size=11, weight="bold")
                        ).pack(side="right", padx=6, pady=3)
            else:
                messagebox.showerror("Error", "No se encontró información para esa reserva.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def al_seleccionar_concepto_cargo(self, opcion: str):
        if not opcion.startswith("Seleccione "):
            self.entry_cargo_desc.delete(0, "end")
            self.entry_cargo_desc.insert(0, opcion)

    def limpiar_form_cargo(self):
        self.combo_concepto_cargo.set("Seleccione concepto rápido (opcional)...")
        self.entry_cargo_desc.delete(0, "end")
        self.entry_cargo_monto.delete(0, "end")

    def registrar_cargo_manual(self):
        reserva_id = self.entry_folio_reserva_id.get().strip()
        if not reserva_id:
            messagebox.showwarning("Reserva requerida", "Primero selecciona una reserva en el Estado de Cuenta Folio.")
            return
        desc = self.entry_cargo_desc.get().strip()
        monto_txt = self.entry_cargo_monto.get().strip()
        if not desc or not monto_txt:
            messagebox.showwarning("Datos incompletos", "Ingresa la descripción y el monto del cargo.")
            return
        try:
            monto = float(monto_txt)
            datos = {
                "id_reserva": int(reserva_id),
                "descripcion": desc,
                "monto": monto,
            }
            resp = requests.post(f"{self.url_base}/finanzas/cargos", json=datos, headers=self.headers)
            if resp.status_code in (200, 201):
                messagebox.showinfo("Cargo Registrado", f"Cargo '{desc}' por ${monto:.2f} agregado al Folio.")
                self.limpiar_form_cargo()
                self.consultar_folio()
            else:
                detalle = self._extraer_detalle_error(resp)
                messagebox.showerror("No se pudo agregar el cargo", detalle)
        except ValueError:
            messagebox.showerror("Monto inválido", "El monto debe ser un número válido (ej. 250.00).")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def usar_saldo_pendiente_pago(self):
        if getattr(self, "saldo_folio_actual", 0.0) <= 0:
            messagebox.showinfo("Sin saldo pendiente", "La reserva seleccionada no tiene saldo pendiente por cobrar.")
            return
        self.entry_pago_monto.delete(0, "end")
        self.entry_pago_monto.insert(0, f"{self.saldo_folio_actual:.2f}")

    def limpiar_form_pago(self):
        self.combo_metodo_pago.set("Selecciona una opción")
        self.entry_pago_monto.delete(0, "end")

    def _ejecutar_post_pago(self, id_reserva: int, metodo_pago_str: str, monto: float) -> bool:
        try:
            datos = {
                "id_reserva": id_reserva,
                "metodo_pago": metodo_pago_str,
                "monto": monto,
            }
            resp = requests.post(f"{self.url_base}/finanzas/pagos", json=datos, headers=self.headers)
            if resp.status_code in (200, 201):
                pago_json = resp.json()
                messagebox.showinfo(
                    "Pago Registrado",
                    f"Pago por ${monto:.2f} registrado con éxito.\n"
                    f"Método: {pago_json.get('metodo_pago')}"
                )
                self.limpiar_form_pago()
                self.consultar_folio()
                return True
            else:
                detalle = self._extraer_detalle_error(resp)
                messagebox.showerror("No se pudo registrar el pago", detalle)
                return False
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return False

    def registrar_pago_folio(self):
        reserva_id = self.entry_folio_reserva_id.get().strip()
        if not reserva_id:
            messagebox.showwarning("Reserva requerida", "Primero selecciona una reserva en el Estado de Cuenta Folio.")
            return
        metodo = self.combo_metodo_pago.get()
        if metodo == "Selecciona una opción":
            messagebox.showwarning("Método de pago requerido", "Selecciona un método de pago (Efectivo o Tarjeta).")
            return
        monto_txt = self.entry_pago_monto.get().strip()
        if not monto_txt:
            messagebox.showwarning("Monto requerido", "Ingresa el monto a pagar o pulsa 'Usar Saldo Total'.")
            return
        try:
            monto = float(monto_txt)
            if monto <= 0:
                messagebox.showwarning("Monto inválido", "El monto a pagar debe ser mayor a $0.00.")
                return
            if monto > round(getattr(self, "saldo_folio_actual", 0.0) + 0.01, 2):
                messagebox.showwarning(
                    "Monto excede saldo",
                    f"El monto (${monto:.2f}) excede el saldo pendiente de la reserva (${self.saldo_folio_actual:.2f})."
                )
                return
            if metodo == "Tarjeta (Terminal PinPad)":
                self.abrir_simulador_terminal_pinpad(int(reserva_id), monto)
            else:
                self._ejecutar_post_pago(int(reserva_id), metodo, monto)
        except ValueError:
            messagebox.showerror("Monto inválido", "El monto debe ser un número válido.")

    def abrir_simulador_terminal_pinpad(self, id_reserva: int, monto: float):
        modal = ctk.CTkToplevel(self)
        modal.title("Terminal Bancaria PinPad")
        modal.geometry("390x430")
        modal.resizable(False, False)
        modal.grab_set()

        ctk.CTkLabel(
            modal,
            text="Terminal Bancaria PinPad",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(12, 4))

        ctk.CTkLabel(
            modal,
            text="Entregue la terminal al huésped para autorizar el cargo",
            font=ctk.CTkFont(size=12),
            text_color="gray70"
        ).pack(pady=(0, 8))

        # Pantalla LCD simulada de la terminal
        frame_lcd = ctk.CTkFrame(modal, fg_color="#0D1B2A", corner_radius=10, border_width=2, border_color="#415A77")
        frame_lcd.pack(fill="x", padx=22, pady=6)

        ctk.CTkLabel(
            frame_lcd,
            text=f"TOTAL A COBRAR: ${monto:.2f} MXN",
            font=ctk.CTkFont(size=17, weight="bold"),
            text_color="#00E676"
        ).pack(pady=(10, 4))

        lbl_estado_lcd = ctk.CTkLabel(
            frame_lcd,
            text="Acerque, inserte o deslice su tarjeta...",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#90CAF9",
            wraplength=320
        )
        lbl_estado_lcd.pack(pady=(2, 10))

        # Frame dinámico para el ingreso de NIP (oculto inicialmente)
        frame_nip = ctk.CTkFrame(modal, fg_color="transparent")
        entry_nip = ctk.CTkEntry(
            frame_nip,
            width=140,
            placeholder_text="NIP (4 dígitos)",
            show="*",
            justify="center",
            font=ctk.CTkFont(size=15, weight="bold")
        )
        entry_nip.pack(side="left", padx=6)

        def confirmar_nip():
            nip = entry_nip.get().strip()
            if len(nip) != 4 or not nip.isdigit():
                lbl_estado_lcd.configure(
                    text="⚠️ NIP inválido: Ingrese exactamente 4 dígitos numéricos.",
                    text_color="#FFB74D"
                )
                return
            token_corto = uuid.uuid4().hex[:8].upper()
            metodo_token = f"Tarjeta Chip ****7390 (Tok: {token_corto})"
            lbl_estado_lcd.configure(
                text=f"✅ APROBADA CON NIP\nToken: tok_chip_{token_corto}",
                text_color="#00E676"
            )
            modal.update_idletasks()
            modal.destroy()
            self._ejecutar_post_pago(id_reserva, metodo_token, monto)

        ctk.CTkButton(
            frame_nip,
            text="Autorizar NIP",
            width=120,
            fg_color="#2E7D32",
            hover_color="#1b5e20",
            command=confirmar_nip
        ).pack(side="left", padx=4)

        def pago_contactless():
            token_corto = uuid.uuid4().hex[:8].upper()
            metodo_token = f"Tarjeta NFC ****4821 (Tok: {token_corto})"
            lbl_estado_lcd.configure(
                text=f"✅ APROBADA SIN CONTACTO (NFC)\nToken: tok_nfc_{token_corto}",
                text_color="#00E676"
            )
            modal.update_idletasks()
            modal.destroy()
            self._ejecutar_post_pago(id_reserva, metodo_token, monto)

        def mostrar_modo_chip():
            lbl_estado_lcd.configure(
                text="💳 Tarjeta con Chip leída.\nCliente: Ingrese su NIP de 4 dígitos y pulse Autorizar.",
                text_color="#FFF59D"
            )
            frame_nip.pack(pady=6)
            entry_nip.focus_set()

        def simular_declinada():
            frame_nip.pack_forget()
            lbl_estado_lcd.configure(
                text="❌ TRANSACCIÓN DECLINADA POR EL BANCO EMISOR\n(Fondos insuficientes o tarjeta bloqueada)",
                text_color="#FF5252"
            )

        frame_acciones_pinpad = ctk.CTkFrame(modal, fg_color="transparent")
        frame_acciones_pinpad.pack(fill="x", padx=25, pady=8)

        ctk.CTkButton(
            frame_acciones_pinpad,
            text="📶 Acercar Tarjeta (Contactless / NFC)",
            height=36,
            fg_color="#1565C0",
            hover_color="#0D47A1",
            command=pago_contactless
        ).pack(fill="x", pady=4)

        ctk.CTkButton(
            frame_acciones_pinpad,
            text="💳 Insertar Tarjeta (Chip + NIP)",
            height=36,
            fg_color="#00695C",
            hover_color="#004D40",
            command=mostrar_modo_chip
        ).pack(fill="x", pady=4)

        ctk.CTkButton(
            frame_acciones_pinpad,
            text="🚫 Simular Tarjeta Declinada",
            height=34,
            fg_color="#C62828",
            hover_color="#8E0000",
            command=simular_declinada
        ).pack(fill="x", pady=4)

        ctk.CTkButton(
            modal,
            text="Cancelar Operación",
            width=160,
            fg_color="gray40",
            hover_color="gray30",
            command=modal.destroy
        ).pack(pady=(6, 10))

    def limpiar_form_factura(self):
        self.entry_fac_rfc.delete(0, "end")
        self.entry_fac_razon.delete(0, "end")

    def generar_pdf_factura(self, fac: dict) -> str:
        carpeta_base = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "facturas_emitidas"))
        os.makedirs(carpeta_base, exist_ok=True)
        uuid_str = fac.get("uuid_fiscal", "SIN-UUID")
        id_res = fac.get("id_reserva", "0")
        nombre_archivo = f"Factura_CFDI_Reserva_{id_res}_{uuid_str[:8]}.pdf"
        ruta_pdf = os.path.join(carpeta_base, nombre_archivo)

        doc = SimpleDocTemplate(
            ruta_pdf,
            pagesize=letter,
            rightMargin=40,
            leftMargin=40,
            topMargin=36,
            bottomMargin=36,
        )
        estilos = getSampleStyleSheet()
        estilo_normal = estilos["Normal"]
        estilo_sub = ParagraphStyle(
            "SubtituloAzul",
            parent=estilo_normal,
            fontName="Helvetica-Bold",
            fontSize=11,
            textColor=colors.HexColor("#0D2B4E"),
            spaceAfter=4,
        )
        estilo_peq = ParagraphStyle(
            "PequenoGris",
            parent=estilo_normal,
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#4A5568"),
        )

        elementos = []

        # 1. Encabezado con Logo KeyFlow (versión clara) y Datos Fiscales del Emisor
        if os.path.exists(self.ruta_logo_light):
            logo_rl = RLImage(self.ruta_logo_light, width=2.2 * inch, height=0.86 * inch)
        elif os.path.exists(self.ruta_logo_dark):
            logo_rl = RLImage(self.ruta_logo_dark, width=2.2 * inch, height=0.86 * inch)
        else:
            logo_rl = Paragraph("<b>HOTEL KEYFLOW</b>", estilo_sub)

        info_emisor = Paragraph(
            "<b>HOTEL KEYFLOW S.A. DE C.V.</b><br/>"
            "RFC Emisor: <b>HKF260101AAA</b><br/>"
            "Régimen Fiscal: 601 - General de Ley Personas Morales<br/>"
            "Tipo de Comprobante: I - Ingreso (CFDI 4.0)<br/>"
            f"Fecha y Hora de Certificación: {fac.get('fecha_timbrado', '')}",
            estilo_normal,
        )
        tabla_header = Table([[logo_rl, info_emisor]], colWidths=[2.6 * inch, 4.6 * inch])
        tabla_header.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                ]
            )
        )
        elementos.append(tabla_header)
        elementos.append(Spacer(1, 8))

        # 2. Tabla de Datos del Receptor y Folio Fiscal UUID
        datos_receptor = [
            [
                Paragraph("<b>DATOS DEL RECEPTOR (CLIENTE)</b>", estilo_sub),
                Paragraph("<b>DATOS FISCALES DEL COMPROBANTE</b>", estilo_sub),
            ],
            [
                Paragraph(
                    f"<b>Razón Social:</b> {fac.get('razon_social', 'PÚBLICO EN GENERAL')}<br/>"
                    f"<b>RFC Receptor:</b> {fac.get('rfc_receptor', '')}<br/>"
                    "<b>Uso de CFDI:</b> G03 - Gastos en general",
                    estilo_normal,
                ),
                Paragraph(
                    f"<b>Folio Fiscal (UUID):</b><br/>{uuid_str}<br/>"
                    f"<b>Reserva #:</b> {id_res} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Habitación:</b> {fac.get('habitaciones', 'S/N')}<br/>"
                    f"<b>Estancia:</b> {fac.get('fecha_entrada', '')} al {fac.get('fecha_salida', '')}",
                    estilo_normal,
                ),
            ],
        ]
        tabla_receptor = Table(datos_receptor, colWidths=[3.5 * inch, 3.7 * inch])
        tabla_receptor.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EDF2F7")),
                    ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#CBD5E0")),
                    ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                    ("PADDING", (0, 0), (-1, -1), 8),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]
            )
        )
        elementos.append(tabla_receptor)
        elementos.append(Spacer(1, 14))

        # 3. Tabla de Conceptos (Cargos del Folio)
        elementos.append(Paragraph("CONCEPTOS FACTURADOS", estilo_sub))
        filas_conceptos = [["Clave SAT", "Cant.", "Unidad", "Descripción del Concepto", "Importe (MXN)"]]
        cargos = fac.get("cargos") or []
        if not cargos:
            filas_conceptos.append(
                ["90111500", "1", "E48", f"Servicios de Hospedaje - Reserva #{id_res}", f"${float(fac.get('total_facturado', 0)):.2f}"]
            )
        else:
            for c in cargos:
                filas_conceptos.append(
                    [
                        "90111500",
                        "1",
                        "E48",
                        str(c.get("descripcion", "Cargo de estancia")),
                        f"${float(c.get('monto', 0)):.2f}",
                    ]
                )

        tabla_conceptos = Table(
            filas_conceptos,
            colWidths=[1.0 * inch, 0.6 * inch, 0.7 * inch, 3.6 * inch, 1.3 * inch],
        )
        tabla_conceptos.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0D2B4E")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("ALIGN", (0, 0), (2, -1), "CENTER"),
                    ("ALIGN", (4, 0), (4, -1), "RIGHT"),
                    ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#CBD5E0")),
                    ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                    ("PADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        elementos.append(tabla_conceptos)
        elementos.append(Spacer(1, 12))

        # 4. Resumen de Pagos y Desglose de Impuestos (Subtotal, IVA 16%, Total)
        pagos = fac.get("pagos") or []
        metodos_str = ", ".join(p.get("metodo_pago", "Efectivo") for p in pagos) if pagos else "Liquidado en Recepción"
        info_pago_p = Paragraph(
            f"<b>Forma / Método de Pago Registrado:</b><br/>{metodos_str}<br/><br/>"
            "<b>Moneda:</b> MXN - Peso Mexicano<br/>"
            "<b>Exportación:</b> 01 - No aplica",
            estilo_normal,
        )

        subtotal = float(fac.get("subtotal", 0.0))
        iva = float(fac.get("iva_16", 0.0))
        total = float(fac.get("total_facturado", 0.0))

        tabla_totales = Table(
            [
                ["Subtotal:", f"${subtotal:,.2f} MXN"],
                ["IVA Trasladado (16%):", f"${iva:,.2f} MXN"],
                ["TOTAL FACTURADO:", f"${total:,.2f} MXN"],
            ],
            colWidths=[1.5 * inch, 1.3 * inch],
        )
        tabla_totales.setStyle(
            TableStyle(
                [
                    ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
                    ("FONTNAME", (0, 2), (-1, 2), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 2), (-1, 2), 11),
                    ("TEXTCOLOR", (0, 2), (-1, 2), colors.HexColor("#0D2B4E")),
                    ("LINEABOVE", (0, 2), (-1, 2), 1.0, colors.HexColor("#0D2B4E")),
                    ("PADDING", (0, 0), (-1, -1), 5),
                ]
            )
        )

        tabla_pie_totales = Table([[info_pago_p, tabla_totales]], colWidths=[4.4 * inch, 2.8 * inch])
        tabla_pie_totales.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
        elementos.append(tabla_pie_totales)
        elementos.append(Spacer(1, 20))

        # 5. Sello Digital PAC / SAT Simulado
        sello_simulado = (
            f"||1.1|{uuid_str}|{fac.get('fecha_timbrado', '')}|HKF260101AAA|"
            f"{fac.get('rfc_receptor', '')}|{total:.2f}|SelloDigitalPACKeyFlow="
            f"{uuid_str.replace('-', '')}89AF01BC||"
        )
        elementos.append(
            Paragraph(
                f"<b>Cadena Original del Complemento de Certificación Digital del SAT:</b><br/>{sello_simulado}<br/><br/>"
                "Este documento es una representación impresa de un CFDI emitida por el Sistema de Gestión Hotelera KeyFlow.",
                estilo_peq,
            )
        )

        doc.build(elementos)
        return ruta_pdf

    def timbrar_factura_gui(self):
        reserva_id = self.entry_folio_reserva_id.get().strip()
        if not reserva_id:
            messagebox.showwarning("Reserva requerida", "Primero selecciona una reserva en el Estado de Cuenta Folio.")
            return
        rfc = self.entry_fac_rfc.get().strip()
        if not rfc:
            messagebox.showwarning("RFC requerido", "Ingresa el RFC del cliente para timbrar la factura.")
            return
        razon = self.entry_fac_razon.get().strip() or "PÚBLICO EN GENERAL"
        try:
            datos = {
                "id_reserva": int(reserva_id),
                "rfc_cliente": rfc,
                "razon_social": razon,
            }
            resp = requests.post(f"{self.url_base}/finanzas/facturar", json=datos, headers=self.headers)
            if resp.status_code == 200:
                fac = resp.json()
                ruta_pdf = self.generar_pdf_factura(fac)
                try:
                    os.startfile(ruta_pdf)
                except Exception:
                    pass
                messagebox.showinfo(
                    "Factura Timbrada y PDF Generado",
                    f"¡Factura electrónica emitida con éxito!\n\n"
                    f"UUID Fiscal: {fac.get('uuid_fiscal')}\n"
                    f"RFC Receptor: {fac.get('rfc_receptor')}\n"
                    f"Razón Social: {fac.get('razon_social')}\n"
                    f"Subtotal: ${fac.get('subtotal', 0):.2f}\n"
                    f"IVA (16%): ${fac.get('iva_16', 0):.2f}\n"
                    f"Total Facturado: ${fac.get('total_facturado', 0):.2f}\n\n"
                    f"Archivo PDF guardado en:\n{ruta_pdf}"
                )
                self.cargar_huespedes()
            elif resp.status_code == 422:
                errores = resp.json().get("detail", [])
                msg = "El RFC ingresado no cumple con la estructura fiscal válida."
                if isinstance(errores, list) and errores:
                    msg = errores[0].get("msg", msg)
                messagebox.showerror("Error de Validación de RFC", msg)
            else:
                detalle = self._extraer_detalle_error(resp)
                messagebox.showerror("No se pudo timbrar la factura", detalle)
        except Exception as e:
            messagebox.showerror("Error", str(e))