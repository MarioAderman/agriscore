"""Generate dummy demo PDFs: Constancia de Situación Fiscal + Certificado Parcelario.

Run: python scripts/generate_demo_docs.py
Output: docs/demo/constancia_fiscal_escutia.pdf, docs/demo/certificado_parcelario_escutia.pdf
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import cm, mm
from reportlab.lib.colors import HexColor, black, white
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "docs", "demo")
os.makedirs(OUT_DIR, exist_ok=True)

# ── Shared colors ──
SAT_DARK = HexColor("#4a4a4a")
SAT_HEADER_BG = HexColor("#3d3d3d")
SAT_LIGHT_BG = HexColor("#f5f5f5")
SAT_BORDER = HexColor("#cccccc")
RAN_GREEN = HexColor("#2e7d32")


# ═══════════════════════════════════════════════════════════════════════════════
# 1. Constancia de Situación Fiscal
# ═══════════════════════════════════════════════════════════════════════════════

def generate_constancia():
    path = os.path.join(OUT_DIR, "constancia_fiscal_escutia.pdf")
    doc = SimpleDocTemplate(
        path, pagesize=letter,
        topMargin=1.5*cm, bottomMargin=2*cm,
        leftMargin=2*cm, rightMargin=2*cm,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "SATTitle", parent=styles["Normal"],
        fontSize=11, fontName="Helvetica-Bold",
        alignment=TA_CENTER, spaceAfter=2*mm,
    )
    header_style = ParagraphStyle(
        "SATHeader", parent=styles["Normal"],
        fontSize=9, fontName="Helvetica-Bold",
        textColor=white, alignment=TA_LEFT,
    )
    label_style = ParagraphStyle(
        "Label", parent=styles["Normal"],
        fontSize=8, fontName="Helvetica-Bold",
        textColor=SAT_DARK,
    )
    value_style = ParagraphStyle(
        "Value", parent=styles["Normal"],
        fontSize=8, fontName="Helvetica",
        textColor=black,
    )
    small_style = ParagraphStyle(
        "Small", parent=styles["Normal"],
        fontSize=6.5, fontName="Helvetica",
        textColor=SAT_DARK, alignment=TA_JUSTIFY,
        leading=8,
    )
    page_style = ParagraphStyle(
        "PageNum", parent=styles["Normal"],
        fontSize=7, fontName="Helvetica",
        alignment=TA_RIGHT,
    )

    elements = []

    # ── Top banner ──
    elements.append(Paragraph("CÉDULA DE IDENTIFICACIÓN FISCAL", title_style))
    elements.append(Spacer(1, 3*mm))

    banner_data = [[
        Paragraph(
            '<font size="7"><b>Hacienda</b> | <b>SAT</b></font>',
            ParagraphStyle("b", parent=styles["Normal"], fontSize=7, alignment=TA_LEFT)
        ),
        Paragraph(
            "<b>CONSTANCIA DE SITUACIÓN FISCAL</b>",
            ParagraphStyle("b", parent=styles["Normal"], fontSize=10,
                           fontName="Helvetica-Bold", alignment=TA_CENTER),
        ),
    ]]
    banner = Table(banner_data, colWidths=[7*cm, 10*cm])
    banner.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), SAT_LIGHT_BG),
        ("BOX", (0, 0), (-1, -1), 0.5, SAT_BORDER),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(banner)
    elements.append(Spacer(1, 2*mm))

    # ── RFC & emission info ──
    info_data = [[
        Paragraph("<b>EUBJ850315KA7</b><br/>Registro Federal de Contribuyentes", value_style),
        Paragraph(
            "Lugar y Fecha de Emisión<br/>"
            "<b>OCOZOCOAUTLA DE ESPINOSA, CHIAPAS A 15 DE MARZO DE 2026</b>",
            ParagraphStyle("c", parent=value_style, alignment=TA_CENTER),
        ),
    ]]
    info_table = Table(info_data, colWidths=[7*cm, 10*cm])
    info_table.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.5, SAT_BORDER),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, SAT_BORDER),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 2*mm))

    # ── Identification header ──
    id_header = Table(
        [[Paragraph("Datos de Identificación del Contribuyente:", header_style)]],
        colWidths=[17*cm],
    )
    id_header.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), SAT_HEADER_BG),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(id_header)

    # ── Identification data ──
    id_rows = [
        ("RFC:", "EUBJ850315KA7"),
        ("CURP:", "EUBJ850315HCSSCN05"),
        ("Nombre (s):", "JOSÉ DANIEL"),
        ("Primer Apellido:", "ESCUTIA"),
        ("Segundo Apellido:", "BARRAGÁN"),
        ("Fecha inicio de operaciones:", "22 DE ENERO DE 2019"),
        ("Estatus en el padrón:", "ACTIVO"),
        ("Fecha de último cambio de estado:", "22 DE ENERO DE 2019"),
        ("Nombre Comercial:", ""),
    ]
    id_data = [[Paragraph(l, label_style), Paragraph(v, value_style)] for l, v in id_rows]
    id_table = Table(id_data, colWidths=[7*cm, 10*cm])
    id_table.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.5, SAT_BORDER),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, SAT_BORDER),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(id_table)
    elements.append(Spacer(1, 3*mm))

    # ── Address header ──
    addr_header = Table(
        [[Paragraph("Datos del domicilio registrado", header_style)]],
        colWidths=[17*cm],
    )
    addr_header.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), SAT_HEADER_BG),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(addr_header)

    # ── Address data (two-column pairs) ──
    addr_rows = [
        ("Código Postal:", "29140", "Tipo de Vialidad:", "CALLE"),
        ("Nombre de Vialidad:", "2A NORTE PONIENTE", "Número Exterior:", "47"),
        ("Número Interior:", "", "Nombre de la Colonia:", "CENTRO"),
        ("Nombre de la Localidad:", "OCOZOCOAUTLA DE ESPINOSA",
         "Nombre del Municipio o Demarcación Territorial:", "OCOZOCOAUTLA DE ESPINOSA"),
        ("Nombre de la Entidad Federativa:", "CHIAPAS", "Entre Calle:", "1A PONIENTE NORTE"),
    ]
    addr_data = []
    for row in addr_rows:
        addr_data.append([
            Paragraph(row[0], label_style), Paragraph(row[1], value_style),
            Paragraph(row[2], label_style), Paragraph(row[3], value_style),
        ])
    addr_table = Table(addr_data, colWidths=[4.5*cm, 4*cm, 4.5*cm, 4*cm])
    addr_table.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.5, SAT_BORDER),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, SAT_BORDER),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(addr_table)
    elements.append(Spacer(1, 2*mm))
    elements.append(Paragraph("Y Calle: 2A NORTE PONIENTE", label_style))
    elements.append(Spacer(1, 4*mm))

    # Page 1 / 3
    elements.append(Paragraph("Página [1] de [3]", page_style))
    elements.append(Spacer(1, 6*mm))

    # ── Page 2: Actividades Económicas ──
    act_header = Table(
        [[Paragraph("Actividades Económicas:", header_style)]],
        colWidths=[17*cm],
    )
    act_header.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), SAT_HEADER_BG),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(act_header)

    act_col_headers = [
        Paragraph("<b>Orden</b>", label_style),
        Paragraph("<b>Actividad Económica</b>", label_style),
        Paragraph("<b>Porcentaje</b>", label_style),
        Paragraph("<b>Fecha Inicio</b>", label_style),
        Paragraph("<b>Fecha Fin</b>", label_style),
    ]
    act_data = [
        act_col_headers,
        [
            Paragraph("1", value_style),
            Paragraph("Cultivo de maíz y de otros cereales excepto trigo y arroz", value_style),
            Paragraph("60", value_style),
            Paragraph("22/01/2019", value_style),
            Paragraph("", value_style),
        ],
        [
            Paragraph("2", value_style),
            Paragraph("Cultivo de frijol y otros granos de leguminosas", value_style),
            Paragraph("30", value_style),
            Paragraph("22/01/2019", value_style),
            Paragraph("", value_style),
        ],
        [
            Paragraph("3", value_style),
            Paragraph("Cultivo de café", value_style),
            Paragraph("10", value_style),
            Paragraph("15/06/2021", value_style),
            Paragraph("", value_style),
        ],
    ]
    act_table = Table(act_data, colWidths=[1.5*cm, 8*cm, 2*cm, 3*cm, 2.5*cm])
    act_table.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.5, SAT_BORDER),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, SAT_BORDER),
        ("BACKGROUND", (0, 0), (-1, 0), SAT_LIGHT_BG),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(act_table)
    elements.append(Spacer(1, 4*mm))

    # ── Regímenes ──
    reg_header = Table(
        [[Paragraph("Regímenes:", header_style)]],
        colWidths=[17*cm],
    )
    reg_header.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), SAT_HEADER_BG),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(reg_header)

    reg_data = [
        [
            Paragraph("<b>Régimen</b>", label_style),
            Paragraph("<b>Fecha Inicio</b>", label_style),
            Paragraph("<b>Fecha Fin</b>", label_style),
        ],
        [
            Paragraph(
                "Régimen de las Personas Físicas con Actividades Empresariales y Profesionales",
                value_style,
            ),
            Paragraph("22/01/2019", value_style),
            Paragraph("", value_style),
        ],
    ]
    reg_table = Table(reg_data, colWidths=[11*cm, 3*cm, 3*cm])
    reg_table.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.5, SAT_BORDER),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, SAT_BORDER),
        ("BACKGROUND", (0, 0), (-1, 0), SAT_LIGHT_BG),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(reg_table)
    elements.append(Spacer(1, 4*mm))

    # ── Obligaciones ──
    obl_header = Table(
        [[Paragraph("Obligaciones:", header_style)]],
        colWidths=[17*cm],
    )
    obl_header.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), SAT_HEADER_BG),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(obl_header)

    obl_data = [
        [
            Paragraph("<b>Descripción de la Obligación</b>", label_style),
            Paragraph("<b>Descripción Vencimiento</b>", label_style),
            Paragraph("<b>Fecha Inicio</b>", label_style),
            Paragraph("<b>Fecha Fin</b>", label_style),
        ],
        [
            Paragraph("Declaración anual de ISR. Personas Físicas.", value_style),
            Paragraph("A más tardar el 30 de abril del ejercicio siguiente.", value_style),
            Paragraph("22/01/2019", value_style),
            Paragraph("", value_style),
        ],
        [
            Paragraph("Declaración de proveedores de IVA", value_style),
            Paragraph("A más tardar el último día del mes inmediato posterior al periodo que corresponda.", value_style),
            Paragraph("22/01/2019", value_style),
            Paragraph("", value_style),
        ],
        [
            Paragraph(
                "Pago provisional mensual de ISR por actividades empresariales. "
                "Régimen de Actividades Empresariales y Profesionales",
                value_style,
            ),
            Paragraph("A más tardar el día 17 del mes inmediato posterior al periodo que corresponda.", value_style),
            Paragraph("22/01/2019", value_style),
            Paragraph("", value_style),
        ],
        [
            Paragraph("Pago definitivo mensual de IVA.", value_style),
            Paragraph("A más tardar el día 17 del mes inmediato posterior al periodo que corresponda.", value_style),
            Paragraph("22/01/2019", value_style),
            Paragraph("", value_style),
        ],
    ]
    obl_table = Table(obl_data, colWidths=[5.5*cm, 6*cm, 3*cm, 2.5*cm])
    obl_table.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.5, SAT_BORDER),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, SAT_BORDER),
        ("BACKGROUND", (0, 0), (-1, 0), SAT_LIGHT_BG),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(obl_table)
    elements.append(Spacer(1, 4*mm))

    # ── Privacy notice ──
    elements.append(Paragraph(
        "Sus datos personales son incorporados y protegidos en los sistemas del SAT, "
        "de conformidad con los Lineamientos de Protección de Datos Personales y con "
        "diversas disposiciones fiscales y legales sobre confidencialidad y protección "
        "de datos, a fin de ejercer las facultades conferidas a la autoridad fiscal.",
        small_style,
    ))
    elements.append(Spacer(1, 2*mm))
    elements.append(Paragraph(
        "Si desea modificar o corregir sus datos personales, puede acudir a cualquier "
        "Módulo de Servicios Tributarios y/o a través de la dirección http://sat.gob.mx",
        small_style,
    ))
    elements.append(Spacer(1, 3*mm))

    # ── Digital seal (mockup) ──
    elements.append(Paragraph(
        "<b>Cadena Original Sello:</b> ||2026/03/15 10:42:17|EUBJ850315KA7|"
        "CONSTANCIA DE SITUACIÓN FISCAL|200001099999900000073|"
        "U2FsdGVkX1+Dm0cKpE7qR4xMN3fVb2hT9wLJkQz5yAe8rPdh3NbcTaZ"
        "CfwXPjiBf||",
        small_style,
    ))
    elements.append(Spacer(1, 1*mm))
    elements.append(Paragraph(
        "<b>Sello Digital:</b> Hk4P3RO82gqJ/sRREg7/YkJ6dKHFCOkn3prndeTPwvGQaxbU8SW414UnziACkMxbq"
        "q0PLdxt5P3+keprwkOZZhEZnsyw3Siz4ZBH3CyXr9VjLPX5uBNWpxjw/GMxIc4A0cPW0Skj9vCBfy"
        "fWYMnWa+m6LBnNQfwOFrWRBQPok=",
        small_style,
    ))
    elements.append(Spacer(1, 4*mm))

    # ── Footer ──
    elements.append(HRFlowable(width="100%", thickness=0.5, color=SAT_BORDER))
    elements.append(Spacer(1, 2*mm))
    footer_data = [[
        Paragraph(
            '<font size="7"><b>Hacienda</b> | <b>SAT</b><br/>'
            '<font size="5">Secretaría de Hacienda y Crédito Público<br/>'
            'SERVICIO DE ADMINISTRACIÓN TRIBUTARIA</font></font>',
            ParagraphStyle("f", parent=styles["Normal"], fontSize=7),
        ),
        Paragraph(
            '<font size="5"><b>Contacto</b><br/>'
            'Av. Hidalgo 77, col. Guerrero, C.P. 06300, Ciudad de México.<br/>'
            'Atención telefónica desde cualquier parte del país:<br/>'
            'MarcaSAT 55 627 22 728 y para el exterior del país<br/>'
            '(+52) 55 627 22 728</font>',
            ParagraphStyle("f", parent=styles["Normal"], fontSize=5, alignment=TA_RIGHT),
        ),
    ]]
    footer = Table(footer_data, colWidths=[8*cm, 9*cm])
    elements.append(footer)

    doc.build(elements)
    print(f"  -> {path}")


# ═══════════════════════════════════════════════════════════════════════════════
# 2. Certificado Parcelario
# ═══════════════════════════════════════════════════════════════════════════════

def generate_certificado():
    path = os.path.join(OUT_DIR, "certificado_parcelario_escutia.pdf")
    c = canvas.Canvas(path, pagesize=letter)
    w, h = letter  # 612 x 792

    # ── Header: coat of arms text ──
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(w/2, h - 2*cm, "ESTADOS UNIDOS MEXICANOS")
    c.setFont("Helvetica", 8)
    c.drawCentredString(w/2, h - 2.5*cm, "SECRETARÍA DE DESARROLLO AGRARIO, TERRITORIAL Y URBANO")

    # ── Title ──
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(w/2, h - 3.5*cm, "CERTIFICADO PARCELARIO")
    c.setFont("Helvetica", 10)
    c.drawCentredString(w/2, h - 4.1*cm, "No. CP-070230-2019-0847")

    # ── Legal preamble ──
    c.setFont("Helvetica", 8)
    y = h - 5.2*cm
    preamble = (
        "QUE SE EXPIDE POR INSTRUCCIONES DEL C. ROMÁN GUILLERMO MEYER FALCÓN, "
        "SECRETARIO DE DESARROLLO AGRARIO, TERRITORIAL Y URBANO, "
        "CON FUNDAMENTO EN LOS ARTÍCULOS 27 FRACCIÓN VII DE LA CONSTITUCIÓN "
        "POLÍTICA DE LOS ESTADOS UNIDOS MEXICANOS; 56, 78 Y DEMÁS RELATIVOS "
        "DE LA LEY AGRARIA, ASÍ COMO EN EL REGLAMENTO INTERIOR DEL REGISTRO "
        "AGRARIO NACIONAL, QUE AMPARA LA PARCELA"
    )
    # Wrap text manually
    from reportlab.lib.utils import simpleSplit
    lines = simpleSplit(preamble, "Helvetica", 8, w - 4*cm)
    for line in lines:
        c.drawString(2*cm, y, line)
        y -= 12

    y -= 6

    # ── Parcel details ──
    def field_line(label, value, x, ypos, label_font="Helvetica-Bold", val_font="Helvetica"):
        c.setFont(label_font, 9)
        c.drawString(x, ypos, label)
        c.setFont(val_font, 9)
        c.drawString(x + c.stringWidth(label, label_font, 9) + 4, ypos, value)

    field_line("No.", "287", 2*cm, y)
    field_line("DEL EJIDO", "EL OCOTE", 6*cm, y)
    y -= 18
    field_line("MUNICIPIO DE", "OCOZOCOAUTLA DE ESPINOSA", 2*cm, y)
    y -= 18
    field_line("ESTADO DE", "CHIAPAS", 2*cm, y)
    field_line("CON SUPERFICIE DE", "5 - 23 - 47.00  Ha", 8*cm, y)
    y -= 18

    c.setFont("Helvetica", 9)
    c.drawString(2*cm, y, "CINCO HECTÁREAS, VEINTITRÉS ÁREAS, CUARENTA Y SIETE CENTIÁREAS")
    y -= 24

    # ── Measurements and boundaries ──
    c.setFont("Helvetica-Bold", 9)
    c.drawString(2*cm, y, "CON LAS SIGUIENTES MEDIDAS Y COLINDANCIAS:")
    y -= 18

    boundaries = [
        ("NORESTE", "142.30 MTS.", "CON PARCELA 286, PROPIEDAD DE RAMIRO GÓMEZ LÓPEZ"),
        ("SURESTE", "198.50 MTS.", "EN LÍNEA QUEBRADA CON PARCELA 288, PROPIEDAD DE MA. ELENA RUIZ VÁZQUEZ"),
        ("SUROESTE", "156.80 MTS.", "CON CAMINO VECINAL A LA RESERVA SELVA EL OCOTE"),
        ("NOROESTE", "187.20 MTS.", "EN LÍNEA QUEBRADA CON PARCELA 285, PROPIEDAD DE FRANCISCO HERNÁNDEZ CRUZ"),
    ]

    c.setFont("Helvetica", 8.5)
    for direction, measurement, boundary in boundaries:
        c.setFont("Helvetica-Bold", 8.5)
        c.drawString(2*cm, y, direction)
        c.setFont("Helvetica", 8.5)
        text = f" {measurement} {boundary}"
        c.drawString(2*cm + c.stringWidth(direction, "Helvetica-Bold", 8.5), y, text)
        y -= 14

    y -= 12

    # ── Beneficiary info ──
    c.setFont("Helvetica-Bold", 9)
    c.drawString(2*cm, y, "EN FAVOR DE:")
    y -= 20

    fields = [
        ("NOMBRE:", "JOSÉ DANIEL ESCUTIA BARRAGÁN"),
        ("EDAD:", "40 AÑOS"),
        ("ORIGINARIO DE:", "OCOZOCOAUTLA DE ESPINOSA, CHIAPAS"),
        ("ESTADO CIVIL:", "CASADO"),
        ("OCUPACIÓN:", "AGRICULTOR"),
        ("CON DOMICILIO EN:", "CALLE 2A NORTE PONIENTE No. 47, COLONIA CENTRO,"),
        ("", "OCOZOCOAUTLA DE ESPINOSA, CHIAPAS, C.P. 29140"),
    ]

    for label, value in fields:
        if label:
            c.setFont("Helvetica-Bold", 9)
            c.drawString(2*cm, y, label)
            c.setFont("Helvetica", 9)
            c.drawString(2*cm + c.stringWidth(label, "Helvetica-Bold", 9) + 6, y, value)
        else:
            c.setFont("Helvetica", 9)
            c.drawString(2*cm + c.stringWidth("CON DOMICILIO EN:", "Helvetica-Bold", 9) + 6, y, value)
        y -= 16

    y -= 8

    # ── Assembly act reference ──
    c.setFont("Helvetica", 9)
    c.drawString(2*cm, y, "DE CONFORMIDAD CON EL ACTA DE ASAMBLEA DE FECHA 14 DE MARZO DE 2019")
    y -= 20

    c.drawString(2*cm, y, "HABIÉNDOSE INSCRITO ESTE CERTIFICADO EN EL REGISTRO AGRARIO NACIONAL, BAJO")
    y -= 14
    c.drawString(2*cm, y, "EL FOLIO No. RAN/CP/07023/2019/0847")
    y -= 30

    # ── Place and date ──
    c.setFont("Helvetica", 9)
    c.drawString(2*cm, y, "TUXTLA GUTIÉRREZ, CHIS. A  14  DE  MARZO  DE  2019")
    y -= 40

    # ── Signature ──
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(w/2, y, "________________________________")
    y -= 14
    c.setFont("Helvetica", 8)
    c.drawCentredString(w/2, y, "LIC. CARLOS ALBERTO MENDOZA RIVERA")
    y -= 12
    c.drawCentredString(w/2, y, "DELEGADO DEL REGISTRO AGRARIO NACIONAL")
    y -= 12
    c.drawCentredString(w/2, y, "EN EL ESTADO DE CHIAPAS")

    # ── GPS coordinates note (useful for pipeline) ──
    y -= 30
    c.setFont("Helvetica", 7)
    c.drawString(2*cm, y, "Coordenadas geográficas de referencia (centroide): Lat. 16.8912° N, Long. -93.5478° O")
    y -= 10
    c.drawString(2*cm, y, "Datum: WGS84  |  Zona UTM: 15N")

    c.save()
    print(f"  -> {path}")


if __name__ == "__main__":
    print("Generando documentos demo...")
    generate_constancia()
    generate_certificado()
    print("Listo.")
