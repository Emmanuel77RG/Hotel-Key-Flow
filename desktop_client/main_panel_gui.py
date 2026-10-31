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
        
        self.label_titulo = ctk.CTkLabel(self, text="Sistema de Gestión Hotelera - Hotel KeyFlow", font=ctk.CTkFont(size=26, weight="bold"))
        self.label_titulo.pack(pady=(20, 10))
        
        self.tabview = ctk.CTkTabview(self, width=900, height=550)
        self.tabview.pack(pady=10, padx=20, fill="both", expand=True)
        
        # Pestaña de Administración (Protegida por Rol)
        if self.id_rol == 1:
            self.tabview.add("Administración")
            self.construir_pestana_admin()
            
        self.tabview.add("Habitaciones")
        self.tabview.add("Recepción y Reservas")
        self.construir_pestana_recepcion()
        self.tabview.add("Facturación y Folios")
        self.construir_pestana_folios()
        self.tabview.add("Punto de Venta")
        self.tabview.add("Mantenimiento")
        self.tabview.add("Reportes")
        
        # --- MÓDULO DE HABITACIONES (GRID) ---
        self.frame_lista = ctk.CTkScrollableFrame(self.tabview.tab("Habitaciones"), width=800, height=450)
        self.frame_lista.pack(pady=10, padx=20, fill="both", expand=True)
        
        self.btn_refrescar = ctk.CTkButton(self.tabview.tab("Habitaciones"), text="Refrescar Inventario", command=self.cargar_habitaciones)
        self.btn_refrescar.pack(pady=10)
        
        self.crear_placeholder(self.tabview.tab("Mantenimiento"), "Módulo de Gestión de Tickets de Mantenimiento\n\n(En desarrollo - Sprint 5)")
        self.crear_placeholder(self.tabview.tab("Punto de Venta"), "Módulo de Punto de Venta (Restaurante y Room Service)\n\n(En desarrollo - Sprint 6)")
        self.crear_placeholder(self.tabview.tab("Reportes"), "Módulo de Reportes Operativos y Corte de Caja\n\n(En desarrollo - Sprint 7)")
        
        self.cargar_habitaciones()

    def construir_pestana_admin(self):
        tab_admin = self.tabview.tab("Administración")
        frame_izq = ctk.CTkFrame(tab_admin)
        frame_izq.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        frame_der = ctk.CTkFrame(tab_admin)
        frame_der.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        # Formulario Habitación
        ctk.CTkLabel(frame_izq, text="Alta de Habitaciones", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=15)
        self.entry_num_hab = ctk.CTkEntry(frame_izq, placeholder_text="Número (Ej. 102)")
        self.entry_num_hab.pack(pady=5)
        self.combo_tipo = ctk.CTkComboBox(frame_izq, values=["Sencilla", "Doble", "Suite"])
        self.combo_tipo.pack(pady=5)
        self.entry_capacidad = ctk.CTkEntry(frame_izq, placeholder_text="Capacidad (Ej. 2)")
        self.entry_capacidad.pack(pady=5)
        self.entry_precio = ctk.CTkEntry(frame_izq, placeholder_text="Precio Base (Ej. 1500.00)")
        self.entry_precio.pack(pady=5)
        ctk.CTkButton(frame_izq, text="Guardar Habitación", command=self.crear_habitacion).pack(pady=20)
        
        # Formulario Usuario
        ctk.CTkLabel(frame_der, text="Alta de Personal", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=15)
        self.entry_nombre_user = ctk.CTkEntry(frame_der, placeholder_text="Nombre Completo")
        self.entry_nombre_user.pack(pady=5)
        self.entry_email_user = ctk.CTkEntry(frame_der, placeholder_text="Correo Electrónico")
        self.entry_email_user.pack(pady=5)
        self.entry_pass_user = ctk.CTkEntry(frame_der, placeholder_text="Contraseña", show="*")
        self.entry_pass_user.pack(pady=5)
        self.combo_rol = ctk.CTkComboBox(frame_der, values=["2 (Recepción)", "3 (Limpieza)", "1 (Administrador)"])
        self.combo_rol.pack(pady=5)
        ctk.CTkButton(frame_der, text="Registrar Usuario", command=self.crear_usuario).pack(pady=20)

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
            else:
                messagebox.showerror("Error", f"Fallo al crear: {respuesta.text}")
        except Exception as e:
            messagebox.showerror("Error", f"Verifica los datos ingresados: {str(e)}")

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
            else:
                messagebox.showerror("Error", f"Fallo al registrar: {respuesta.text}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

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
        
        # Tarjeta con tamaño fijo
        tarjeta = ctk.CTkFrame(self.frame_lista, fg_color=color_fondo, width=250, height=140, corner_radius=15)
        tarjeta.grid_propagate(False) # Evita que la tarjeta se encoja
        tarjeta.grid(row=self.fila_actual, column=self.columna_actual, padx=15, pady=15)
        
        # Número de Habitación gigante
        ctk.CTkLabel(tarjeta, text=f"{habitacion['numero_habitacion']}", font=ctk.CTkFont(size=36, weight="bold"), text_color="white").pack(pady=(10, 0))
        
        # Subtítulo con tipo
        ctk.CTkLabel(tarjeta, text=f"{habitacion['tipo']} (Cap: {habitacion['capacidad']})", font=ctk.CTkFont(size=12), text_color="white").pack(pady=(0, 10))
        
        # OptionMenu: Al elegir una opción, ejecuta actualizar_estado automáticamente
        estados_permitidos = ["Limpia", "Sucia", "En Limpieza", "Ocupada", "Mantenimiento"]
        combo_estado = ctk.CTkOptionMenu(
            tarjeta, 
            values=estados_permitidos, 
            width=160, 
            fg_color="#212121", 
            button_color="#111111", 
            text_color="white",
            command=lambda nuevo_estado, id_hab=habitacion['id_habitacion']: self.actualizar_estado(id_hab, nuevo_estado)
        )
        combo_estado.set(habitacion['estado'])
        combo_estado.pack(pady=5)
        
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