"""
Panel Principal de Hotel KeyFlow.
Actúa como Shell y Coordinador de la aplicación de escritorio.
Delega cada módulo a su vista correspondiente en el paquete 'views'.
"""
import calendar
from datetime import date, datetime, timedelta
import os
import uuid
import customtkinter as ctk
from PIL import Image
import requests
from tkinter import messagebox

try:
    from reports import generar_pdf_factura as generar_pdf_factura_rep
    from reports import generar_pdf_corte_caja as generar_pdf_corte_caja_rep
    from widgets import crear_controles_paginacion
    from modals import (
        abrir_mini_calendario as abrir_mini_calendario_modal,
        abrir_simulador_terminal_pinpad as abrir_simulador_pinpad_modal,
    )
    from api import (
        ClienteAPIBase,
        HabitacionesAPI,
        HuespedesAPI,
        ReservasAPI,
        MantenimientoAPI,
        PosAPI,
        ReportesAPI,
    )
    from views import (
        TabHabitacionesView,
        TabUsuariosView,
        TabRecepcionView,
        TabFoliosView,
        TabPOSView,
        TabMantenimientoView,
        TabReportesView,
    )
except ImportError:
    from desktop_client.reports import generar_pdf_factura as generar_pdf_factura_rep
    from desktop_client.reports import generar_pdf_corte_caja as generar_pdf_corte_caja_rep
    from desktop_client.widgets import crear_controles_paginacion
    from desktop_client.modals import (
        abrir_mini_calendario as abrir_mini_calendario_modal,
        abrir_simulador_terminal_pinpad as abrir_simulador_pinpad_modal,
    )
    from desktop_client.api import (
        ClienteAPIBase,
        HabitacionesAPI,
        HuespedesAPI,
        ReservasAPI,
        MantenimientoAPI,
        PosAPI,
        ReportesAPI,
    )
    from desktop_client.views import (
        TabHabitacionesView,
        TabUsuariosView,
        TabRecepcionView,
        TabFoliosView,
        TabPOSView,
        TabMantenimientoView,
        TabReportesView,
    )


