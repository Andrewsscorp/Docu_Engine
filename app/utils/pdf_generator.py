from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import io

def generar_pdf_fuid(subserie_nombre, registros):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter), rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        name='TitleStyle',
        parent=styles['Heading1'],
        alignment=1, # Center
        fontSize=14,
        spaceAfter=10
    )
    
    header_style = ParagraphStyle(
        name='HeaderStyle',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=5
    )
    
    # Title
    elements.append(Paragraph("FORMATO ÚNICO DE INVENTARIO DOCUMENTAL - FUID", title_style))
    elements.append(Spacer(1, 0.2 * inch))
    
    # Institutional Header
    header_data = [
        ["ENTIDAD REMITENTE:", "ENTIDAD PRODUCTORA:", "UNIDAD ADMINISTRATIVA:", "OBJETO:"],
        ["ALCALDÍA MUNICIPAL", "SECRETARÍA GENERAL", "ARCHIVO CENTRAL", "TRANSFERENCIA PRIMARIA"]
    ]
    
    header_table = Table(header_data, colWidths=[2 * inch, 2 * inch, 2.5 * inch, 2.5 * inch])
    header_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 0.3 * inch))
    
    elements.append(Paragraph(f"<b>SUBSERIE:</b> {subserie_nombre}", header_style))
    elements.append(Spacer(1, 0.2 * inch))
    
    # Grid Data
    grid_data = [["No.\nORDEN", "CÓDIGO", "NOMBRE DE LA UNIDAD\nDE CONSERVACIÓN", "FECHAS EXTREMAS\n(Inicial - Final)", "CAJA /\nCARPETA", "FOLIOS", "SOPORTE"]]
    
    for r in registros:
        fechas = f"{r['fecha_inicial_str']} - {r['fecha_final_str']}" if r.get('fecha_inicial_str') else "Sin fechas"
        grid_data.append([
            str(r.get('no_orden', '')),
            str(r.get('codigo', '')),
            str(r.get('nombre_unidad_conservacion', '')),
            fechas,
            str(r.get('caja_carpeta', 'N/A')),
            str(r.get('folios', 0)),
            str(r.get('soporte', 'ELECTRÓNICO'))
        ])
        
    grid_table = Table(grid_data, colWidths=[0.6*inch, 2*inch, 3*inch, 1.8*inch, 0.8*inch, 0.6*inch, 1*inch])
    grid_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4f46e5')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    
    elements.append(grid_table)
    
    # Signatures
    elements.append(Spacer(1, 0.5 * inch))
    sig_data = [
        ["ELABORADO POR:", "ENTREGADO POR:", "RECIBIDO POR:"],
        ["_________________________", "_________________________", "_________________________"],
        ["Nombre:", "Nombre:", "Nombre:"],
        ["Cargo:", "Cargo:", "Cargo:"],
        ["Firma:", "Firma:", "Firma:"]
    ]
    sig_table = Table(sig_data, colWidths=[3*inch, 3*inch, 3*inch])
    sig_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(sig_table)
    
    doc.build(elements)
    
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
