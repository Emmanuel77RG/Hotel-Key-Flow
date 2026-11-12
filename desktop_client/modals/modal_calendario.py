"""
Modal interactivo de selección de fecha tipo mini-calendario.
"""
import calendar
from datetime import date, datetime, timedelta
import customtkinter as ctk


def abrir_mini_calendario(
    padre,
    entry_destino,
    titulo: str = "Seleccionar Fecha",
    es_entrada: bool = True,
    al_seleccionar=None,
    entry_salida_sugerida=None,
):
    """
    Despliega una ventana emergente modal con navegación mensual interactiva.
    Inserta la fecha elegida (YYYY-MM-DD) en `entry_destino`.
    """
    modal = ctk.CTkToplevel(padre)
    modal.title(titulo)
    modal.geometry("320x330")
    modal.resizable(False, False)
    modal.transient(padre)

    hoy = date.today()
    valor_actual = entry_destino.get().strip() if hasattr(entry_destino, "get") else ""
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

    def set_entry_text(entry, valor: str):
        if hasattr(entry, "configure") and hasattr(entry, "delete"):
            entry.configure(state="normal")
            entry.delete(0, "end")
            entry.insert(0, valor)
            entry.configure(state="readonly")

    def seleccionar_dia(dia_num: int):
        fecha_elegida = date(estado_cal["anio"], estado_cal["mes"], dia_num)
        set_entry_text(entry_destino, fecha_elegida.strftime("%Y-%m-%d"))

        # Si eligió fecha de entrada y la salida está vacía o es menor/igual, sugerir +1 noche
        if es_entrada and entry_salida_sugerida:
            sal_txt = entry_salida_sugerida.get().strip()
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
                set_entry_text(entry_salida_sugerida, manana.strftime("%Y-%m-%d"))

        modal.destroy()
        if callable(al_seleccionar):
            al_seleccionar()

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
    modal.after(20, lambda: (modal.lift(), modal.focus_force(), modal.grab_set()))
    return modal
