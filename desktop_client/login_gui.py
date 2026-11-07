import os
import customtkinter as ctk
from PIL import Image
import requests
from tkinter import messagebox
from main_panel_gui import PanelPrincipal

# Configuración del tema de la ventana
ctk.set_appearance_mode("Dark")  # Opciones: "System", "Dark", "Light"
ctk.set_default_color_theme("blue")

class VentanaLogin(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.http = requests.Session()
        
        self.title("Hotel KeyFlow - Acceso")
        self.geometry("400x500")
        self.resizable(False, False)
        
        # Logo del sistema
        ruta_assets = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
        ruta_dark = os.path.join(ruta_assets, "logo_dark.png")
        ruta_light = os.path.join(ruta_assets, "logo_light.png")
        if os.path.exists(ruta_dark):
            img_dark = Image.open(ruta_dark)
            img_light = Image.open(ruta_light) if os.path.exists(ruta_light) else img_dark
            self.logo_ctk = ctk.CTkImage(light_image=img_light, dark_image=img_dark, size=(240, 94))
            self.label_titulo = ctk.CTkLabel(self, text="", image=self.logo_ctk)
        else:
            self.label_titulo = ctk.CTkLabel(self, text="Hotel KeyFlow", font=ctk.CTkFont(size=32, weight="bold"))
        self.label_titulo.pack(pady=(50, 35))
        
        # Campo Correo
        self.entry_email = ctk.CTkEntry(self, placeholder_text="Correo electrónico", width=280, height=40)
        self.entry_email.pack(pady=10)
        self.entry_email.bind("<Return>", lambda _e: self.procesar_login())
        
        # Campo Contraseña
        self.entry_password = ctk.CTkEntry(self, placeholder_text="Contraseña", show="*", width=280, height=40)
        self.entry_password.pack(pady=20)
        self.entry_password.bind("<Return>", lambda _e: self.procesar_login())
        
        # Botón Iniciar Sesión
        self.btn_login = ctk.CTkButton(self, text="Iniciar Sesión", width=280, height=40, font=ctk.CTkFont(weight="bold"), command=self.procesar_login)
        self.btn_login.pack(pady=20)
        
    def procesar_login(self, *_args):
        email = self.entry_email.get()
        password = self.entry_password.get()
        
        if not email or not password:
            messagebox.showwarning("Advertencia", "Por favor, completa todos los campos.")
            return
            
        # Nuestra API espera recibir los datos como un formulario (Form-Data)
        datos_formulario = {
            "username": email,
            "password": password
        }
        
        url_api = "http://127.0.0.1:8000/login"
        
        try:
            # Enviamos la petición a nuestro Backend reutilizando sesión HTTP
            respuesta = self.http.post(url_api, data=datos_formulario)
            
            if respuesta.status_code == 200:
                # ¡Acceso concedido! Extraemos el token y el rol
                datos = respuesta.json()
                token = datos.get("access_token")
                id_rol = datos.get("id_rol")
                
                self.abrir_panel_principal(token, id_rol) # Pasamos ambos datos
                
            elif respuesta.status_code == 401:
                messagebox.showerror("Acceso Denegado", "Correo o contraseña incorrectos.")
            elif respuesta.status_code == 403:
                messagebox.showerror("Cuenta Desactivada", "Esta cuenta de usuario se encuentra desactivada. Contacta al Administrador.")
            else:
                messagebox.showerror("Error", f"Error del servidor: {respuesta.status_code}")
                
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Error de Conexión", "No se pudo conectar al servidor. Verifica que la API esté encendida.")

    def abrir_panel_principal(self, token, id_rol):
        self.destroy()
        app_principal = PanelPrincipal(token, id_rol) # Instanciamos con el rol
        app_principal.mainloop()

if __name__ == "__main__":
    app = VentanaLogin()
    app.mainloop()