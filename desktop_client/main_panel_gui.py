import customtkinter as ctk
import requests
from tkinter import messagebox

class PanelPrincipal(ctk.CTk):
    def __init__(self, token, id_rol):
        super().__init__()
        
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
        self.header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        self.label_titulo = ctk.CTkLabel(self.header_frame, text="Sistema de Gestión Hotelera - Hotel KeyFlow", font=ctk.CTkFont(size=26, weight="bold"))
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
        self.combo_rol = ctk.CTkComboBox(frame_izq, width=240, values=["2 (Recepción)", "3 (Limpieza)", "1 (Administrador)"])
        self.combo_rol.pack(pady=8)
        ctk.CTkButton(frame_izq, text="Registrar Usuario", width=240, command=self.crear_usuario).pack(pady=20)

        # Encabezado y Lista de Personal en Columna Derecha
        frame_header_der = ctk.CTkFrame(frame_der, fg_color="transparent")
        frame_header_der.pack(fill="x", padx=12, pady=(12, 5))
        ctk.CTkLabel(
            frame_header_der,
            text="Personal Registrado (RF-ADM-003)",
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
                self.cargar_usuarios()
            else:
                messagebox.showerror("Error", f"Fallo al registrar: {respuesta.text}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

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
                for hab in respuesta.json():
                    self.crear_tarjeta_habitacion(hab)
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

    def construir_pestana_recepcion(self):
        tab_rec = self.tabview.tab("Recepción y Reservas")
        
        # Frame izquierdo: Registro de Huéspedes
        frame_huesped = ctk.CTkFrame(tab_rec)
        frame_huesped.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(frame_huesped, text="Registro de Huésped", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=15)
        self.entry_h_nombre = ctk.CTkEntry(frame_huesped, placeholder_text="Nombre Completo")
        self.entry_h_nombre.pack(pady=5)
        self.entry_h_doc = ctk.CTkEntry(frame_huesped, placeholder_text="Documento de Identidad")
        self.entry_h_doc.pack(pady=5)
        self.entry_h_email = ctk.CTkEntry(frame_huesped, placeholder_text="Correo Electrónico")
        self.entry_h_email.pack(pady=5)
        self.entry_h_tel = ctk.CTkEntry(frame_huesped, placeholder_text="Teléfono")
        self.entry_h_tel.pack(pady=5)
        ctk.CTkButton(frame_huesped, text="Registrar Huésped", command=self.crear_huesped).pack(pady=20)
        
        # Frame derecho: Creación de Reservas y Check-in
        frame_res = ctk.CTkFrame(tab_rec)
        frame_res.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(frame_res, text="Gestión de Reservas", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)
        self.entry_r_huesped_id = ctk.CTkEntry(frame_res, placeholder_text="ID Huésped")
        self.entry_r_huesped_id.pack(pady=5)
        self.entry_r_hab_id = ctk.CTkEntry(frame_res, placeholder_text="ID Habitación")
        self.entry_r_hab_id.pack(pady=5)
        self.entry_r_f_entrada = ctk.CTkEntry(frame_res, placeholder_text="Fecha Entrada (AAAA-MM-DD)")
        self.entry_r_f_entrada.pack(pady=5)
        self.entry_r_f_salida = ctk.CTkEntry(frame_res, placeholder_text="Fecha Salida (AAAA-MM-DD)")
        self.entry_r_f_salida.pack(pady=5)
        ctk.CTkButton(frame_res, text="Crear Reserva", command=self.crear_reserva).pack(pady=10)
        
        ctk.CTkLabel(frame_res, text="Ejecutar Check-in / Folio", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 5))
        self.entry_checkin_id = ctk.CTkEntry(frame_res, placeholder_text="ID de Reserva")
        self.entry_checkin_id.pack(pady=5)
        ctk.CTkButton(frame_res, text="Hacer Check-in & Abrir Folio", fg_color="#2E7D32", hover_color="#1b5e20", command=self.ejecutar_checkin).pack(pady=10)

    def construir_pestana_folios(self):
        tab_fol = self.tabview.tab("Facturación y Folios")
        
        frame_folios = ctk.CTkFrame(tab_fol)
        frame_folios.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(frame_folios, text="Control de Cuentas Folio", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=15)
        
        self.entry_folio_reserva_id = ctk.CTkEntry(frame_folios, placeholder_text="Ingrese el ID de la Reserva")
        self.entry_folio_reserva_id.pack(pady=5)
        ctk.CTkButton(frame_folios, text="Consultar Estado de Folio", command=self.consultar_folio).pack(pady=15)
        
        self.label_resultado_folio = ctk.CTkLabel(frame_folios, text="Consulte una reserva para ver el estado de su cuenta y folio.", font=ctk.CTkFont(size=14), text_color="gray70")
        self.label_resultado_folio.pack(pady=20)

    def crear_huesped(self):
        try:
            datos = {
                "nombre_completo": self.entry_h_nombre.get(),
                "documento_identidad": self.entry_h_doc.get(),
                "email": self.entry_h_email.get(),
                "telefono": self.entry_h_tel.get()
            }
            respuesta = requests.post(f"{self.url_base}/huespedes/", json=datos, headers=self.headers)
            if respuesta.status_code in [200, 201]:
                messagebox.showinfo("Éxito", "Huésped registrado correctamente en el sistema.")
            else:
                messagebox.showerror("Error", f"No se pudo registrar: {respuesta.text}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def crear_reserva(self):
        try:
            datos = {
                "fecha_entrada": self.entry_r_f_entrada.get(),
                "fecha_salida": self.entry_r_f_salida.get(),
                "estado_reserva": "Confirmada",
                "estado_folio": "Abierto",
                "id_usuario": 2,  # <--- Cambia el 1 por el ID 2 o 3 que acabamos de ver en la base de datos
                "id_huesped": int(self.entry_r_huesped_id.get()),
                "id_habitacion": int(self.entry_r_hab_id.get())
            }
            respuesta = requests.post(f"{self.url_base}/reservas/", json=datos, headers=self.headers)
            if respuesta.status_code in [200, 201]:
                res_json = respuesta.json()
                messagebox.showinfo("Éxito", f"Reserva creada con éxito. ID Asignado: {res_json.get('id_reserva')}")
            else:
                messagebox.showerror("Error", f"Fallo al crear reserva: {respuesta.text}")
        except Exception as e:
            messagebox.showerror("Error", f"Verifica que los IDs y fechas sean correctos: {str(e)}")

    def ejecutar_checkin(self):
        try:
            reserva_id = self.entry_checkin_id.get()
            if not reserva_id:
                messagebox.showwarning("Advertencia", "Por favor ingresa un ID de reserva.")
                return
            respuesta = requests.post(f"{self.url_base}/reservas/{reserva_id}/checkin", headers=self.headers)
            if respuesta.status_code == 200:
                data = respuesta.json()
                messagebox.showinfo("Éxito", f"¡Check-in realizado y Folio abierto!\nEstado Reserva: {data.get('nuevo_estado_reserva')}\nEstado Folio: {data.get('nuevo_estado_folio')}")
            else:
                messagebox.showerror("Error", f"No se pudo completar el check-in: {respuesta.text}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def consultar_folio(self):
        try:
            reserva_id = self.entry_folio_reserva_id.get()
            respuesta = requests.get(f"{self.url_base}/reservas/{reserva_id}", headers=self.headers)
            if respuesta.status_code == 200:
                data = respuesta.json()
                texto = (f"--- DETALLE DE CUENTA FOLIO ---\n"
                         f"Reserva ID: {data.get('id_reserva')}\n"
                         f"Estado de Reserva: {data.get('estado_reserva')}\n"
                         f"Estado de Folio: {data.get('estado_folio')}\n"
                         f"Entrada: {data.get('fecha_entrada')} | Salida: {data.get('fecha_salida')}")
                self.label_resultado_folio.configure(text=texto, text_color="white")
            else:
                messagebox.showerror("Error", "No se encontró información para esa reserva.")
        except Exception as e:
            messagebox.showerror("Error", str(e))