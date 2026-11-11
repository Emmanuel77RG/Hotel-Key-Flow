"""
Vista de la pestaña de Reportes Financieros, Operativos y Corte de Caja.
"""
from datetime import date
import os
import requests
from tkinter import messagebox
import customtkinter as ctk

try:
    from reports import generar_pdf_corte_caja
    from widgets import crear_controles_paginacion
    from modals import abrir_mini_calendario
except ImportError:
    from desktop_client.reports import generar_pdf_corte_caja
    from desktop_client.widgets import crear_controles_paginacion
    from desktop_client.modals import abrir_mini_calendario


class TabReportesView:
    def __init__(self, tab, app):
        self.tab = tab
        self.app = app
        self.pag_rep_fin = 1
        self.pag_rep_op = 1
        self.ITEMS_POR_PAGINA = getattr(app, "ITEMS_POR_PAGINA", 15)

        self.construir()

    def construir(self):
        # Barra Superior de Filtros y Acciones Ejecutivas
        frame_top_rep = ctk.CTkFrame(self.tab, fg_color="transparent")
        frame_top_rep.pack(fill="x", padx=12, pady=(8, 4))

        ctk.CTkLabel(
            frame_top_rep,
            text="Rendimiento Financiero, Operativo y Corte de Caja",
            font=ctk.CTkFont(size=17, weight="bold")
        ).pack(side="left")

        ctk.CTkButton(
            frame_top_rep,
            text="📄 Exportar Corte de Caja PDF",
            width=205,
            height=28,
            fg_color="#2E7D32",
            hover_color="#1b5e20",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.exportar_corte_caja_pdf_gui
        ).pack(side="right", padx=(4, 0))

        ctk.CTkButton(
            frame_top_rep,
            text="🔄 Actualizar",
            width=105,
            height=28,
            command=self.cargar_reportes_gui
        ).pack(side="right", padx=4)

        # Barra de Filtros de Fecha y Turno
        frame_filtros_rep = ctk.CTkFrame(self.tab, fg_color="transparent")
        frame_filtros_rep.pack(fill="x", padx=12, pady=(0, 4))

        ctk.CTkLabel(
            frame_filtros_rep,
            text="Periodo de Corte:",
            font=ctk.CTkFont(size=12),
            text_color="gray75"
        ).pack(side="left", padx=(0, 6))

        self.combo_rep_periodo = ctk.CTkOptionMenu(
            frame_filtros_rep,
            width=165,
            height=26,
            values=["Todo el historial", "Corte de Hoy", "Fecha específica"],
            command=self.al_cambiar_periodo_reporte
        )
        self.combo_rep_periodo.set("Todo el historial")
        self.combo_rep_periodo.pack(side="left", padx=(0, 6))

        self.entry_rep_fecha = ctk.CTkEntry(
            frame_filtros_rep,
            width=110,
            height=26,
            placeholder_text="AAAA-MM-DD",
            state="readonly"
        )
        self.entry_rep_fecha.pack(side="left", padx=2)

        ctk.CTkButton(
            frame_filtros_rep,
            text="📅",
            width=32,
            height=26,
            fg_color="#1F6AA5",
            command=lambda: (
                self.combo_rep_periodo.set("Fecha específica"),
                abrir_mini_calendario(
                    padre=self.app,
                    entry_destino=self.entry_rep_fecha,
                    titulo="Fecha de Corte de Caja",
                    es_entrada=False,
                    al_seleccionar=self.cargar_reportes_gui
                )
            )
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            frame_filtros_rep,
            text="Aplicar Fecha",
            width=95,
            height=26,
            command=self.cargar_reportes_gui
        ).pack(side="left", padx=(4, 12))

        self.var_rep_mi_turno = ctk.BooleanVar(value=False)
        self.chk_rep_mi_turno = ctk.CTkCheckBox(
            frame_filtros_rep,
            text="Solo pagos de mi turno (Cajero actual)",
            variable=self.var_rep_mi_turno,
            font=ctk.CTkFont(size=12),
            checkbox_width=18,
            checkbox_height=18,
            command=self.cargar_reportes_gui
        )
        self.chk_rep_mi_turno.pack(side="left", padx=6)

        self.lbl_rep_cajero_info = ctk.CTkLabel(
            frame_filtros_rep,
            text="",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#90CAF9"
        )
        self.lbl_rep_cajero_info.pack(side="right")

        # Fila de 5 Tarjetas KPI Ejecutivas
        frame_kpis_rep = ctk.CTkFrame(self.tab, fg_color="transparent")
        frame_kpis_rep.pack(fill="x", padx=10, pady=3)

        def crear_kpi_rep(parent, titulo, color_borde):
            box = ctk.CTkFrame(parent, border_width=1, border_color=color_borde, corner_radius=8)
            box.pack(side="left", fill="x", expand=True, padx=3, pady=2)
            lbl_val = ctk.CTkLabel(box, text="$0.00", font=ctk.CTkFont(size=15, weight="bold"), text_color=color_borde)
            lbl_val.pack(pady=(4, 0))
            ctk.CTkLabel(box, text=titulo, font=ctk.CTkFont(size=10), text_color="gray75").pack(pady=(0, 4))
            return lbl_val

        self.kpi_rep_ocupacion = crear_kpi_rep(frame_kpis_rep, "% Ocupación Hotel", "#42A5F5")
        self.kpi_rep_recaudado = crear_kpi_rep(frame_kpis_rep, "Total Cobrado (Corte)", "#66BB6A")
        self.kpi_rep_efectivo = crear_kpi_rep(frame_kpis_rep, "Efectivo en Caja", "#81C784")
        self.kpi_rep_tarjeta = crear_kpi_rep(frame_kpis_rep, "Terminal PinPad (Tarjeta)", "#29B6F6")
        self.kpi_rep_por_cobrar = crear_kpi_rep(frame_kpis_rep, "Por Cobrar en Folios", "#FFA726")

        # Cuerpo Dividido en 2 Columnas
        frame_cuerpo_rep = ctk.CTkFrame(self.tab, fg_color="transparent")
        frame_cuerpo_rep.pack(fill="both", expand=True, padx=10, pady=(2, 8))

        # --- Columna Izquierda: Auditoría Financiera y Corte de Caja ---
        frame_izq_rep = ctk.CTkFrame(frame_cuerpo_rep)
        frame_izq_rep.pack(side="left", fill="both", expand=True, padx=(0, 5))

        self.lbl_rep_resumen_cargos = ctk.CTkLabel(
            frame_izq_rep,
            text="Cargos Hospedaje: $0.00   |   Consumos POS: $0.00   |   Total Cargos: $0.00",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#FFCC80"
        )
        self.lbl_rep_resumen_cargos.pack(pady=(6, 2))

        opciones_fin = ["Pagos Recibidos (Corte de Caja)", "Cargos Generados (Hospedaje y POS)"]
        if getattr(self.app, "id_rol", None) == 1:
            opciones_fin.append("Relación de Transacciones (Auditoría)")

        self.seg_vista_finanzas = ctk.CTkSegmentedButton(
            frame_izq_rep,
            values=opciones_fin,
            command=lambda _v: (setattr(self, "pag_rep_fin", 1), self.renderizar_lista_financiera_reporte())
        )
        self.seg_vista_finanzas.set("Pagos Recibidos (Corte de Caja)")
        self.seg_vista_finanzas.pack(fill="x", padx=10, pady=4)

        self.frame_rep_finanzas = ctk.CTkScrollableFrame(frame_izq_rep)
        self.frame_rep_finanzas.pack(fill="both", expand=True, padx=8, pady=(2, 4))

        self.frame_pag_rep_fin = ctk.CTkFrame(frame_izq_rep, fg_color="transparent")
        self.frame_pag_rep_fin.pack(fill="x", padx=8, pady=(0, 6))

        # --- Columna Derecha: Rendimiento Operativo, Llegadas y Salidas ---
        frame_der_rep = ctk.CTkFrame(frame_cuerpo_rep)
        frame_der_rep.pack(side="right", fill="both", expand=True, padx=(5, 0))

        self.lbl_rep_estado_habs = ctk.CTkLabel(
            frame_der_rep,
            text="Habitaciones: 0 Ocupadas | 0 Limpias | 0 Sucias | 0 En Limpieza | 0 Mantenimiento",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#90CAF9"
        )
        self.lbl_rep_estado_habs.pack(pady=(6, 1))

        self.lbl_rep_estado_mant = ctk.CTkLabel(
            frame_der_rep,
            text="Mantenimiento: 0 Pendientes | 0 En Reparación | 0 Críticos Activos | 0 Resueltos",
            font=ctk.CTkFont(size=11),
            text_color="gray75"
        )
        self.lbl_rep_estado_mant.pack(pady=(0, 3))

        self.seg_vista_operativa = ctk.CTkSegmentedButton(
            frame_der_rep,
            values=["Llegadas y Salidas (Check-in / Check-out)", "Llegadas (Check-in)", "Salidas (Check-out)"],
            command=lambda _v: (setattr(self, "pag_rep_op", 1), self.renderizar_lista_operativa_reporte())
        )
        self.seg_vista_operativa.set("Llegadas y Salidas (Check-in / Check-out)")
        self.seg_vista_operativa.pack(fill="x", padx=10, pady=4)

        self.frame_rep_operativo = ctk.CTkScrollableFrame(frame_der_rep)
        self.frame_rep_operativo.pack(fill="both", expand=True, padx=8, pady=(2, 4))

        self.frame_pag_rep_op = ctk.CTkFrame(frame_der_rep, fg_color="transparent")
        self.frame_pag_rep_op.pack(fill="x", padx=8, pady=(0, 6))

        self.cargar_reportes_gui()

    def al_cambiar_periodo_reporte(self, opcion: str):
        if opcion == "Todo el historial":
            self.app._set_entry_readonly(self.entry_rep_fecha, "", "AAAA-MM-DD")
            self.cargar_reportes_gui()
        elif opcion == "Corte de Hoy":
            hoy_str = date.today().strftime("%Y-%m-%d")
            self.app._set_entry_readonly(self.entry_rep_fecha, hoy_str, "AAAA-MM-DD")
            self.cargar_reportes_gui()
        elif opcion == "Fecha específica":
            if not self.entry_rep_fecha.get().strip():
                hoy_str = date.today().strftime("%Y-%m-%d")
                self.app._set_entry_readonly(self.entry_rep_fecha, hoy_str, "AAAA-MM-DD")
            self.cargar_reportes_gui()

    def cargar_reportes_gui(self):
        if not hasattr(self, "kpi_rep_ocupacion"):
            return
        periodo = self.combo_rep_periodo.get()
        fecha_param = "todos"
        if periodo == "Corte de Hoy":
            fecha_param = date.today().strftime("%Y-%m-%d")
            self.app._set_entry_readonly(self.entry_rep_fecha, fecha_param, "AAAA-MM-DD")
        elif periodo == "Fecha específica":
            f_txt = self.entry_rep_fecha.get().strip()
            fecha_param = f_txt if f_txt else "todos"

        solo_turno = bool(self.var_rep_mi_turno.get())
        try:
            resp = self.app.http.get(
                f"{self.app.url_base}/reportes/resumen",
                params={"fecha": fecha_param, "solo_mi_turno": solo_turno},
            )
            if resp.status_code == 200:
                self.app.cache_reporte = resp.json()
                self.renderizar_reportes_gui()
            else:
                messagebox.showerror("Error en Reporte", self.app._extraer_detalle_error(resp))
        except requests.exceptions.ConnectionError:
            pass
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def renderizar_reportes_gui(self):
        data = self.app.cache_reporte
        if not data:
            return

        cajero = data.get("cajero_actual", {})
        filtro_f = data.get("filtro_fecha", "Todo el historial")
        self.lbl_rep_cajero_info.configure(
            text=f"Operador: {cajero.get('nombre', 'Personal')}  |  Corte: {filtro_f}"
        )

        ocup = data.get("ocupacion", {})
        fin = data.get("finanzas", {})
        mant = data.get("mantenimiento", {})

        porc = float(ocup.get("porcentaje_ocupacion", 0.0))
        ocup_cnt = ocup.get("ocupadas", 0)
        tot_habs = ocup.get("total_habitaciones", 0)
        self.kpi_rep_ocupacion.configure(text=f"{porc:.1f}% ({ocup_cnt}/{tot_habs})")

        self.kpi_rep_recaudado.configure(text=f"${float(fin.get('total_recaudado', 0.0)):.2f}")
        self.kpi_rep_efectivo.configure(text=f"${float(fin.get('total_efectivo', 0.0)):.2f}")
        self.kpi_rep_tarjeta.configure(text=f"${float(fin.get('total_tarjeta', 0.0)):.2f}")
        self.kpi_rep_por_cobrar.configure(text=f"${float(fin.get('saldo_por_cobrar_folios', 0.0)):.2f}")

        self.lbl_rep_resumen_cargos.configure(
            text=(
                f"Cargos Hospedaje: ${float(fin.get('cargos_hospedaje', 0.0)):.2f}   |   "
                f"Consumos POS: ${float(fin.get('cargos_pos', 0.0)):.2f}   |   "
                f"Total Cargos: ${float(fin.get('total_cargos_periodo', 0.0)):.2f}"
            )
        )

        self.lbl_rep_estado_habs.configure(
            text=(
                f"Habitaciones: {ocup.get('ocupadas', 0)} Ocupadas | "
                f"{ocup.get('limpias', 0)} Limpias | "
                f"{ocup.get('sucias', 0)} Sucias | "
                f"{ocup.get('en_limpieza', 0)} En Limpieza | "
                f"{ocup.get('mantenimiento', 0)} Mantenimiento"
            )
        )

        self.lbl_rep_estado_mant.configure(
            text=(
                f"Tickets Mantenimiento: {mant.get('pendientes', 0)} Pendientes | "
                f"{mant.get('en_reparacion', 0)} En Reparación | "
                f"{mant.get('criticos_activos', 0)} Críticos Activos | "
                f"{mant.get('resueltos', 0)} Resueltos"
            )
        )

        self.renderizar_lista_financiera_reporte()
        self.renderizar_lista_operativa_reporte()

    def _cambiar_pagina_rep_fin(self, nueva_pag: int):
        self.pag_rep_fin = nueva_pag
        self.renderizar_lista_financiera_reporte()

    def _cambiar_pagina_rep_op(self, nueva_pag: int):
        self.pag_rep_op = nueva_pag
        self.renderizar_lista_operativa_reporte()

    def renderizar_lista_financiera_reporte(self):
        if not hasattr(self, "frame_rep_finanzas") or not self.app.cache_reporte:
            return
        for w in self.frame_rep_finanzas.winfo_children():
            w.destroy()

        vista = self.seg_vista_finanzas.get()
        if vista == "Pagos Recibidos (Corte de Caja)":
            pagos = self.app.cache_reporte.get("pagos_detalle", [])
            if not pagos:
                if hasattr(self, "frame_pag_rep_fin"):
                    for w in self.frame_pag_rep_fin.winfo_children():
                        w.destroy()
                ctk.CTkLabel(
                    self.frame_rep_finanzas,
                    text="No hay pagos registrados para el periodo o filtro seleccionado.",
                    text_color="gray60",
                    font=ctk.CTkFont(size=12)
                ).pack(pady=25)
                return

            inicio, fin = crear_controles_paginacion(
                self.frame_pag_rep_fin,
                self.pag_rep_fin,
                len(pagos),
                self.ITEMS_POR_PAGINA,
                self._cambiar_pagina_rep_fin,
            )

            for p in pagos[inicio:fin]:
                card = ctk.CTkFrame(self.frame_rep_finanzas)
                card.pack(fill="x", padx=3, pady=3)

                info = ctk.CTkFrame(card, fg_color="transparent")
                info.pack(side="left", fill="x", expand=True, padx=8, pady=5)

                metodo = p.get("metodo_pago", "Efectivo")
                es_efec = "efectivo" in metodo.lower()
                color_met = "#81C784" if es_efec else "#29B6F6"

                ctk.CTkLabel(
                    info,
                    text=f"Pago #{p['id_pago']}  |  Folio #{p['id_reserva']} (Hab. {p['habitaciones']})  |  {p['huesped']}",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    anchor="w"
                ).pack(fill="x")

                ctk.CTkLabel(
                    info,
                    text=f"Método: {metodo}   |   Cajero: {p.get('cajero', '')}   |   Fecha: {p.get('fecha_creacion', '')}",
                    font=ctk.CTkFont(size=10),
                    text_color=color_met,
                    anchor="w"
                ).pack(fill="x")

                ctk.CTkLabel(
                    card,
                    text=f"+ ${float(p.get('monto', 0.0)):.2f}",
                    font=ctk.CTkFont(size=13, weight="bold"),
                    text_color="#66BB6A"
                ).pack(side="right", padx=10, pady=5)
        elif vista == "Relación de Transacciones (Auditoría)":
            pagos = self.app.cache_reporte.get("pagos_detalle", [])
            if not pagos:
                if hasattr(self, "frame_pag_rep_fin"):
                    for w in self.frame_pag_rep_fin.winfo_children():
                        w.destroy()
                ctk.CTkLabel(
                    self.frame_rep_finanzas,
                    text="No hay transacciones registradas para el periodo o filtro seleccionado.",
                    text_color="gray60",
                    font=ctk.CTkFont(size=12)
                ).pack(pady=25)
                return

            inicio, fin = crear_controles_paginacion(
                self.frame_pag_rep_fin,
                self.pag_rep_fin,
                len(pagos),
                self.ITEMS_POR_PAGINA,
                self._cambiar_pagina_rep_fin,
            )

            # Barra resumen de auditoría
            total_tx = len(pagos)
            monto_acumulado = sum(float(p.get("monto", 0.0)) for p in pagos)
            frame_header_audit = ctk.CTkFrame(self.frame_rep_finanzas, fg_color="#1E293B", corner_radius=6)
            frame_header_audit.pack(fill="x", padx=3, pady=(2, 6))
            ctk.CTkLabel(
                frame_header_audit,
                text=f"📋 Relación de Auditoría: {total_tx} transacciones conciliadas   |   Monto Acumulado: ${monto_acumulado:,.2f}",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color="#38BDF8"
            ).pack(pady=5)

            for p in pagos[inicio:fin]:
                card = ctk.CTkFrame(self.frame_rep_finanzas)
                card.pack(fill="x", padx=3, pady=3)

                info = ctk.CTkFrame(card, fg_color="transparent")
                info.pack(side="left", fill="x", expand=True, padx=8, pady=5)

                metodo = p.get("metodo_pago", "Efectivo")
                es_efec = "efectivo" in metodo.lower()
                color_met = "#81C784" if es_efec else "#38BDF8"

                ctk.CTkLabel(
                    info,
                    text=f"Transacción #{p['id_pago']}  |  Folio #{p['id_reserva']} (Hab. {p['habitaciones']})  |  {p['huesped']}",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    anchor="w"
                ).pack(fill="x")

                ctk.CTkLabel(
                    info,
                    text=f"Cajero: {p.get('cajero', '')}   |   Fecha: {p.get('fecha_creacion', '')}   |   Método: {metodo}",
                    font=ctk.CTkFont(size=10),
                    text_color=color_met,
                    anchor="w"
                ).pack(fill="x")

                token_completo = p.get("token_auditoria") or metodo
                ctk.CTkLabel(
                    info,
                    text=f"🔑 Conciliación / Token Bancario: {token_completo}",
                    font=ctk.CTkFont(size=10, weight="bold"),
                    text_color="#FBBF24" if not es_efec else "gray70",
                    anchor="w"
                ).pack(fill="x")

                ctk.CTkLabel(
                    card,
                    text=f"+ ${float(p.get('monto', 0.0)):.2f}",
                    font=ctk.CTkFont(size=13, weight="bold"),
                    text_color="#66BB6A"
                ).pack(side="right", padx=10, pady=5)
        else:
            cargos = self.app.cache_reporte.get("cargos_detalle", [])
            if not cargos:
                if hasattr(self, "frame_pag_rep_fin"):
                    for w in self.frame_pag_rep_fin.winfo_children():
                        w.destroy()
                ctk.CTkLabel(
                    self.frame_rep_finanzas,
                    text="No hay cargos registrados para el periodo seleccionado.",
                    text_color="gray60",
                    font=ctk.CTkFont(size=12)
                ).pack(pady=25)
                return

            inicio, fin = crear_controles_paginacion(
                self.frame_pag_rep_fin,
                self.pag_rep_fin,
                len(cargos),
                self.ITEMS_POR_PAGINA,
                self._cambiar_pagina_rep_fin,
            )

            for c in cargos[inicio:fin]:
                card = ctk.CTkFrame(self.frame_rep_finanzas)
                card.pack(fill="x", padx=3, pady=3)

                info = ctk.CTkFrame(card, fg_color="transparent")
                info.pack(side="left", fill="x", expand=True, padx=8, pady=5)

                es_pos = bool(c.get("es_pos"))
                origen_tag = "PUNTO DE VENTA" if es_pos else "HOSPEDAJE / EXTRA"
                color_tag = "#CE93D8" if es_pos else "#FFCC80"

                ctk.CTkLabel(
                    info,
                    text=f"Cargo #{c['id_cargo']} [{origen_tag}]  |  Folio #{c['id_reserva']} (Hab. {c['habitaciones']})  |  {c['huesped']}",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color=color_tag,
                    anchor="w"
                ).pack(fill="x")

                ctk.CTkLabel(
                    info,
                    text=f"{c.get('descripcion', '')}   |   Fecha: {c.get('fecha_creacion', '')}",
                    font=ctk.CTkFont(size=10),
                    text_color="gray75",
                    anchor="w"
                ).pack(fill="x")

                ctk.CTkLabel(
                    card,
                    text=f"${float(c.get('monto', 0.0)):.2f}",
                    font=ctk.CTkFont(size=13, weight="bold"),
                    text_color="#FF8A65"
                ).pack(side="right", padx=10, pady=5)

    def renderizar_lista_operativa_reporte(self):
        if not hasattr(self, "frame_rep_operativo") or not self.app.cache_reporte:
            return
        for w in self.frame_rep_operativo.winfo_children():
            w.destroy()

        movs = self.app.cache_reporte.get("movimientos_operativos", {})
        llegadas = movs.get("llegadas", [])
        salidas = movs.get("salidas", [])
        vista = self.seg_vista_operativa.get()

        elementos_render = []
        if vista in ("Llegadas y Salidas (Check-in / Check-out)", "Llegadas (Check-in)"):
            for r in llegadas:
                elementos_render.append(("LLEGADA / CHECK-IN", "#4FC3F7", r))
        if vista in ("Llegadas y Salidas (Check-in / Check-out)", "Salidas (Check-out)"):
            for r in salidas:
                elementos_render.append(("SALIDA / CHECK-OUT", "#FFB74D", r))

        if not elementos_render:
            if hasattr(self, "frame_pag_rep_op"):
                for w in self.frame_pag_rep_op.winfo_children():
                    w.destroy()
            ctk.CTkLabel(
                self.frame_rep_operativo,
                text="No hay movimientos de llegadas o salidas para la fecha seleccionada.",
                text_color="gray60",
                font=ctk.CTkFont(size=12)
            ).pack(pady=25)
            return

        inicio, fin = crear_controles_paginacion(
            self.frame_pag_rep_op,
            self.pag_rep_op,
            len(elementos_render),
            self.ITEMS_POR_PAGINA,
            self._cambiar_pagina_rep_op,
        )

        for tipo_mov, color_mov, r in elementos_render[inicio:fin]:
            card = ctk.CTkFrame(self.frame_rep_operativo)
            card.pack(fill="x", padx=3, pady=3)

            info = ctk.CTkFrame(card, fg_color="transparent")
            info.pack(side="left", fill="x", expand=True, padx=8, pady=5)

            ctk.CTkLabel(
                info,
                text=f"[{tipo_mov}]  Hab. {r.get('habitaciones')}  |  {r.get('huesped')}  (Reserva #{r['id_reserva']})",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=color_mov,
                anchor="w"
            ).pack(fill="x")

            ctk.CTkLabel(
                info,
                text=(
                    f"Entrada: {r.get('fecha_entrada')}  ->  Salida: {r.get('fecha_salida')}   |   "
                    f"Estado: {r.get('estado_reserva')}   |   Folio: {r.get('estado_folio')}"
                ),
                font=ctk.CTkFont(size=10),
                text_color="gray75",
                anchor="w"
            ).pack(fill="x")

            ctk.CTkButton(
                card,
                text="Ver Folio",
                width=74,
                height=24,
                command=lambda rid=r["id_reserva"]: (
                    self.app.seleccionar_reserva_id(rid),
                    self.app.tabview.set("Facturación y Folios")
                )
            ).pack(side="right", padx=8, pady=5)

    def exportar_corte_caja_pdf_gui(self):
        if not self.app.cache_reporte:
            self.cargar_reportes_gui()
        if not self.app.cache_reporte:
            messagebox.showwarning("Sin datos", "No se pudo obtener la información del reporte para exportar.")
            return
        try:
            ruta_pdf = generar_pdf_corte_caja(
                self.app.cache_reporte,
                ruta_logo_light=self.app.ruta_logo_light,
                ruta_logo_dark=self.app.ruta_logo_dark,
            )
            try:
                os.startfile(ruta_pdf)
            except Exception:
                pass
            fin = self.app.cache_reporte.get("finanzas", {})
            messagebox.showinfo(
                "Corte de Caja Exportado en PDF",
                f"El reporte ejecutivo y corte de caja se generó exitosamente.\n\n"
                f"Periodo: {self.app.cache_reporte.get('filtro_fecha')}\n"
                f"Total Recaudado: ${float(fin.get('total_recaudado', 0.0)):.2f} MXN\n"
                f"Efectivo: ${float(fin.get('total_efectivo', 0.0)):.2f} MXN\n"
                f"Terminal PinPad: ${float(fin.get('total_tarjeta', 0.0)):.2f} MXN\n\n"
                f"Archivo guardado en:\n{ruta_pdf}"
            )
        except Exception as e:
            messagebox.showerror("Error al generar PDF", str(e))
