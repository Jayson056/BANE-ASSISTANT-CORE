import sys
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable

def md_to_pdf(input_path, output_path):
    doc = SimpleDocTemplate(output_path, pagesize=LETTER)
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'MainTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor("#003366"),
        spaceAfter=20,
        alignment=1 # Center
    )
    
    heading2_style = ParagraphStyle(
        'H2',
        parent=styles['Heading2'],
        fontSize=18,
        textColor=colors.HexColor("#005599"),
        spaceBefore=15,
        spaceAfter=10
    )

    body_style = styles['BodyText']
    body_style.fontSize = 12
    body_style.leading = 14

    elements = []
    
    try:
        with open(input_path, 'r') as f:
            lines = f.readlines()
            
        for line in lines:
            line = line.strip()
            if not line:
                elements.append(Spacer(1, 12))
                continue
                
            if line.startswith("# "):
                elements.append(Paragraph(line[2:], title_style))
                elements.append(HRFlowable(width="100%", thickness=1, color=colors.grey))
            elif line.startswith("## "):
                elements.append(Paragraph(line[3:], heading2_style))
            elif line.startswith("### "):
                elements.append(Paragraph(f"<b>{line[4:]}</b>", styles['Heading3']))
            elif line.startswith("* ") or line.startswith("- "):
                elements.append(Paragraph(f"• {line[2:]}", body_style))
            elif line.startswith("---"):
                elements.append(HRFlowable(width="80%", thickness=0.5, color=colors.lightgrey))
            else:
                # Simplified rendering without manual bold/italic tagging to avoid parse errors
                elements.append(Paragraph(line, body_style))
                
        doc.build(elements)
        print(f"✅ Created PDF at {output_path}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python pdf_gen.py input.md output.pdf")
    else:
        md_to_pdf(sys.argv[1], sys.argv[2])
