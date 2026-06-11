from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import Table
from django.conf import settings
import os


def generate_will_pdf(will):

    filename = f"will_{will.id}.pdf"
    file_path = os.path.join(settings.MEDIA_ROOT, "wills", filename)

    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    doc = SimpleDocTemplate(file_path)
    elements = []

    styles = getSampleStyleSheet()

    elements.append(Paragraph("<b>Digital Will Document</b>", styles["Title"]))
    elements.append(Spacer(1, 0.5 * inch))

    elements.append(Paragraph(f"Testator: {will.testator.name}", styles["Normal"]))
    elements.append(Paragraph(f"Created At: {will.created_at}", styles["Normal"]))
    elements.append(Spacer(1, 0.3 * inch))

    data = [["Asset", "Beneficiary", "Share %"]]

    for dist in will.assetdistribution_set.all():
        data.append([
            dist.asset.name,
            dist.beneficiary.name,
            str(dist.share_percentage)
        ])

    table = Table(data)
    table.setStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
    ])

    elements.append(table)

    doc.build(elements)

    return f"wills/{filename}"