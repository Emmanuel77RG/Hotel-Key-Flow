"""
Componente reutilizable de paginación para CustomTkinter.
Permite navegar entre páginas de datos con botones y texto informativo,
evitando la sobrecarga del Canvas y visual tearing.
"""
import customtkinter as ctk


def crear_controles_paginacion(
    frame_contenedor,
    pagina_actual: int,
    total_items: int,
    items_por_pagina: int,
    callback_cambio_pagina,
) -> tuple[int, int]:
    """
    Limpia y construye una barra de paginación compacta y estilizada en 'frame_contenedor'.
    Retorna (inicio_slice, fin_slice) para renderizar únicamente ese subconjunto de datos.
    """
    if frame_contenedor is None:
        return 0, total_items

    for w in frame_contenedor.winfo_children():
        w.destroy()

    if total_items == 0:
        return 0, 0

    total_paginas = max(1, (total_items + items_por_pagina - 1) // items_por_pagina)
    pagina = max(1, min(pagina_actual, total_paginas))
    inicio = (pagina - 1) * items_por_pagina
    fin = min(inicio + items_por_pagina, total_items)

    if total_paginas > 1:
        frame_barra = ctk.CTkFrame(frame_contenedor, fg_color="transparent")
        frame_barra.pack(fill="x", pady=2)

        btn_ant = ctk.CTkButton(
            frame_barra,
            text="◀ Anterior",
            width=75,
            height=22,
            font=ctk.CTkFont(size=11),
            fg_color="#1F6AA5" if pagina > 1 else "gray30",
            state="normal" if pagina > 1 else "disabled",
            command=lambda: callback_cambio_pagina(pagina - 1),
        )
        btn_ant.pack(side="left", padx=4)

        lbl_info = ctk.CTkLabel(
            frame_barra,
            text=f"Página {pagina} de {total_paginas}  ({inicio + 1}–{fin} de {total_items})",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="gray85",
        )
        lbl_info.pack(side="left", expand=True)

        btn_sig = ctk.CTkButton(
            frame_barra,
            text="Siguiente ▶",
            width=75,
            height=22,
            font=ctk.CTkFont(size=11),
            fg_color="#1F6AA5" if pagina < total_paginas else "gray30",
            state="normal" if pagina < total_paginas else "disabled",
            command=lambda: callback_cambio_pagina(pagina + 1),
        )
        btn_sig.pack(side="right", padx=4)
    else:
        lbl_info = ctk.CTkLabel(
            frame_contenedor,
            text=f"Mostrando {total_items} registro(s)",
            font=ctk.CTkFont(size=10),
            text_color="gray60",
        )
        lbl_info.pack(pady=1)

    return inicio, fin
