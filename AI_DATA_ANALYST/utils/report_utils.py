import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def create_pdf_report(report_path: str, title: str, summary: dict, insight: dict):
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    c = canvas.Canvas(report_path, pagesize=A4)
    width, height = A4

    y = height - 50
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, title)

    y -= 40
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Analysis Summary")
    y -= 20
    c.setFont("Helvetica", 10)

    for key, value in summary.items():
        text = f"{key}: {value}"
        c.drawString(50, y, text[:110])
        y -= 15
        if y < 100:
            c.showPage()
            y = height - 50

    y -= 10
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "AI Insight")
    y -= 20
    c.setFont("Helvetica", 10)

    for key, value in insight.items():
        text = f"{key}: {value}"
        c.drawString(50, y, text[:110])
        y -= 15
        if y < 100:
            c.showPage()
            y = height - 50

    c.save()