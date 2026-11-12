"""
Vista de la pestaña de Usuarios (Administración de Personal).
"""
import requests
from tkinter import messagebox
import customtkinter as ctk


class TabUsuariosView:
    def __init__(self, tab, app):
        self.tab = tab
        self.app = app

        # Form widgets references
        self.entry_nombre_user = None
        self.entry_email_user = None
        self.entry_pass_user = None
        self.combo_rol = None
        self.frame_lista_usuarios = None

        self.construir()

    def construir(self):
        tab_admin = self.tab

        # Columna Izquierda: Formulario de Alta de Personal
        frame_izq = ctk.CTkFrame(tab_admin, width=300)
        frame_izq.pack(side="left", fill="y", padx=(10, 5), pady=10)
        frame_izq.pack_propagate(False)

        # Columna Derecha: Lista amplia de Personal Registrado
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

    def crear_usuario(self):
        try:
            datos = {
                "nombre": self.entry_nombre_user.get(),
                "email": self.entry_email_user.get(),
                "password": self.entry_pass_user.get(),
                "id_rol": int(self.combo_rol.get()[0])
            }
            respuesta = self.app.http.post(f"{self.app.url_base}/usuarios/", json=datos)
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
        if not self.frame_lista_usuarios or not self.frame_lista_usuarios.winfo_exists():
            return
        for widget in self.frame_lista_usuarios.winfo_children():
            widget.destroy()

        nombres_roles = {1: "Admin", 2: "Recepción", 3: "Limpieza"}
        try:
            respuesta = self.app.http.get(f"{self.app.url_base}/usuarios/")
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
            respuesta = self.app.http.patch(
                f"{self.app.url_base}/usuarios/{id_usuario}/estado",
                json={"estado_activo": nuevo_estado}
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
        modal = self.app._crear_modal(f"Editar Empleado #{usuario['id_usuario']}", "360x360")

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
                resp = self.app.http.put(
                    f"{self.app.url_base}/usuarios/{usuario['id_usuario']}",
                    json=datos
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
        self.app._mostrar_modal(modal)