class PanelPrincipal(ctk.CTk):
    OPCIONES_DOCUMENTO = TabRecepcionView.OPCIONES_DOCUMENTO
    CATEGORIAS_MANTENIMIENTO = TabMantenimientoView.CATEGORIAS_MANTENIMIENTO
    PRIORIDADES_MANTENIMIENTO = TabMantenimientoView.PRIORIDADES_MANTENIMIENTO
    CATALOGO_FALLAS_COMUNES = TabMantenimientoView.CATALOGO_FALLAS_COMUNES
    CATEGORIAS_POS = TabPOSView.CATEGORIAS_POS
    MODALIDADES_POS = TabPOSView.MODALIDADES_POS
    COLORES_CATEGORIA_POS = TabPOSView.COLORES_CATEGORIA_POS
    COLORES_ESTADO = TabHabitacionesView.COLORES_ESTADO

    def __init__(self, token, id_rol):
        super().__init__()
        self.title("Hotel KeyFlow")

        self.token = token
        self.id_rol = id_rol
        self.headers = {"Authorization": f"Bearer {self.token}"}
        self.url_base = "http://127.0.0.1:8000"
        self.http = requests.Session()
        self.http.headers.update(self.headers)

        # Servicios modulares de API
        self.cliente_api = ClienteAPIBase(token=self.token, url_base=self.url_base)
        self.api_habitaciones = HabitacionesAPI(self.cliente_api)
        self.api_huespedes = HuespedesAPI(self.cliente_api)
        self.api_reservas = ReservasAPI(self.cliente_api)
        self.api_mantenimiento = MantenimientoAPI(self.cliente_api)
        self.api_pos = PosAPI(self.cliente_api)
        self.api_reportes = ReportesAPI(self.cliente_api)

        # Cachés en memoria y temporizadores de debounce para evitar llamadas de red repetitivas
        self.cache_habitaciones = []
        self.cache_huespedes = []
        self.cache_reservas = []
        self.cache_tickets = []
        self.cache_productos_pos = []
        self.carrito_pos = {}
        self.cache_reporte = None
        self.mapa_huespedes = {}
        self._after_busq_huesped = None
        self._after_busq_ticket = None
        self._after_busq_pos = None
        self._pestanas_construidas = set()

        # Variables de paginación para mantener scroll fluido a 60 FPS y evitar sobrecarga visual
        self.pag_tickets = 1
        self.pag_rep_fin = 1
        self.pag_rep_op = 1
        self.pag_huespedes = 1
        self.pag_reservas = 1
        self.pag_pos = 1
        self.ITEMS_POR_PAGINA = 15

        # Encabezado con logotipo institucional y perfil de usuario
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

        self.btn_logout = ctk.CTkButton(
            self.header_frame,
            text="Cerrar Sesión",
            width=120,
            fg_color="#C62828",
            hover_color="#b71c1c",
            command=self.cerrar_sesion,
        )
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

        self.tabview = ctk.CTkTabview(self, width=900, height=550, command=self._al_cambiar_pestana)
        self.tabview.pack(pady=10, padx=20, fill="both", expand=True)

        # Registro de pestañas disponibles según Rol (Carga Perezosa / Lazy Loading)
        if self.id_rol == 1:
            self.tabview.add("Usuarios")
        self.tabview.add("Habitaciones")
        if self.id_rol in (1, 2):
            self.tabview.add("Recepción y Reservas")
            self.tabview.add("Facturación y Folios")
            self.tabview.add("Punto de Venta")
        self.tabview.add("Mantenimiento")
        if self.id_rol in (1, 2):
            self.tabview.add("Reportes")

        # Construir únicamente la pestaña activa inicial para un arranque instantáneo
        self._asegurar_pestana(self.tabview.get())

        # Maximizar siempre la ventana principal
        self.maximizar_ventana()
        self.after(50, self.maximizar_ventana)

    def maximizar_ventana(self):
        """Asegura que la ventana principal siempre inicie y se mantenga en estado maximizado."""
        try:
            self.state("zoomed")
        except Exception:
            try:
                self.attributes("-zoomed", True)
            except Exception:
                w = self.winfo_screenwidth()
                h = self.winfo_screenheight()
                self.geometry(f"{w}x{h}+0+0")

    # =========================================================================
    # GESTIÓN DE PESTAÑAS (LAZY LOADING) Y MODALES GLOBALES
    # =========================================================================
    def _al_cambiar_pestana(self):
        pestana = self.tabview.get()
        ya_construida = pestana in self._pestanas_construidas
        self._asegurar_pestana(pestana)
        if ya_construida:
            if pestana == "Reportes":
                self.cargar_reportes_gui()
            elif pestana == "Punto de Venta":
                self.actualizar_combo_habitaciones_pos(self.cache_reservas or None)

    def _asegurar_pestana(self, nombre_pestana: str):
        if not nombre_pestana or nombre_pestana in self._pestanas_construidas:
            return
        self._pestanas_construidas.add(nombre_pestana)
        if nombre_pestana == "Usuarios":
            self.construir_pestana_admin()
        elif nombre_pestana == "Habitaciones":
            self.construir_pestana_habitaciones()
        elif nombre_pestana == "Recepción y Reservas":
            self.construir_pestana_recepcion()
        elif nombre_pestana == "Facturación y Folios":
            self.construir_pestana_folios()
        elif nombre_pestana == "Punto de Venta":
            self.construir_pestana_pos()
        elif nombre_pestana == "Mantenimiento":
            self.construir_pestana_mantenimiento()
        elif nombre_pestana == "Reportes":
            self.construir_pestana_reportes()

    def _crear_modal(self, titulo: str, geometria: str, resizable: bool = False):
        modal = ctk.CTkToplevel(self)
        modal.title(titulo)
        modal.geometry(geometria)
        modal.resizable(resizable, resizable)
        modal.transient(self)
        return modal

    def _mostrar_modal(self, modal):
        modal.after(20, lambda: (modal.lift(), modal.focus_force(), modal.grab_set()))

    def _crear_controles_paginacion(
        self,
        frame_contenedor,
        pagina_actual: int,
        total_items: int,
        items_por_pagina: int,
        callback_cambio_pagina,
    ) -> tuple:
        return crear_controles_paginacion(
            frame_contenedor,
            pagina_actual,
            total_items,
            items_por_pagina,
            callback_cambio_pagina,
        )

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

    def cerrar_sesion(self):
        respuesta = messagebox.askyesno("Cerrar Sesión", "¿Estás seguro de que deseas salir?")
        if respuesta:
            try:
                self.http.close()
            except Exception:
                pass
            self.destroy()
            from login_gui import VentanaLogin
            app_login = VentanaLogin()
            app_login.mainloop()

    def crear_placeholder(self, tab, texto):
        ctk.CTkLabel(tab, text=texto, font=ctk.CTkFont(size=16)).pack(expand=True)

    # --- Propiedades de compatibilidad con widgets de vistas ---
    @property
    def entry_checkin_id(self):
        return getattr(self.vista_recepcion, "entry_checkin_id", None) if hasattr(self, "vista_recepcion") else None

    @property
    def entry_folio_reserva_id(self):
        return getattr(self.vista_folios, "entry_folio_reserva_id", None) if hasattr(self, "vista_folios") else None

    @property
    def saldo_folio_actual(self):
        return getattr(self.vista_folios, "saldo_folio_actual", 0.0) if hasattr(self, "vista_folios") else 0.0

    @saldo_folio_actual.setter
    def saldo_folio_actual(self, val):
        if hasattr(self, "vista_folios"):
            self.vista_folios.saldo_folio_actual = val

    @property
    def frame_lista(self):
        return getattr(self.vista_habitaciones, "frame_lista", None) if hasattr(self, "vista_habitaciones") else None

    # =========================================================================
    # MÓDULO 1: HABITACIONES (DELEGACIÓN A TabHabitacionesView)
    # =========================================================================
    def construir_pestana_habitaciones(self):
        tab_hab = self.tabview.tab("Habitaciones")
        self.vista_habitaciones = TabHabitacionesView(tab_hab, self)

    def cargar_habitaciones(self):
        if hasattr(self, "vista_habitaciones"):
            self.vista_habitaciones.cargar_habitaciones()

    def crear_tarjeta_habitacion(self, habitacion):
        if hasattr(self, "vista_habitaciones"):
            self.vista_habitaciones.crear_tarjeta_habitacion(habitacion)

    def actualizar_estado(self, id_habitacion, nuevo_estado):
        if hasattr(self, "vista_habitaciones"):
            self.vista_habitaciones.actualizar_estado(id_habitacion, nuevo_estado)

    def abrir_modal_nueva_habitacion(self):
        if hasattr(self, "vista_habitaciones"):
            self.vista_habitaciones.abrir_modal_nueva_habitacion()

    def crear_habitacion(self):
        if hasattr(self, "vista_habitaciones"):
            return self.vista_habitaciones.crear_habitacion()
        return False

    def abrir_modal_editar_habitacion(self, habitacion):
        if hasattr(self, "vista_habitaciones"):
            self.vista_habitaciones.abrir_modal_editar_habitacion(habitacion)

    # =========================================================================
    # MÓDULO 2: USUARIOS Y ADMINISTRACIÓN (DELEGACIÓN A TabUsuariosView)
    # =========================================================================
    def construir_pestana_admin(self):
        tab_admin = self.tabview.tab("Usuarios")
        self.vista_usuarios = TabUsuariosView(tab_admin, self)

    def crear_usuario(self):
        if hasattr(self, "vista_usuarios"):
            return self.vista_usuarios.crear_usuario()

    def limpiar_formulario_usuario(self):
        if hasattr(self, "vista_usuarios"):
            self.vista_usuarios.limpiar_formulario_usuario()

    def cargar_usuarios(self):
        if hasattr(self, "vista_usuarios"):
            self.vista_usuarios.cargar_usuarios()

    def cambiar_estado_usuario(self, id_usuario, nuevo_estado):
        if hasattr(self, "vista_usuarios"):
            self.vista_usuarios.cambiar_estado_usuario(id_usuario, nuevo_estado)

    def abrir_modal_editar_usuario(self, usuario):
        if hasattr(self, "vista_usuarios"):
            self.vista_usuarios.abrir_modal_editar_usuario(usuario)

    # =========================================================================
    # MÓDULO 3: RECEPCIÓN Y RESERVAS (DELEGACIÓN A TabRecepcionView)
    # =========================================================================
    def construir_pestana_recepcion(self):
        tab_rec = self.tabview.tab("Recepción y Reservas")
        self.vista_recepcion = TabRecepcionView(tab_rec, self)

    def crear_huesped(self):
        if hasattr(self, "vista_recepcion"):
            return self.vista_recepcion.crear_huesped()

    def limpiar_formulario_huesped(self):
        if hasattr(self, "vista_recepcion"):
            self.vista_recepcion.limpiar_formulario_huesped()

    def limpiar_busqueda_huesped(self):
        if hasattr(self, "vista_recepcion"):
            self.vista_recepcion.limpiar_busqueda_huesped()

    def _filtrar_huespedes_debounced(self, _event=None):
        if hasattr(self, "vista_recepcion"):
            self.vista_recepcion._filtrar_huespedes_debounced(_event)

    def actualizar_combo_habitaciones_reserva(self, lista_habs=None):
        if hasattr(self, "vista_recepcion"):
            self.vista_recepcion.actualizar_combo_habitaciones_reserva(lista_habs)

    def al_seleccionar_combo_habitacion(self, opcion_seleccionada: str):
        if hasattr(self, "vista_recepcion"):
            self.vista_recepcion.al_seleccionar_combo_habitacion(opcion_seleccionada)

    def cargar_huespedes(self, forzar_red: bool = True):
        if hasattr(self, "vista_recepcion"):
            self.vista_recepcion.cargar_huespedes(forzar_red)

    def _cambiar_pagina_huespedes(self, nueva_pag: int):
        if hasattr(self, "vista_recepcion"):
            self.vista_recepcion._cambiar_pagina_huespedes(nueva_pag)

    def renderizar_huespedes(self):
        if hasattr(self, "vista_recepcion"):
            self.vista_recepcion.renderizar_huespedes()

    def eliminar_huesped_gui(self, id_huesped: int, nombre: str):
        if hasattr(self, "vista_recepcion"):
            self.vista_recepcion.eliminar_huesped_gui(id_huesped, nombre)

    def seleccionar_huesped_id(self, id_huesped):
        if hasattr(self, "vista_recepcion"):
            self.vista_recepcion.seleccionar_huesped_id(id_huesped)

    def abrir_modal_editar_huesped(self, huesped):
        if hasattr(self, "vista_recepcion"):
            self.vista_recepcion.abrir_modal_editar_huesped(huesped)

    def abrir_mini_calendario(self, entry_destino, titulo="Seleccionar Fecha", es_entrada=True, al_seleccionar=None):
        entry_salida = getattr(self.vista_recepcion, "entry_r_f_salida", None) if (hasattr(self, "vista_recepcion") and es_entrada) else None
        return abrir_mini_calendario_modal(
            padre=self,
            entry_destino=entry_destino,
            titulo=titulo,
            es_entrada=es_entrada,
            al_seleccionar=al_seleccionar,
            entry_salida_sugerida=entry_salida,
        )

    def abrir_selector_fecha(self, entry_destino, titulo="Seleccionar Fecha", al_seleccionar=None):
        self.abrir_mini_calendario(entry_destino, titulo=titulo, es_entrada=False, al_seleccionar=al_seleccionar)

    def limpiar_formulario_reserva(self):
        if hasattr(self, "vista_recepcion"):
            self.vista_recepcion.limpiar_formulario_reserva()

    def _cambiar_pagina_reservas(self, nueva_pag: int):
        if hasattr(self, "vista_recepcion"):
            self.vista_recepcion._cambiar_pagina_reservas(nueva_pag)

    def cargar_reservas(self):
        if hasattr(self, "vista_recepcion"):
            self.vista_recepcion.cargar_reservas()

    def renderizar_reservas(self):
        if hasattr(self, "vista_recepcion"):
            self.vista_recepcion.renderizar_reservas()

    def seleccionar_reserva_id(self, id_reserva):
        if hasattr(self, "vista_recepcion"):
            self.vista_recepcion.seleccionar_reserva_id(id_reserva)

    def crear_reserva(self):
        if hasattr(self, "vista_recepcion"):
            return self.vista_recepcion.crear_reserva()

    def ejecutar_cancelar_reserva(self):
        if hasattr(self, "vista_recepcion"):
            return self.vista_recepcion.ejecutar_cancelar_reserva()

    def ejecutar_checkin(self):
        if hasattr(self, "vista_recepcion"):
            return self.vista_recepcion.ejecutar_checkin()

    def ejecutar_checkout(self):
        if hasattr(self, "vista_recepcion"):
            return self.vista_recepcion.ejecutar_checkout()

    # =========================================================================
    # MÓDULO 4: FACTURACIÓN Y FOLIOS (DELEGACIÓN A TabFoliosView)
    # =========================================================================
    def construir_pestana_folios(self):
        tab_fol = self.tabview.tab("Facturación y Folios")
        self.vista_folios = TabFoliosView(tab_fol, self)

    def actualizar_combo_reservas_folio(self, lista_res=None):
        if hasattr(self, "vista_folios"):
            self.vista_folios.actualizar_combo_reservas_folio(lista_res)

    def al_seleccionar_combo_folio(self, opcion: str):
        if hasattr(self, "vista_folios"):
            self.vista_folios.al_seleccionar_combo_folio(opcion)

    def limpiar_consulta_folio(self):
        if hasattr(self, "vista_folios"):
            self.vista_folios.limpiar_consulta_folio()

    def _extraer_detalle_error(self, resp) -> str:
        try:
            data = resp.json()
            if isinstance(data, dict):
                return str(data.get("detail", resp.text))
            return str(data)
        except Exception:
            return resp.text or f"Error HTTP {resp.status_code}"

    def consultar_folio(self):
        if hasattr(self, "vista_folios"):
            self.vista_folios.consultar_folio()

    def al_seleccionar_concepto_cargo(self, opcion: str):
        if hasattr(self, "vista_folios"):
            self.vista_folios.al_seleccionar_concepto_cargo(opcion)

    def limpiar_form_cargo(self):
        if hasattr(self, "vista_folios"):
            self.vista_folios.limpiar_form_cargo()

    def registrar_cargo_manual(self):
        if hasattr(self, "vista_folios"):
            self.vista_folios.registrar_cargo_manual()

    def usar_saldo_pendiente_pago(self):
        if hasattr(self, "vista_folios"):
            self.vista_folios.usar_saldo_pendiente_pago()

    def limpiar_form_pago(self):
        if hasattr(self, "vista_folios"):
            self.vista_folios.limpiar_form_pago()

    def _ejecutar_post_pago(self, id_reserva: int, metodo_pago_str: str, monto: float) -> bool:
        if hasattr(self, "vista_folios"):
            return self.vista_folios._ejecutar_post_pago(id_reserva, metodo_pago_str, monto)
        return False

    def registrar_pago_folio(self):
        if hasattr(self, "vista_folios"):
            self.vista_folios.registrar_pago_folio()

    def abrir_simulador_terminal_pinpad(self, id_reserva: int, monto: float):
        return abrir_simulador_pinpad_modal(
            padre=self,
            id_reserva=id_reserva,
            monto=monto,
            al_autorizar=self._ejecutar_post_pago,
        )

    def limpiar_form_factura(self):
        if hasattr(self, "vista_folios"):
            self.vista_folios.limpiar_form_factura()

    def generar_pdf_factura(self, fac: dict) -> str:
        return generar_pdf_factura_rep(
            fac,
            ruta_logo_light=self.ruta_logo_light,
            ruta_logo_dark=self.ruta_logo_dark,
        )

    def timbrar_factura_gui(self):
        if hasattr(self, "vista_folios"):
            self.vista_folios.timbrar_factura_gui()

    # =========================================================================
    # MÓDULO 5: MANTENIMIENTO (DELEGACIÓN A TabMantenimientoView)
    # =========================================================================
    def construir_pestana_mantenimiento(self):
        tab_mant = self.tabview.tab("Mantenimiento")
        self.vista_mantenimiento = TabMantenimientoView(tab_mant, self)

    def cargar_tickets_mantenimiento(self, forzar_red: bool = True):
        if hasattr(self, "vista_mantenimiento"):
            self.vista_mantenimiento.cargar_tickets_mantenimiento(forzar_red=forzar_red)

    def renderizar_tickets_mantenimiento(self):
        if hasattr(self, "vista_mantenimiento"):
            self.vista_mantenimiento.renderizar_tickets_mantenimiento()

    def actualizar_combo_habitaciones_mantenimiento(self, lista_habs=None):
        if hasattr(self, "vista_mantenimiento"):
            self.vista_mantenimiento.actualizar_combo_habitaciones_mantenimiento(lista_habs=lista_habs)

    # =========================================================================
    # MÓDULO 6: PUNTO DE VENTA (DELEGACIÓN A TabPOSView)
    # =========================================================================
    def construir_pestana_pos(self):
        tab_pos = self.tabview.tab("Punto de Venta")
        self.vista_pos = TabPOSView(tab_pos, self)

    def actualizar_combo_habitaciones_pos(self, lista_res=None, forzar_red: bool = False):
        if hasattr(self, "vista_pos"):
            self.vista_pos.actualizar_combo_habitaciones_pos(lista_res=lista_res, forzar_red=forzar_red)

    def cargar_productos_pos(self, forzar_red: bool = True):
        if hasattr(self, "vista_pos"):
            self.vista_pos.cargar_productos_pos(forzar_red=forzar_red)

    def renderizar_productos_pos(self):
        if hasattr(self, "vista_pos"):
            self.vista_pos.renderizar_productos_pos()

    def renderizar_carrito_pos(self):
        if hasattr(self, "vista_pos"):
            self.vista_pos.renderizar_carrito_pos()

    def limpiar_comanda_pos(self):
        if hasattr(self, "vista_pos"):
            self.vista_pos.limpiar_comanda_pos()

    # =========================================================================
    # MÓDULO 7: REPORTES OPERATIVOS Y CORTE DE CAJA (DELEGACIÓN A TabReportesView)
    # =========================================================================
    def construir_pestana_reportes(self):
        tab_rep = self.tabview.tab("Reportes")
        self.vista_reportes = TabReportesView(tab_rep, self)

    def al_cambiar_periodo_reporte(self, opcion: str):
        if hasattr(self, "vista_reportes"):
            self.vista_reportes.al_cambiar_periodo_reporte(opcion)

    def cargar_reportes_gui(self):
        if hasattr(self, "vista_reportes"):
            self.vista_reportes.cargar_reportes_gui()

    def renderizar_reportes_gui(self):
        if hasattr(self, "vista_reportes"):
            self.vista_reportes.renderizar_reportes_gui()

    def renderizar_lista_financiera_reporte(self):
        if hasattr(self, "vista_reportes"):
            self.vista_reportes.renderizar_lista_financiera_reporte()

    def renderizar_lista_operativa_reporte(self):
        if hasattr(self, "vista_reportes"):
            self.vista_reportes.renderizar_lista_operativa_reporte()

    def exportar_corte_caja_pdf_gui(self):
        if hasattr(self, "vista_reportes"):
            self.vista_reportes.exportar_corte_caja_pdf_gui()
