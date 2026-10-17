import customtkinter as ctk
import requests
from tkinter import messagebox
from main_panel_gui import PanelPrincipal

# Configuración del tema de la ventana
ctk.set_appearance_mode("Dark")  # Opciones: "System", "Dark", "Light"
ctk.set_default_color_theme("blue")

class VentanaLogin(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Hotel KeyFlow - Acceso")
        self.geometry("400x500")
        self.resizable(False, False)
        
        # Título
        self.label_titulo = ctk.CTkLabel(self, text="Hotel KeyFlow", font=ctk.CTkFont(size=32, weight="bold"))
        self.label_titulo.pack(pady=(60, 40))
        
        # Campo Correo
        self.entry_email = ctk.CTkEntry(self, placeholder_text="Correo electrónico", width=280, height=40)
        self.entry_email.pack(pady=10)
        
        # Campo Contraseña
        self.entry_password = ctk.CTkEntry(self, placeholder_text="Contraseña", show="*", width=280, height=40)
        self.entry_password.pack(pady=20)
        
        # Botón Iniciar Sesión
        self.btn_login = ctk.CTkButton(self, text="Iniciar Sesión", width=280, height=40, font=ctk.CTkFont(weight="bold"), command=self.procesar_login)
        self.btn_login.pack(pady=20)
        
    def procesar_login(self):
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
            # Enviamos la petición a nuestro Backend
            respuesta = requests.post(url_api, data=datos_formulario)
            
            if respuesta.status_code == 200:
                # ¡Acceso concedido! Extraemos el token y el rol
                datos = respuesta.json()
                token = datos.get("access_token")
                id_rol = datos.get("id_rol")
                
                self.abrir_panel_principal(token, id_rol) # Pasamos ambos datos
                
            elif respuesta.status_code == 401:
                messagebox.showerror("Acceso Denegado", "Correo o contraseña incorrectos.")
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