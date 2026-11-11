"""
Modal interactivo para la simulación de cobro en terminal bancaria PinPad.
Soporta pago Contactless (NFC) y Chip + NIP con tokenización simulada.
"""
import uuid
import customtkinter as ctk


def abrir_simulador_terminal_pinpad(padre, id_reserva: int, monto: float, al_autorizar):
    """
    Despliega la terminal PinPad simulada.
    Llama a `al_autorizar(id_reserva, metodo_token, monto)` al completar el cobro.
    """
    modal = ctk.CTkToplevel(padre)
    modal.title("Terminal Bancaria PinPad")
    modal.geometry("390x430")
    modal.resizable(False, False)
    modal.transient(padre)

    ctk.CTkLabel(
        modal,
        text="Terminal Bancaria PinPad",
        font=ctk.CTkFont(size=18, weight="bold")
    ).pack(pady=(12, 4))

    ctk.CTkLabel(
        modal,
        text="Entregue la terminal al huésped para autorizar el cargo",
        font=ctk.CTkFont(size=12),
        text_color="gray70"
    ).pack(pady=(0, 8))

    # Pantalla LCD simulada de la terminal
    frame_lcd = ctk.CTkFrame(modal, fg_color="#0D1B2A", corner_radius=10, border_width=2, border_color="#415A77")
    frame_lcd.pack(fill="x", padx=22, pady=6)

    ctk.CTkLabel(
        frame_lcd,
        text=f"TOTAL A COBRAR: ${monto:.2f} MXN",
        font=ctk.CTkFont(size=17, weight="bold"),
        text_color="#00E676"
    ).pack(pady=(10, 4))

    lbl_estado_lcd = ctk.CTkLabel(
        frame_lcd,
        text="Acerque, inserte o deslice su tarjeta...",
        font=ctk.CTkFont(size=12, weight="bold"),
        text_color="#90CAF9",
        wraplength=320
    )
    lbl_estado_lcd.pack(pady=(2, 10))

    # Frame dinámico para el ingreso de NIP (oculto inicialmente)
    frame_nip = ctk.CTkFrame(modal, fg_color="transparent")
    entry_nip = ctk.CTkEntry(
        frame_nip,
        width=140,
        placeholder_text="NIP (4 dígitos)",
        show="*",
        justify="center",
        font=ctk.CTkFont(size=15, weight="bold")
    )
    entry_nip.pack(side="left", padx=6)

    def confirmar_nip():
        nip = entry_nip.get().strip()
        if len(nip) != 4 or not nip.isdigit():
            lbl_estado_lcd.configure(
                text="⚠️ NIP inválido: Ingrese exactamente 4 dígitos numéricos.",
                text_color="#FFB74D"
            )
            return
        token_corto = uuid.uuid4().hex[:8].upper()
        metodo_token = f"Tarjeta Chip ****7390 (Tok: {token_corto})"
        lbl_estado_lcd.configure(
            text=f"✅ APROBADA CON NIP\nAutorización: ****{token_corto[-4:]}",
            text_color="#00E676"
        )
        modal.update_idletasks()
        modal.destroy()
        if callable(al_autorizar):
            al_autorizar(id_reserva, metodo_token, monto)

    ctk.CTkButton(
        frame_nip,
        text="Autorizar NIP",
        width=120,
        fg_color="#2E7D32",
        hover_color="#1b5e20",
        command=confirmar_nip
    ).pack(side="left", padx=4)

    def pago_contactless():
        token_corto = uuid.uuid4().hex[:8].upper()
        metodo_token = f"Tarjeta NFC ****4821 (Tok: {token_corto})"
        lbl_estado_lcd.configure(
            text=f"✅ APROBADA SIN CONTACTO (NFC)\nAutorización: ****{token_corto[-4:]}",
            text_color="#00E676"
        )
        modal.update_idletasks()
        modal.destroy()
        if callable(al_autorizar):
            al_autorizar(id_reserva, metodo_token, monto)

    def mostrar_modo_chip():
        lbl_estado_lcd.configure(
            text="💳 Tarjeta con Chip leída.\nCliente: Ingrese su NIP de 4 dígitos y pulse Autorizar.",
            text_color="#FFF59D"
        )
        frame_nip.pack(pady=6)
        entry_nip.focus_set()

    def simular_declinada():
        frame_nip.pack_forget()
        lbl_estado_lcd.configure(
            text="❌ TRANSACCIÓN DECLINADA POR EL BANCO EMISOR\n(Fondos insuficientes o tarjeta bloqueada)",
            text_color="#FF5252"
        )

    frame_acciones_pinpad = ctk.CTkFrame(modal, fg_color="transparent")
    frame_acciones_pinpad.pack(fill="x", padx=25, pady=8)

    ctk.CTkButton(
        frame_acciones_pinpad,
        text="📶 Acercar Tarjeta (Contactless / NFC)",
        height=36,
        fg_color="#1565C0",
        hover_color="#0D47A1",
        command=pago_contactless
    ).pack(fill="x", pady=4)

    ctk.CTkButton(
        frame_acciones_pinpad,
        text="💳 Insertar Tarjeta (Chip + NIP)",
        height=36,
        fg_color="#00695C",
        hover_color="#004D40",
        command=mostrar_modo_chip
    ).pack(fill="x", pady=4)

    ctk.CTkButton(
        frame_acciones_pinpad,
        text="🚫 Simular Tarjeta Declinada",
        height=34,
        fg_color="#C62828",
        hover_color="#8E0000",
        command=simular_declinada
    ).pack(fill="x", pady=4)

    ctk.CTkButton(
        modal,
        text="Cancelar Operación",
        width=160,
        fg_color="gray40",
        hover_color="gray30",
        command=modal.destroy
    ).pack(pady=(6, 10))

    modal.after(20, lambda: (modal.lift(), modal.focus_force(), modal.grab_set()))
    return modal
