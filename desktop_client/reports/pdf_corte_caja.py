import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


def generar_pdf_corte_caja(data: dict, ruta_logo_light: str = None, ruta_logo_dark: str = None, carpeta_destino: str = None) -> str:
    """
    Genera un informe ejecutivo de corte de caja y rendimiento operativo en formato PDF.
    Alineación calibrada a exactamente 7.50 pulgadas de ancho útil (márgenes de 0.5 in).
    Retorna la ruta absoluta del archivo PDF generado.
    """
    if carpeta_destino:
        carpeta_rep = carpeta_destino
    else:
        carpeta_rep = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "reportes_pdf")
    os.makedirs(carpeta_rep, exist_ok=True)
    marca_tiempo = datetime.now().strftime("%Y%m%d_%H%M%S")
    ruta_pdf = os.path.join(carpeta_rep, f"Corte_Caja_KeyFlow_{marca_tiempo}.pdf")

    doc = SimpleDocTemplate(
        ruta_pdf,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=32,
        bottomMargin=50,
    )
    estilos = getSampleStyleSheet()
    estilo_titulo = ParagraphStyle(
        "TituloRep",
        parent=estilos["Heading1"],
        fontSize=15,
        leading=18,
        textColor=colors.HexColor("#1A365D"),
        spaceAfter=2,
    )
    estilo_sub = ParagraphStyle(
        "SubRep",
        parent=estilos["Normal"],
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#4A5568"),
    )
    estilo_sec = ParagraphStyle(
        "SecRep",
        parent=estilos["Heading2"],
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#1A365D"),
        spaceBefore=10,
        spaceAfter=4,
    )
    estilo_th_blanco = ParagraphStyle(
        "THBlanco",
        parent=estilos["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        textColor=colors.white,
        alignment=1,  # Centrado
    )
    estilo_celda = ParagraphStyle(
        "CeldaRep",
        parent=estilos["Normal"],
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#2D3748"),
    )
    estilo_celda_center = ParagraphStyle(
        "CeldaRepCenter",
        parent=estilo_celda,
        alignment=1,  # Centrado
    )
    estilo_celda_right = ParagraphStyle(
        "CeldaRepRight",
        parent=estilo_celda,
        alignment=2,  # Derecha
    )
    estilo_celda_bold = ParagraphStyle(
        "CeldaRepBold",
        parent=estilo_celda,
        fontName="Helvetica-Bold",
    )
    estilo_celda_bold_right = ParagraphStyle(
        "CeldaRepBoldRight",
        parent=estilo_celda,
        fontName="Helvetica-Bold",
        alignment=2,  # Derecha
    )

    elementos = []
    cajero = data.get("cajero_actual", {})
    ocup = data.get("ocupacion", {})
    fin = data.get("finanzas", {})
    mant = data.get("mantenimiento", {})

    bloque_emisor = [
        Paragraph("<b>HOTEL KEYFLOW — SISTEMA DE GESTIÓN HOTELERA</b>", estilo_titulo),
        Paragraph("<b>REPORTE EJECUTIVO DE RENDIMIENTO Y CORTE DE CAJA</b>", estilo_sub),
        Paragraph(
            f"<b>Fecha de Generación:</b> {data.get('fecha_generacion', '')} &nbsp;&nbsp;|&nbsp;&nbsp; "
            f"<b>Periodo Consultado:</b> {data.get('filtro_fecha', 'Todo el historial')}",
            estilo_sub,
        ),
        Paragraph(
            f"<b>Cajero / Operador en Turno:</b> {cajero.get('nombre', 'Personal')} ({cajero.get('email', '')})",
            estilo_sub,
        ),
    ]

    logo_path = ruta_logo_light if (ruta_logo_light and os.path.exists(ruta_logo_light)) else ruta_logo_dark
    if logo_path and os.path.exists(logo_path):
        img_logo = RLImage(logo_path, width=1.9 * inch, height=0.75 * inch)
        t_header = Table([[img_logo, bloque_emisor]], colWidths=[2.1 * inch, 5.4 * inch])
        t_header.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        elementos.append(t_header)
    else:
        for p in bloque_emisor:
            elementos.append(p)

    elementos.append(Spacer(1, 8))

    # 1. Tabla de Resumen Financiero (Corte de Caja)
    elementos.append(Paragraph("1. Resumen Financiero de Corte de Caja", estilo_sec))
    filas_fin = [
        [
            Paragraph("<b>Indicador Financiero</b>", estilo_th_blanco),
            Paragraph("<b>Monto (MXN)</b>", estilo_th_blanco),
            Paragraph("<b>Indicador de Cargos / Saldos</b>", estilo_th_blanco),
            Paragraph("<b>Monto (MXN)</b>", estilo_th_blanco),
        ],
        [
            Paragraph("Efectivo Recibido en Caja", estilo_celda),
            Paragraph(f"${float(fin.get('total_efectivo', 0.0)):.2f}", estilo_celda_right),
            Paragraph("Cargos por Hospedaje y Extras", estilo_celda),
            Paragraph(f"${float(fin.get('cargos_hospedaje', 0.0)):.2f}", estilo_celda_right),
        ],
        [
            Paragraph("Cobros en Terminal PinPad (Tarjeta)", estilo_celda),
            Paragraph(f"${float(fin.get('total_tarjeta', 0.0)):.2f}", estilo_celda_right),
            Paragraph("Consumos Punto de Venta (POS)", estilo_celda),
            Paragraph(f"${float(fin.get('cargos_pos', 0.0)):.2f}", estilo_celda_right),
        ],
        [
            Paragraph("<b>TOTAL RECAUDADO EN CORTE</b>", estilo_celda_bold),
            Paragraph(f"<b>${float(fin.get('total_recaudado', 0.0)):.2f}</b>", estilo_celda_bold_right),
            Paragraph("<b>Saldo Pendiente por Cobrar (Folios)</b>", estilo_celda_bold),
            Paragraph(f"<b>${float(fin.get('saldo_por_cobrar_folios', 0.0)):.2f}</b>", estilo_celda_bold_right),
        ],
    ]
    t_fin = Table(filas_fin, colWidths=[2.35 * inch, 1.25 * inch, 2.65 * inch, 1.25 * inch])
    t_fin.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1A365D")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BACKGROUND", (0, 3), (1, 3), colors.HexColor("#E6FFFA")),
                ("BACKGROUND", (2, 3), (3, 3), colors.HexColor("#FFF5F5")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    elementos.append(t_fin)

    # 2. Tabla de Indicadores Operativos y Ocupación
    elementos.append(Paragraph("2. Indicadores Operativos y Estado del Inventario", estilo_sec))
    filas_op = [
        [
            Paragraph("<b>% Ocupación</b>", estilo_th_blanco),
            Paragraph("<b>Habitaciones</b>", estilo_th_blanco),
            Paragraph("<b>Ocupadas</b>", estilo_th_blanco),
            Paragraph("<b>Limpias</b>", estilo_th_blanco),
            Paragraph("<b>Sucias / Limpieza</b>", estilo_th_blanco),
            Paragraph("<b>Mantenimiento</b>", estilo_th_blanco),
            Paragraph("<b>Tickets Activos</b>", estilo_th_blanco),
        ],
        [
            Paragraph(f"<b>{float(ocup.get('porcentaje_ocupacion', 0.0)):.1f}%</b>", estilo_celda_center),
            Paragraph(str(ocup.get("total_habitaciones", 0)), estilo_celda_center),
            Paragraph(str(ocup.get("ocupadas", 0)), estilo_celda_center),
            Paragraph(str(ocup.get("limpias", 0)), estilo_celda_center),
            Paragraph(f"{ocup.get('sucias', 0)} / {ocup.get('en_limpieza', 0)}", estilo_celda_center),
            Paragraph(str(ocup.get("mantenimiento", 0)), estilo_celda_center),
            Paragraph(str(mant.get("pendientes", 0) + mant.get("en_reparacion", 0)), estilo_celda_center),
        ],
    ]
    t_op = Table(
        filas_op,
        colWidths=[1.10 * inch, 1.05 * inch, 0.85 * inch, 0.85 * inch, 1.25 * inch, 1.20 * inch, 1.20 * inch],
    )
    t_op.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2C5282")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    elementos.append(t_op)

    # 3. Desglose de Pagos Recibidos en el Corte
    elementos.append(Paragraph("3. Desglose de Pagos Procesados en el Corte de Caja", estilo_sec))
    pagos = data.get("pagos_detalle", [])
    filas_pagos = [
        [
            Paragraph("<b>ID</b>", estilo_th_blanco),
            Paragraph("<b>Folio / Hab.</b>", estilo_th_blanco),
            Paragraph("<b>Huésped</b>", estilo_th_blanco),
            Paragraph("<b>Método de Pago / Token</b>", estilo_th_blanco),
            Paragraph("<b>Cajero</b>", estilo_th_blanco),
            Paragraph("<b>Fecha y Hora</b>", estilo_th_blanco),
            Paragraph("<b>Monto</b>", estilo_th_blanco),
        ]
    ]
    if pagos:
        for p in pagos:
            fecha_raw = str(p.get("fecha_creacion", ""))
            fecha_formateada = fecha_raw.replace(" ", "<br/>") if " " in fecha_raw else fecha_raw
            filas_pagos.append(
                [
                    Paragraph(f"#{p['id_pago']}", estilo_celda_center),
                    Paragraph(f"Folio #{p['id_reserva']}<br/>Hab. {p['habitaciones']}", estilo_celda),
                    Paragraph(str(p.get("huesped", "")), estilo_celda),
                    Paragraph(str(p.get("metodo_pago", "")), estilo_celda),
                    Paragraph(str(p.get("cajero", "")), estilo_celda),
                    Paragraph(fecha_formateada, estilo_celda_center),
                    Paragraph(f"${float(p.get('monto', 0.0)):.2f}", estilo_celda_bold_right),
                ]
            )
    else:
        filas_pagos.append([
            Paragraph("-", estilo_celda_center),
            Paragraph("-", estilo_celda),
            Paragraph("Sin pagos registrados en este corte", estilo_celda),
            Paragraph("-", estilo_celda),
            Paragraph("-", estilo_celda),
            Paragraph("-", estilo_celda_center),
            Paragraph("$0.00", estilo_celda_right)
        ])

    t_pagos = Table(
        filas_pagos,
        colWidths=[0.45 * inch, 1.10 * inch, 1.40 * inch, 1.60 * inch, 0.90 * inch, 1.10 * inch, 0.95 * inch],
    )
    t_pagos.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1A365D")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E0")),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    elementos.append(t_pagos)

    # 4. Listado de Llegadas y Salidas
    elementos.append(Paragraph("4. Listado Operativo de Llegadas (Check-in) y Salidas (Check-out)", estilo_sec))
    movs = data.get("movimientos_operativos", {})
    filas_movs = [
        [
            Paragraph("<b>Movimiento</b>", estilo_th_blanco),
            Paragraph("<b>Folio / Hab.</b>", estilo_th_blanco),
            Paragraph("<b>Huésped</b>", estilo_th_blanco),
            Paragraph("<b>Entrada</b>", estilo_th_blanco),
            Paragraph("<b>Salida</b>", estilo_th_blanco),
            Paragraph("<b>Estado Reserva</b>", estilo_th_blanco),
            Paragraph("<b>Estado Folio</b>", estilo_th_blanco),
        ]
    ]
    for r in movs.get("llegadas", []):
        filas_movs.append(
            [
                Paragraph("<font color='#0288D1'><b>LLEGADA</b></font>", estilo_celda_center),
                Paragraph(f"#{r['id_reserva']} (Hab. {r.get('habitaciones')})", estilo_celda),
                Paragraph(str(r.get("huesped", "")), estilo_celda),
                Paragraph(str(r.get("fecha_entrada", "")), estilo_celda_center),
                Paragraph(str(r.get("fecha_salida", "")), estilo_celda_center),
                Paragraph(str(r.get("estado_reserva", "")), estilo_celda_center),
                Paragraph(str(r.get("estado_folio", "")), estilo_celda_center),
            ]
        )
    for r in movs.get("salidas", []):
        filas_movs.append(
            [
                Paragraph("<font color='#E65100'><b>SALIDA</b></font>", estilo_celda_center),
                Paragraph(f"#{r['id_reserva']} (Hab. {r.get('habitaciones')})", estilo_celda),
                Paragraph(str(r.get("huesped", "")), estilo_celda),
                Paragraph(str(r.get("fecha_entrada", "")), estilo_celda_center),
                Paragraph(str(r.get("fecha_salida", "")), estilo_celda_center),
                Paragraph(str(r.get("estado_reserva", "")), estilo_celda_center),
                Paragraph(str(r.get("estado_folio", "")), estilo_celda_center),
            ]
        )
    if len(filas_movs) == 1:
        filas_movs.append([
            Paragraph("-", estilo_celda_center),
            Paragraph("-", estilo_celda),
            Paragraph("Sin movimientos registrados", estilo_celda),
            Paragraph("-", estilo_celda_center),
            Paragraph("-", estilo_celda_center),
            Paragraph("-", estilo_celda_center),
            Paragraph("-", estilo_celda_center)
        ])

    t_movs = Table(
        filas_movs,
        colWidths=[0.90 * inch, 1.15 * inch, 1.75 * inch, 0.90 * inch, 0.90 * inch, 1.00 * inch, 0.90 * inch],
    )
    t_movs.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2C5282")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E0")),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    elementos.append(t_movs)

    # 5. Resumen de Mantenimiento y Pie
    elementos.append(Paragraph("5. Estatus de Tickets de Mantenimiento", estilo_sec))
    filas_mant = [
        [
            Paragraph("<b>Tickets Pendientes</b>", estilo_th_blanco),
            Paragraph("<b>En Reparación</b>", estilo_th_blanco),
            Paragraph("<b>Resueltos</b>", estilo_th_blanco),
            Paragraph("<b>Total Reportados</b>", estilo_th_blanco),
        ],
        [
            Paragraph(str(mant.get("pendientes", 0)), estilo_celda_center),
            Paragraph(str(mant.get("en_reparacion", 0)), estilo_celda_center),
            Paragraph(str(mant.get("resueltos", 0)), estilo_celda_center),
            Paragraph(str(mant.get("total_tickets", 0)), estilo_celda_center),
        ],
    ]
    t_mant = Table(filas_mant, colWidths=[1.875 * inch, 1.875 * inch, 1.875 * inch, 1.875 * inch])
    t_mant.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4A5568")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E0")),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    elementos.append(t_mant)

    elementos.append(Spacer(1, 14))
    pie_linea = Paragraph(
        "<i>Reporte operativo y financiero generado por Hotel KeyFlow PMS. Documento interno para auditoría de caja.</i>",
        estilo_sub,
    )
    elementos.append(pie_linea)

    elementos.append(Spacer(1, 24))
    tabla_firmas = Table(
        [
            ["________________________________________", "________________________________________"],
            [
                f"ENTREGA TURNO: {cajero.get('nombre', 'Cajero en Turno')}",
                "RECIBE Y AUDITA: Gerencia / Administración",
            ],
        ],
        colWidths=[3.75 * inch, 3.75 * inch],
    )
    tabla_firmas.setStyle(
        TableStyle(
            [
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#2D3748")),
            ]
        )
    )
    elementos.append(tabla_firmas)

    doc.build(elementos)
    return ruta_pdf
