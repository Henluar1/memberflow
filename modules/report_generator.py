import pandas as pd
from fpdf import FPDF
import matplotlib.pyplot as plt
import os
from datetime import datetime
from modules.database_manager import leggi_config

class ReportPDF(FPDF):
    def header(self):
        conf = leggi_config()
        # Fascia blu istituzionale in alto
        self.set_fill_color(0, 45, 90) # Blu Assafrica
        self.rect(0, 0, 210, 40, 'F')
        
        # Logo Istituzionale
        logo = conf.get('logo_istituzionale', '')
        if logo and os.path.exists(logo):
            self.image(logo, 12, 10, 22)
            self.set_xy(40, 12)
        else:
            self.set_xy(15, 12)
            
        self.set_font("Arial", "B", 16)
        self.set_text_color(255, 255, 255)
        nome_ass = conf.get('nome_associazione', 'ASSAFRICA').upper()
        self.cell(0, 10, f"REPORT ANALITICO - {nome_ass}", 0, 1, "L")
        
        self.set_font("Arial", "I", 9)
        self.set_xy(self.get_x() if not logo else 40, 20)
        self.cell(0, 10, f"Data Generazione: {datetime.now().strftime('%d/%m/%Y %H:%M')}", 0, 1, "L")
        self.ln(20)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.set_text_color(128)
        self.cell(0, 10, f"Documento Riservato - Business Community Network 2026 - Pagina {self.page_no()}", 0, 0, "C")

def genera_report_dati(df):
    pdf = ReportPDF()
    pdf.add_page()
    
    # --- 1. EXECUTIVE SUMMARY (KPI BOXES) ---
    pdf.set_font("Arial", "B", 14)
    pdf.set_text_color(0, 45, 90)
    pdf.cell(0, 10, "1. Executive Summary", 0, 1)
    pdf.ln(5)
    
    # Prepariamo i dati
    totale = len(df)
    pagati = len(df[df['pagato'] == 'Pagato'])
    regolarita = (pagati / totale * 100) if totale > 0 else 0
    panafricani = len(df[df['sede'] == "Tutta l'Africa"])
    
    # Box grafici per i KPI
    pdf.set_fill_color(245, 247, 249)
    pdf.set_draw_color(200, 200, 200)
    pdf.set_font("Arial", "B", 10)
    pdf.set_text_color(100)
    
    # Intestazioni KPI
    cols = [45, 45, 45, 45]
    pdf.cell(cols[0], 10, "TOTALE SOCI", 1, 0, "C", True)
    pdf.cell(cols[1], 10, "IN REGOLA", 1, 0, "C", True)
    pdf.cell(cols[2], 10, "% REGOLARITA", 1, 0, "C", True)
    pdf.cell(cols[3], 10, "PAN-AFRICANI", 1, 1, "C", True)
    
    # Valori KPI
    pdf.set_font("Arial", "B", 14)
    pdf.set_text_color(0, 45, 90)
    pdf.cell(cols[0], 15, str(totale), 1, 0, "C")
    pdf.cell(cols[1], 15, str(pagati), 1, 0, "C")
    pdf.cell(cols[2], 15, f"{regolarita:.1f}%", 1, 0, "C")
    pdf.cell(cols[3], 15, str(panafricani), 1, 1, "C")
    pdf.ln(15)

    # --- 2. GRAFICO DISTRIBUZIONE SETTORIALE ---
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "2. Analisi Merceologica", 0, 1)
    
    # Generiamo il grafico con Matplotlib
    plt.figure(figsize=(6, 4))
    colors = ['#004A99', '#2E86C1', '#5DADE2', '#AED6F1', '#D6EAF8']
    df['categoria'].value_counts().plot(kind='pie', autopct='%1.1f%%', colors=colors, startangle=140)
    plt.ylabel("")
    plt.axis('equal')
    
    chart_path = "temp_pie.png"
    plt.savefig(chart_path, bbox_inches='tight', dpi=150)
    plt.close()
    
    pdf.image(chart_path, x=45, y=pdf.get_y()+5, w=120)
    pdf.set_y(pdf.get_y() + 95)
    os.remove(chart_path)

    # --- 3. ANALISI GEOGRAFICA (BAR CHART) ---
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "3. Penetrazione Mercati (Top 10 Paesi)", 0, 1)
    
    # Calcolo dei paesi più presidiati
    paesi_flat = []
    for p in df['sede'].dropna():
        if p != "Tutta l'Africa":
            paesi_flat.extend([x.strip() for x in str(p).split(",")])
    
    if paesi_flat:
        df_paesi = pd.Series(paesi_flat).value_counts().head(10)
        plt.figure(figsize=(7, 4))
        df_paesi.sort_values().plot(kind='barh', color='#004A99')
        plt.xlabel("Numero Aziende")
        
        bar_path = "temp_bar.png"
        plt.savefig(bar_path, bbox_inches='tight', dpi=150)
        plt.close()
        pdf.image(bar_path, x=30, y=pdf.get_y()+5, w=150)
        pdf.set_y(pdf.get_y() + 100)
        os.remove(bar_path)

    # --- 4. DETTAGLIO ANALITICO (TABELLA) ---
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "4. Elenco Sintetico Soci", 0, 1)
    pdf.ln(5)
    
    # Header Tabella
    pdf.set_fill_color(0, 45, 90)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 9)
    pdf.cell(60, 8, " RAGIONE SOCIALE", 1, 0, "L", True)
    pdf.cell(55, 8, " SETTORE", 1, 0, "L", True)
    pdf.cell(40, 8, " REFERENTE", 1, 0, "L", True)
    pdf.cell(35, 8, " STATO QUOTA", 1, 1, "C", True)
    
    # Righe Tabella
    pdf.set_text_color(0)
    pdf.set_font("Arial", "", 8)
    fill = False
    for _, row in df.iterrows():
        pdf.set_fill_color(248, 249, 250)
        pdf.cell(60, 7, f" {str(row['nome'])[:35]}", 1, 0, "L", fill)
        pdf.cell(55, 7, f" {str(row['categoria'])}", 1, 0, "L", fill)
        pdf.cell(40, 7, f" {str(row['referente'])}", 1, 0, "L", fill)
        
        # Colore dinamico per lo stato pagamento
        if row['pagato'] == 'Pagato':
            pdf.set_text_color(40, 167, 69) # Verde
        else:
            pdf.set_text_color(220, 53, 69) # Rosso
            
        pdf.cell(35, 7, row['pagato'], 1, 1, "C", fill)
        pdf.set_text_color(0)
        fill = not fill # Effetto "zebra"

    file_path = "Analisi_Network_Assafrica_2026.pdf"
    pdf.output(file_path)
    return file_path