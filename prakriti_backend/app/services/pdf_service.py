import base64
from fpdf import FPDF


class PDFService:
    def generate_bulletin(self, district_name, risk_level, risk_score, top_conditions, xai_reasons, seasonal_advisory):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Arial', size=16, style='B')
        pdf.cell(200, 10, txt='PrakritiOS Health Bulletin', ln=1, align='C')
        pdf.set_font('Arial', size=14, style='B')
        pdf.cell(200, 10, txt=f'District: {district_name} | Risk: {risk_level} ({risk_score}/100)', ln=1, align='L')
        pdf.set_font('Arial', size=12)
        pdf.cell(200, 10, txt=f"Top Conditions: {', '.join(top_conditions)}", ln=1, align='L')
        pdf.ln(5)
        pdf.set_font('Arial', size=12, style='B')
        pdf.cell(200, 10, txt='AI Reasoning:', ln=1)
        pdf.set_font('Arial', size=11)
        for r in xai_reasons:
            pdf.cell(200, 8, txt=f'- {r}', ln=1)
        pdf.ln(5)
        pdf.set_font('Arial', size=12, style='B')
        pdf.cell(200, 10, txt='Seasonal Advisory:', ln=1)
        pdf.set_font('Arial', size=11)
        pdf.multi_cell(0, 10, txt=seasonal_advisory)
        path = '/tmp/bulletin.pdf'
        pdf.output(path)
        with open(path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')

    def generate_arogya_report(self, user_name, dosha, history):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Arial', size=16, style='B')
        pdf.cell(200, 10, txt='Arogya Granth — Personal Health Report', ln=1, align='C')
        pdf.set_font('Arial', size=12)
        pdf.cell(200, 10, txt=f'Patient: {user_name} | Dominant Dosha: {dosha}', ln=1)
        path = '/tmp/arogya.pdf'
        pdf.output(path)
        with open(path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')
import base64
import os
from fpdf import FPDF
class PDFService:
    def generate_bulletin(self, district_name, risk_level, risk_score, top_conditions, xai_reasons, seasonal_advisory):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=16, style='B')
        pdf.cell(200, 10, txt="PrakritiOS Health Bulletin", ln=1, align='C')
        pdf.set_font("Arial", size=14, style='B')
        pdf.cell(200, 10, txt=f"District: {district_name} | Risk: {risk_level} ({risk_score}/100)", ln=1, align='L')
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=f"Top Conditions: {', '.join(top_conditions)}", ln=1, align='L')
        pdf.ln(5)
        pdf.set_font("Arial", size=12, style='B')
        pdf.cell(200, 10, txt="AI Reasoning:", ln=1)
        pdf.set_font("Arial", size=11)
        for r in xai_reasons:
            pdf.cell(200, 8, txt=f"- {r}", ln=1)
        pdf.ln(5)
        pdf.set_font("Arial", size=12, style='B')
        pdf.cell(200, 10, txt="Seasonal Advisory:", ln=1)
        pdf.set_font("Arial", size=11)
        pdf.multi_cell(0, 10, txt=seasonal_advisory)
        
        path = "/tmp/bulletin.pdf"
        os.makedirs("/tmp", exist_ok=True)
        pdf.output(path)
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
        return b64

    def generate_arogya_report(self, user_name, dosha, history):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=16, style='B')
        pdf.cell(200, 10, txt="Arogya Report", ln=1, align='C')
        path = "/tmp/arogya.pdf"
        os.makedirs("/tmp", exist_ok=True)
        pdf.output(path)
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
        return b64
