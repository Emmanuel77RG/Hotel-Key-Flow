import os
import uuid
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


def generar_pdf_factura(fac: dict, ruta_logo_light: str = None, ruta_logo_dark: str = None, carpeta_destino: str = None) -> str:
    """
    Genera un comprobante fiscal digital CFDI 4.0 en PDF para una reserva.
    Retorna la ruta absoluta del archivo PDF generado.
    """
    if carpeta_destino:
        carpeta_base = carpeta_destino
    else:
        carpeta_base = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "facturas_emitidas"))
    os.makedirs(carpeta_base, exist_ok=True)
    uuid_str = fac.get("uuid_fiscal", "SIN-UUID")
    id_res = fac.get("id_reserva", "0")
    nombre_archivo = f"Factura_CFDI_Reserva_{id_res}_{uuid_str[:8]}.pdf"
    ruta_pdf = os.path.join(carpeta_base, nombre_archivo)

    doc = SimpleDocTemplate(
        ruta_pdf,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=36,
        bottomMargin=95,
    )
    estilos = getSampleStyleSheet()
    estilo_normal = estilos["Normal"]
    estilo_sub = ParagraphStyle(
        "SubtituloAzul",
        parent=estilo_normal,
        fontName="Helvetica-Bold",
        fontSize=11,
        textColor=colors.HexColor("#0D2B4E"),
        spaceAfter=4,
    )
    estilo_peq = ParagraphStyle(
        "PequenoGris",
        parent=estilo_normal,
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#4A5568"),
    )

    elementos = []

    # 1. Encabezado con Logo KeyFlow y Datos Fiscales del Emisor
    logo_rl = None
    if ruta_logo_light and os.path.exists(ruta_logo_light):
        logo_rl = RLImage(ruta_logo_light, width=2.2 * inch, height=0.86 * inch)
    elif ruta_logo_dark and os.path.exists(ruta_logo_dark):
        logo_rl = RLImage(ruta_logo_dark, width=2.2 * inch, height=0.86 * inch)
    else:
        logo_rl = Paragraph("<b>HOTEL KEYFLOW</b>", estilo_sub)

    info_emisor = Paragraph(
        "<b>HOTEL KEYFLOW S.A. DE C.V.</b><br/>"
        "RFC Emisor: <b>HKF260101AAA</b><br/>"
        "Régimen Fiscal: 601 - General de Ley Personas Morales<br/>"
        "Tipo de Comprobante: I - Ingreso (CFDI 4.0)<br/>"
        f"Fecha y Hora de Certificación: {fac.get('fecha_timbrado', '')}",
        estilo_normal,
    )
    tabla_header = Table([[logo_rl, info_emisor]], colWidths=[2.6 * inch, 4.6 * inch])
    tabla_header.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ]
        )
    )
    elementos.append(tabla_header)
    elementos.append(Spacer(1, 8))

    # 2. Tabla de Datos del Receptor y Folio Fiscal UUID
    datos_receptor = [
        [
            Paragraph("<b>DATOS DEL RECEPTOR (CLIENTE)</b>", estilo_sub),
            Paragraph("<b>DATOS FISCALES DEL COMPROBANTE</b>", estilo_sub),
        ],
        [
            Paragraph(
                f"<b>Razón Social:</b> {fac.get('razon_social', 'PÚBLICO EN GENERAL')}<br/>"
                f"<b>RFC Receptor:</b> {fac.get('rfc_receptor', '')}<br/>"
                "<b>Uso de CFDI:</b> G03 - Gastos en general",
                estilo_normal,
            ),
            Paragraph(
                f"<b>Folio Fiscal (UUID):</b><br/>{uuid_str}<br/>"
                f"<b>Reserva #:</b> {id_res} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Habitación:</b> {fac.get('habitaciones', 'S/N')}<br/>"
                f"<b>Estancia:</b> {fac.get('fecha_entrada', '')} al {fac.get('fecha_salida', '')}",
                estilo_normal,
            ),
        ],
    ]
    tabla_receptor = Table(datos_receptor, colWidths=[3.5 * inch, 3.7 * inch])
    tabla_receptor.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EDF2F7")),
                ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#CBD5E0")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                ("PADDING", (0, 0), (-1, -1), 8),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    elementos.append(tabla_receptor)
    elementos.append(Spacer(1, 14))

    # 3. Tabla de Conceptos (Cargos del Folio)
    elementos.append(Paragraph("CONCEPTOS FACTURADOS", estilo_sub))
    filas_conceptos = [["Clave SAT", "Cant.", "Unidad", "Descripción del Concepto", "Importe (MXN)"]]
    cargos = fac.get("cargos") or []
    if not cargos:
        filas_conceptos.append(
            ["90111500", "1", "E48", f"Servicios de Hospedaje - Reserva #{id_res}", f"${float(fac.get('total_facturado', 0)):.2f}"]
        )
    else:
        for c in cargos:
            filas_conceptos.append(
                [
                    "90111500",
                    "1",
                    "E48",
                    str(c.get("descripcion", "Cargo de estancia")),
                    f"${float(c.get('monto', 0)):.2f}",
                ]
            )

    tabla_conceptos = Table(
        filas_conceptos,
        colWidths=[1.0 * inch, 0.6 * inch, 0.7 * inch, 3.6 * inch, 1.3 * inch],
    )
    tabla_conceptos.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0D2B4E")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("ALIGN", (0, 0), (2, -1), "CENTER"),
                ("ALIGN", (4, 0), (4, -1), "RIGHT"),
                ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#CBD5E0")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                ("PADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    elementos.append(tabla_conceptos)
    elementos.append(Spacer(1, 12))

    # 4. Resumen de Pagos y Desglose de Impuestos (Subtotal, IVA 16%, Total)
    pagos = fac.get("pagos") or []
    metodos_str = ", ".join(p.get("metodo_pago", "Efectivo") for p in pagos) if pagos else "Liquidado en Recepción"
    info_pago_p = Paragraph(
        f"<b>Forma / Método de Pago Registrado:</b><br/>{metodos_str}<br/><br/>"
        "<b>Moneda:</b> MXN - Peso Mexicano<br/>"
        "<b>Exportación:</b> 01 - No aplica",
        estilo_normal,
    )

    subtotal = float(fac.get("subtotal", 0.0))
    iva = float(fac.get("iva_16", 0.0))
    total = float(fac.get("total_facturado", 0.0))

    tabla_totales = Table(
        [
            ["Subtotal:", f"${subtotal:,.2f} MXN"],
            ["IVA Trasladado (16%):", f"${iva:,.2f} MXN"],
            ["TOTAL FACTURADO:", f"${total:,.2f} MXN"],
        ],
        colWidths=[1.5 * inch, 1.3 * inch],
    )
    tabla_totales.setStyle(
        TableStyle(
            [
                ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
                ("FONTNAME", (0, 2), (-1, 2), "Helvetica-Bold"),
                ("FONTSIZE", (0, 2), (-1, 2), 11),
                ("TEXTCOLOR", (0, 2), (-1, 2), colors.HexColor("#0D2B4E")),
                ("LINEABOVE", (0, 2), (-1, 2), 1.0, colors.HexColor("#0D2B4E")),
                ("PADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )

    tabla_pie_totales = Table([[info_pago_p, tabla_totales]], colWidths=[4.4 * inch, 2.8 * inch])
    tabla_pie_totales.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    elementos.append(tabla_pie_totales)

    # 5. Pie de página fijo al final de la hoja (Cadena Original del SAT y leyenda CFDI)
    sello_simulado = (
        f"||1.1|{uuid_str}|{fac.get('fecha_timbrado', '')}|HKF260101AAA|"
        f"{fac.get('rfc_receptor', '')}|{total:.2f}|SelloDigitalPACKeyFlow="
        f"{uuid_str.replace('-', '')}89AF01BC||"
    )
    parrafo_pie = Paragraph(
        f"<b>Cadena Original del Complemento de Certificación Digital del SAT:</b><br/>{sello_simulado}<br/><br/>"
        "Este documento es una representación impresa de un CFDI emitida por el Sistema de Gestión Hotelera KeyFlow.",
        estilo_peq,
    )

    def dibujar_pie_pagina(canvas, doc_obj):
        canvas.saveState()
        ancho_util = letter[0] - doc_obj.leftMargin - doc_obj.rightMargin
        _, alto_p = parrafo_pie.wrap(ancho_util, doc_obj.bottomMargin)
        y_base = 28
        canvas.setStrokeColor(colors.HexColor("#CBD5E0"))
        canvas.setLineWidth(0.6)
        canvas.line(
            doc_obj.leftMargin,
            y_base + alto_p + 8,
            letter[0] - doc_obj.rightMargin,
            y_base + alto_p + 8,
        )
        parrafo_pie.drawOn(canvas, doc_obj.leftMargin, y_base)
        canvas.restoreState()

    doc.build(elementos, onFirstPage=dibujar_pie_pagina, onLaterPages=dibujar_pie_pagina)
    return ruta_pdf
