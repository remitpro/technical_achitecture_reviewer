from crewai.tools import tool
from docx import Document
from fpdf import FPDF
import os

@tool
def generate_report(content: str, output_name: str) -> str:
    """Generate DOCX and PDF report"""

    # Generate DOCX
    doc = Document()
    for line in content.split("\n"):
        doc.add_paragraph(line)
    
    docx_path = f"{output_name}.docx"
    doc.save(docx_path)

    # Generate PDF
    pdf_path = f"{output_name}.pdf"
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", size=11)
    
    for line in content.split("\n"):
        # Very basic formatting translation to avoid rendering errors
        safe_line = line.encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 7, txt=safe_line)
        
    pdf.output(pdf_path)

    return f"Report generated: {docx_path}, {pdf_path}"