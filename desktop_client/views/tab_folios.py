"""
Vista de la pestaña de Facturación y Folios - Estados de Cuenta, Cargos, Pagos y Emisión CFDI.
"""
import os
import requests
from tkinter import messagebox
import customtkinter as ctk

try:
    from modals import abrir_simulador_terminal_pinpad as abrir_simulador_pinpad_modal
except ImportError:
    from desktop_client.modals import abrir_simulador_terminal_pinpad as abrir_simulador_pinpad_modal

try:
    from reports import generar_pdf_factura as generar_pdf_factura_rep
except ImportError:
    from desktop_client.reports import generar_pdf_factura as generar_pdf_factura_rep


class TabFoliosView:
    def __init__(self, tab, app):
        self.tab = tab
        self.app = app
        self.saldo_folio_actual = 0.0

        # Referencias a widgets
        self.combo_folio_reserva = None
        self.entry_folio_reserva_id = None
        self.frame_resumen_folio = None
        self.label_resultado_folio = None
        self.label_saldo_destacado = None
        self.frame_movimientos_folio = None

        self.combo_concepto_cargo = None
        self.entry_cargo_desc = None
        self.entry_cargo_monto = None

        self.combo_metodo_pago = None
        self.entry_pago_monto = None

        self.entry_fac_rfc = None
        self.entry_fac_razon = None

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
        tab_fol = self.tab
        self.saldo_folio_actual = 0.0

        # Panel Izquierdo: Consulta y Estado de Cuenta Folio
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

        # Panel Derecho: Cargos Manuales, Registro de Pagos y Timbrado PAC
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

        self.actualizar_combo_reservas_folio(self.app.cache_reservas or None)

    def actualizar_combo_reservas_folio(self, lista_res=None):
        if not self.combo_folio_reserva or not self.combo_folio_reserva.winfo_exists():
            return
        try:
            if lista_res is None:
                if self.app.cache_reservas:
                    lista_res = self.app.cache_reservas
                else:
                    resp = self.app.http.get(f"{self.app.url_base}/reservas/")
                    if resp.status_code == 200:
                        lista_res = resp.json()
                        self.app.cache_reservas = lista_res
                    else:
                        return
            opciones = ["Seleccione una reserva..."]
            for r in lista_res:
                nom = (
                    r.get("nombre_huesped")
                    or getattr(self.app, "mapa_huespedes", {}).get(r.get("id_huesped"))
                    or f"Huésped #{r.get('id_huesped')}"
                )
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
        if self.combo_folio_reserva:
            self.combo_folio_reserva.set("Seleccione una reserva...")
        self._set_entry_readonly(self.entry_folio_reserva_id, "", "ID Reserva")
        self.saldo_folio_actual = 0.0
        if self.label_resultado_folio:
            self.label_resultado_folio.configure(
                text="Seleccione una reserva para visualizar su Estado de Cuenta Folio.",
                text_color="gray70"
            )
        if self.label_saldo_destacado:
            self.label_saldo_destacado.configure(text="Saldo Pendiente: $0.00", text_color="gray60")
        if self.frame_movimientos_folio and self.frame_movimientos_folio.winfo_exists():
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
            reserva_id = self.entry_folio_reserva_id.get().strip() if self.entry_folio_reserva_id else ""
            if not reserva_id:
                messagebox.showwarning("Advertencia", "Seleccione una reserva del menú desplegable.")
                return
            respuesta = self.app.http.get(f"{self.app.url_base}/reservas/{reserva_id}")
            if respuesta.status_code == 200:
                data = respuesta.json()
                nom_h = data.get("nombre_huesped") or f"Huésped #{data.get('id_huesped')}"
                rfc_h = data.get("rfc_huesped") or ""
                habs = data.get("numeros_habitaciones") or "Sin hab."
                total_cargos = float(data.get("total_cargos", 0.0))
                total_pagos = float(data.get("total_pagos", 0.0))
                saldo = float(data.get("saldo_pendiente", 0.0))
                self.saldo_folio_actual = saldo

                if self.combo_folio_reserva:
                    prefijo = f"Reserva #{data.get('id_reserva')} |"
                    for op in self.combo_folio_reserva.cget("values"):
                        if op.startswith(prefijo):
                            self.combo_folio_reserva.set(op)
                            break

                if self.entry_fac_rfc:
                    self.entry_fac_rfc.delete(0, "end")
                    if rfc_h:
                        self.entry_fac_rfc.insert(0, rfc_h)
                if self.entry_fac_razon:
                    self.entry_fac_razon.delete(0, "end")
                    if data.get("nombre_huesped"):
                        self.entry_fac_razon.insert(0, data.get("nombre_huesped"))

                texto = (
                    f"Reserva #{data.get('id_reserva')}  |  Huésped: {nom_h}  |  Habitación: {habs}\n"
                    f"Estado Reserva: {data.get('estado_reserva')}  |  Estado Folio: {data.get('estado_folio')}\n"
                    f"Estancia: {data.get('fecha_entrada')} al {data.get('fecha_salida')}\n"
                    f"Total Cargos: ${total_cargos:.2f}   |   Total Pagos: ${total_pagos:.2f}"
                )
                if self.label_resultado_folio:
                    self.label_resultado_folio.configure(text=texto, text_color="white")

                color_saldo = "#66BB6A" if saldo <= 0 else "#FFA726"
                estado_liq = "(LIQUIDADO)" if saldo <= 0 and total_cargos > 0 else ""
                if self.label_saldo_destacado:
                    self.label_saldo_destacado.configure(
                        text=f"Saldo Pendiente: ${saldo:.2f} {estado_liq}",
                        text_color=color_saldo
                    )

                if self.frame_movimientos_folio and self.frame_movimientos_folio.winfo_exists():
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
            if self.entry_cargo_desc:
                self.entry_cargo_desc.delete(0, "end")
                self.entry_cargo_desc.insert(0, opcion)

    def limpiar_form_cargo(self):
        if self.combo_concepto_cargo:
            self.combo_concepto_cargo.set("Seleccione concepto rápido (opcional)...")
        if self.entry_cargo_desc:
            self.entry_cargo_desc.delete(0, "end")
        if self.entry_cargo_monto:
            self.entry_cargo_monto.delete(0, "end")

    def registrar_cargo_manual(self):
        reserva_id = self.entry_folio_reserva_id.get().strip() if self.entry_folio_reserva_id else ""
        if not reserva_id:
            messagebox.showwarning("Reserva requerida", "Primero selecciona una reserva en el Estado de Cuenta Folio.")
            return
        desc = self.entry_cargo_desc.get().strip() if self.entry_cargo_desc else ""
        monto_txt = self.entry_cargo_monto.get().strip() if self.entry_cargo_monto else ""
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
            resp = self.app.http.post(f"{self.app.url_base}/finanzas/cargos", json=datos)
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
        if self.saldo_folio_actual <= 0:
            messagebox.showinfo("Sin saldo pendiente", "La reserva seleccionada no tiene saldo pendiente por cobrar.")
            return
        if self.entry_pago_monto:
            self.entry_pago_monto.delete(0, "end")
            self.entry_pago_monto.insert(0, f"{self.saldo_folio_actual:.2f}")

    def limpiar_form_pago(self):
        if self.combo_metodo_pago:
            self.combo_metodo_pago.set("Selecciona una opción")
        if self.entry_pago_monto:
            self.entry_pago_monto.delete(0, "end")

    def _ejecutar_post_pago(self, id_reserva: int, metodo_pago_str: str, monto: float) -> bool:
        try:
            datos = {
                "id_reserva": id_reserva,
                "metodo_pago": metodo_pago_str,
                "monto": monto,
            }
            resp = self.app.http.post(f"{self.app.url_base}/finanzas/pagos", json=datos)
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
        reserva_id = self.entry_folio_reserva_id.get().strip() if self.entry_folio_reserva_id else ""
        if not reserva_id:
            messagebox.showwarning("Reserva requerida", "Primero selecciona una reserva en el Estado de Cuenta Folio.")
            return
        metodo = self.combo_metodo_pago.get() if self.combo_metodo_pago else ""
        if metodo == "Selecciona una opción":
            messagebox.showwarning("Método de pago requerido", "Selecciona un método de pago (Efectivo o Tarjeta).")
            return
        monto_txt = self.entry_pago_monto.get().strip() if self.entry_pago_monto else ""
        if not monto_txt:
            messagebox.showwarning("Monto requerido", "Ingresa el monto a pagar o pulsa 'Usar Saldo Total'.")
            return
        try:
            monto = float(monto_txt)
            if monto <= 0:
                messagebox.showwarning("Monto inválido", "El monto a pagar debe ser mayor a $0.00.")
                return
            if monto > round(self.saldo_folio_actual + 0.01, 2):
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
        return abrir_simulador_pinpad_modal(
            padre=self.app,
            id_reserva=id_reserva,
            monto=monto,
            al_autorizar=self._ejecutar_post_pago,
        )

    def limpiar_form_factura(self):
        if self.entry_fac_rfc:
            self.entry_fac_rfc.delete(0, "end")
        if self.entry_fac_razon:
            self.entry_fac_razon.delete(0, "end")

    def generar_pdf_factura(self, fac: dict) -> str:
        return generar_pdf_factura_rep(
            fac,
            ruta_logo_light=self.app.ruta_logo_light,
            ruta_logo_dark=self.app.ruta_logo_dark,
        )

    def timbrar_factura_gui(self):
        reserva_id = self.entry_folio_reserva_id.get().strip() if self.entry_folio_reserva_id else ""
        if not reserva_id:
            messagebox.showwarning("Reserva requerida", "Primero selecciona una reserva en el Estado de Cuenta Folio.")
            return
        rfc = self.entry_fac_rfc.get().strip() if self.entry_fac_rfc else ""
        if not rfc:
            messagebox.showwarning("RFC requerido", "Ingresa el RFC del cliente para timbrar la factura.")
            return
        razon = (self.entry_fac_razon.get().strip() if self.entry_fac_razon else "") or "PÚBLICO EN GENERAL"
        try:
            datos = {
                "id_reserva": int(reserva_id),
                "rfc_cliente": rfc,
                "razon_social": razon,
            }
            resp = self.app.http.post(f"{self.app.url_base}/finanzas/facturar", json=datos)
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
                if hasattr(self.app, "cargar_huespedes"):
                    self.app.cargar_huespedes(forzar_red=True)
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
