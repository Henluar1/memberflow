from fpdf import FPDF
import datetime

from fpdf import FPDF
import datetime
import os
from modules.database_manager import leggi_config

class ReportPDF(FPDF):
    def header(self):
        conf = leggi_config()
        logo_inst = conf.get('logo_istituzionale', '')
        nome_ass = conf.get('nome_associazione', 'Associazione')

        if logo_inst and os.path.exists(logo_inst):
            self.image(logo_inst, 10, 8, 20)
        
        self.set_font("helvetica", "B", 15)
        self.set_text_color(0, 45, 90)
        self.cell(0, 10, f"REPORT ANALITICO - {nome_ass.upper()}", ln=True, align="C")
        self.set_font("helvetica", "I", 8)
        self.cell(0, 5, f"Data report: {datetime.datetime.now().strftime('%d/%m/%Y')}", ln=True, align="C")
        self.ln(10)
        
def genera_report_dati(df):
    pdf = ReportPDF()
    pdf.add_page()
    
    # --- RIASSUNTO NUMERICO ---
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 10, "1. Riepilogo Numerico", ln=True)
    pdf.set_font("helvetica", "", 10)
    
    totale = len(df)
    pagati = len(df[df['pagato'] == 'Pagato'])
    scoperti = totale - pagati
    
    pdf.cell(0, 8, f"Totale Associati a sistema: {totale}", ln=True)
    pdf.cell(0, 8, f"Soci in regola con i pagamenti: {pagati}", ln=True)
    pdf.cell(0, 8, f"Soci con pagamento in attesa: {scoperti}", ln=True)
    pdf.ln(5)

    # --- TABELLA SETTORI ---
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 10, "2. Distribuzione per Settore", ln=True)
    
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("helvetica", "B", 10)
    pdf.cell(100, 8, "Settore Merceologico", 1, 0, "C", True)
    pdf.cell(40, 8, "N. Soci", 1, 1, "C", True)
    
    pdf.set_font("helvetica", "", 10)
    stats = df['categoria'].value_counts()
    for cat, count in stats.items():
        pdf.cell(100, 8, cat, 1)
        pdf.cell(40, 8, str(count), 1, 1, "C")
    
    file_path = "Report_Analytics.pdf"
    pdf.output(file_path)
    return file_path