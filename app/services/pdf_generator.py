from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Spacer,
    Paragraph,
    Table,
    TableStyle,
    PageBreak,
)
from typing import Optional


def generate_trophy_pdf(
    trophy_data: dict,
    measurement: dict,
    measurer_name: Optional[str] = None,
    output_path: str = "/tmp/trophy.pdf",
) -> str:
    """
    Generate a PDF trophy certificate.

    Args:
        trophy_data: dict with keys: id, name, species, hunt_date, location,
                     owner_name, status, version
        measurement: dict with keys: method_id, length_cm, width_cm, total_cm,
                     measurement_date, algorithm_version
        measurer_name: optional name of the measurer
        output_path: path where PDF will be saved

    Returns:
        output_path: the path where the PDF was saved
    """
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
        leftMargin=15 * mm,
        rightMargin=15 * mm,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "TrophyTitle",
        parent=styles["Heading1"],
        fontSize=18,
        spaceAfter=6 * mm,
        textColor=HexColor("#1a1a1a"),
        alignment=1,  # center
        fontName="Helvetica-Bold",
    )

    heading_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontSize=12,
        spaceBefore=4 * mm,
        spaceAfter=2 * mm,
        textColor=HexColor("#2c3e50"),
        fontName="Helvetica-Bold",
    )

    body_style = ParagraphStyle(
        "BodyText",
        parent=styles["Normal"],
        fontSize=10,
        spaceAfter=2 * mm,
        fontName="Helvetica",
    )

    bold_style = ParagraphStyle(
        "BoldText",
        parent=styles["Normal"],
        fontSize=10,
        spaceAfter=2 * mm,
        fontName="Helvetica-Bold",
    )

    # Collect content
    elements = []

    # Title
    elements.append(Paragraph("DIGITAL TROPHY CERTIFICATE", title_style))
    elements.append(Spacer(1, 3 * mm))

    # Trophy info section
    elements.append(Paragraph("TROPHY INFORMATION", heading_style))

    trophy_table_data = [
        [Paragraph("<b>Trophy ID:</b>", bold_style), Paragraph(str(trophy_data.get("id", "N/A")), body_style)],
        [Paragraph("<b>Name:</b>", bold_style), Paragraph(str(trophy_data.get("name", "N/A")), body_style)],
        [Paragraph("<b>Species:</b>", bold_style), Paragraph(str(trophy_data.get("species", "N/A")), body_style)],
        [Paragraph("<b>Hunt Date:</b>", bold_style), Paragraph(str(trophy_data.get("hunt_date", "N/A")), body_style)],
        [Paragraph("<b>Location:</b>", bold_style), Paragraph(str(trophy_data.get("location", "N/A")), body_style)],
        [Paragraph("<b>Owner:</b>", bold_style), Paragraph(str(trophy_data.get("owner_name", "N/A")), body_style)],
        [Paragraph("<b>Status:</b>", bold_style), Paragraph(str(trophy_data.get("status", "N/A")), body_style)],
        [Paragraph("<b>Version:</b>", bold_style), Paragraph(str(trophy_data.get("version", "N/A")), body_style)],
    ]

    trophy_table = Table(trophy_table_data, colWidths=[40 * mm, 100 * mm])
    trophy_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#cccccc")),
        ("BACKGROUND", (0, 0), (0, -1), HexColor("#f0f4f8")),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    elements.append(trophy_table)

    # Measurement section
    elements.append(Paragraph("MEASUREMENT DATA", heading_style))

    method_name = "Method 6 (Carnivores)" if measurement.get("method_id") == 6 else f"Method {measurement.get('method_id', 'N/A')}"

    measurement_table_data = [
        [Paragraph("<b>Method:</b>", bold_style), Paragraph(method_name, body_style)],
        [Paragraph("<b>Length (cm):</b>", bold_style),
         Paragraph(f"{measurement.get('length_cm', 0):.2f}", body_style)],
        [Paragraph("<b>Width (cm):</b>", bold_style),
         Paragraph(f"{measurement.get('width_cm', 0):.2f}", body_style)],
        [Paragraph("<b>Total Score:</b>", bold_style),
         Paragraph(f"{measurement.get('total_cm', 0):.2f}", body_style)],
        [Paragraph("<b>Measurement Date:</b>", bold_style),
         Paragraph(str(measurement.get("measurement_date", "N/A")), body_style)],
        [Paragraph("<b>Algorithm:</b>", bold_style),
         Paragraph(str(measurement.get("algorithm_version", "N/A")), body_style)],
    ]

    if measurer_name:
        measurement_table_data.append(
            [Paragraph("<b>Measurer:</b>", bold_style),
             Paragraph(str(measurer_name), body_style)]
        )

    measurement_table = Table(measurement_table_data, colWidths=[40 * mm, 100 * mm])
    measurement_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#cccccc")),
        ("BACKGROUND", (0, 0), (0, -1), HexColor("#f0f4f8")),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    elements.append(measurement_table)

    # Warning
    elements.append(Spacer(1, 8 * mm))
    warning_style = ParagraphStyle(
        "Warning",
        parent=styles["Normal"],
        fontSize=8,
        textColor=HexColor("#c0392b"),
        fontName="Helvetica-Oblique",
        alignment=1,
    )
    elements.append(Paragraph(
        "WARNING: PDF is not a replacement for official paper/expert procedure",
        warning_style,
    ))

    # Build PDF
    doc.build(elements)

    return output_path
