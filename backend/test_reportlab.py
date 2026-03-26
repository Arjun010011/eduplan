print("Loading modules...")
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
import tempfile
import os

print("Modules loaded.")
pdf_path = os.path.join(tempfile.mkdtemp(), "test.pdf")
print("PDF path:", pdf_path)
doc = SimpleDocTemplate(
    pdf_path,
    pagesize=A4,
    leftMargin=2.5 * cm,
    rightMargin=2.5 * cm,
    topMargin=2 * cm,
    bottomMargin=2 * cm,
    title="Test"
)
print("Doc created.")
story = []
table_rows = [["1", "2", "3", "4", "5"]]
table = Table(table_rows, repeatRows=1, colWidths=[1.5*cm, 4*cm, 4.5*cm, 4.5*cm, 1.5*cm])
story.append(table)
print("Building doc...")
doc.build(story)
print("Done without hanging!")
