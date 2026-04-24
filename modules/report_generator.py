import pandas as pd
from fpdf import FPDF
import matplotlib.pyplot as plt
import os
import uuid
from datetime import datetime
from modules.database_manager import leggi_config

class ReportPDF(FPDF):
    def header(self):
        conf = leggi_config()
        self.set_fill_color(0, 45, 90) # Blu Assafrica
        self.rect(0, 0, 210, 35, 'F')
        self.set_fill_color(184, 151, 93) # Oro Assafrica
        self.rect(0, 35, 210, 2, 'F')
        
        logo = conf.get('logo_istituzionale', '')
        if logo and os.path.exists(logo):
            self.image(logo, 12, 8, 22)
            self.set_xy(40, 10)
        else:
            self.set_xy(15, 10)
            
        self.set_font("helvetica", "B", 16)
        self.set_text_color(255, 255, 255)
        nome_ass = conf.get('nome_associazione', 'ASSAFRICA').upper()
        self.cell(0, 8, f"REPORT ANALITICO BUSINESS COMMUNITY", 0, 1, "L")
        
        self.set_font("helvetica", "", 10)
        self.set_xy(self.get_x() if not logo else 40, 18)
        self.cell(0, 6, f"{nome_ass} | Generato il: {datetime.now().strftime('%d/%m/%Y alle %H:%M')}", 0, 1, "L")
        self.ln(20)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(128)
        self.cell(0, 10, f"Documento Riservato ad uso interno - Pagina {self.page_no()}", 0, 0, "C")

def genera_report_dati(df):
    pdf = ReportPDF()
    pdf.add_page()
    
    COLORS_BLUES = ['#002d5a', '#004080', '#0059b3', '#3385ff', '#80b3ff', '#b3d1ff', '#e6f0ff']
    COLOR_RED = '#d9534f'
    COLOR_GREEN = '#5cb85c'
    
    # --- 1. EXECUTIVE SUMMARY ---
    pdf.set_font("helvetica", "B", 14)
    pdf.set_text_color(0, 45, 90)
    pdf.cell(0, 10, "1. Executive Summary", 0, 1)
    pdf.ln(2)
    
    totale = len(df)
    pagati = len(df[df['pagato'] == 'Pagato'])
    regolarita = (pagati / totale * 100) if totale > 0 else 0
    panafricani = len(df[df['sede'] == "Tutta l'Africa"])
    
    pdf.set_fill_color(250, 250, 250)
    pdf.set_draw_color(220, 220, 220)
    pdf.set_font("helvetica", "B", 9)
    pdf.set_text_color(100)
    
    cols = [45, 45, 45, 45]
    pdf.set_x(15)
    pdf.cell(cols[0], 8, "TOTALE AZIENDE", 1, 0, "C", True)
    pdf.cell(cols[1], 8, "IN REGOLA", 1, 0, "C", True)
    pdf.cell(cols[2], 8, "SALUTE FINANZIARIA", 1, 0, "C", True)
    pdf.cell(cols[3], 8, "PAN-AFRICANE", 1, 1, "C", True)
    
    pdf.set_x(15)
    pdf.set_font("helvetica", "B", 16)
    pdf.set_text_color(0, 45, 90)
    pdf.cell(cols[0], 15, str(totale), 1, 0, "C")
    pdf.set_text_color(40, 167, 69) if regolarita > 80 else pdf.set_text_color(220, 53, 69)
    pdf.cell(cols[1], 15, str(pagati), 1, 0, "C")
    pdf.cell(cols[2], 15, f"{regolarita:.1f}%", 1, 0, "C")
    pdf.set_text_color(0, 45, 90)
    pdf.cell(cols[3], 15, str(panafricani), 1, 1, "C")
    pdf.ln(10)

    # --- 2. GRAFICO DONUT ---
    run_id = str(uuid.uuid4())[:8]
    pdf.set_font("helvetica", "B", 14)
    pdf.cell(0, 10, "2. Composizione Settoriale del Network", 0, 1)
    
    fig, ax = plt.subplots(figsize=(8, 4))
    settori_counts = df['categoria'].value_counts()
    wedges, texts, autotexts = ax.pie(settori_counts, autopct='%1.1f%%', colors=COLORS_BLUES[:len(settori_counts)], pctdistance=0.8, textprops={'color':"w", 'weight':"bold", 'fontsize':8})
    ax.add_artist(plt.Circle((0,0), 0.60, fc='white'))
    ax.legend(wedges, settori_counts.index, title="Settori", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1), fontsize=8)
    
    pie_path = f"temp_donut_{run_id}.png"
    plt.savefig(pie_path, bbox_inches='tight', dpi=200, transparent=True)
    plt.close()
    pdf.image(pie_path, x=15, y=pdf.get_y()+2, w=150)
    pdf.set_y(pdf.get_y() + 85)
    if os.path.exists(pie_path): os.remove(pie_path)

    # --- 3. ANALISI GEOGRAFICA (IL PUNTO DOVE CRASHAVA) ---
    pdf.add_page()
    pdf.set_font("helvetica", "B", 14)
    pdf.cell(0, 10, "3. Analisi Mercati e Rischio Quote", 0, 1)
    pdf.ln(2)
    
    paesi_flat = []
    for p in df['sede']:
        # TRATTAMENTO DI SICUREZZA: trasforma tutto in stringa e pulisce
        p_str = str(p) if p is not None else ""
        if p_str and p_str != "nan" and p_str != "Tutta l'Africa":
            # Dividiamo solo se è una stringa valida
            paesi_flat.extend([x.strip() for x in p_str.split(",") if x.strip()])
    
    if paesi_flat:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
        pd.Series(paesi_flat).value_counts().head(8).sort_values().plot(kind='barh', ax=ax1, color=COLORS_BLUES[1])
        ax1.set_title("Top 8 Mercati", fontsize=10, weight='bold')
        
        pag_sett = df.groupby(['categoria', 'pagato']).size().unstack(fill_value=0)
        for col in ['Pagato', 'In attesa']: 
            if col not in pag_sett: pag_sett[col] = 0
        pag_sett.sort_values(by='In attesa').tail(6).plot(kind='barh', stacked=True, ax=ax2, color=[COLOR_RED, COLOR_GREEN])
        ax2.set_title("Rischio Quote per Settore", fontsize=10, weight='bold')
        
        plt.tight_layout()
        dual_path = f"temp_dual_{run_id}.png"
        plt.savefig(dual_path, bbox_inches='tight', dpi=200, transparent=True)
        plt.close()
        pdf.image(dual_path, x=10, y=pdf.get_y(), w=190)
        pdf.set_y(pdf.get_y() + 85)
        if os.path.exists(dual_path): os.remove(dual_path)

    # --- 4. TABELLA ---
    pdf.add_page()
    pdf.set_font("helvetica", "B", 14)
    pdf.cell(0, 10, "4. Elenco Sintetico Associati", 0, 1)
    pdf.ln(5)
    
    pdf.set_fill_color(0, 45, 90)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("helvetica", "B", 8)
    w_nome, w_cat, w_ref, w_stato = 65, 55, 45, 25
    pdf.cell(w_nome, 8, " RAGIONE SOCIALE", 1, 0, "L", True)
    pdf.cell(w_cat, 8, " SETTORE", 1, 0, "L", True)
    pdf.cell(w_ref, 8, " REFERENTE", 1, 0, "L", True)
    pdf.cell(w_stato, 8, " QUOTA", 1, 1, "C", True)
    
    pdf.set_text_color(40, 40, 40)
    pdf.set_font("helvetica", "", 8)
    fill = False
    for _, row in df.sort_values(by=['pagato', 'nome'], ascending=[False, True]).iterrows():
        pdf.set_fill_color(245, 248, 250)
        pdf.cell(w_nome, 7, f" {str(row['nome'])[:40]}", 'B', 0, "L", fill)
        pdf.cell(w_cat, 7, f" {str(row['categoria'])[:30]}", 'B', 0, "L", fill)
        ref = str(row['referente']) if pd.notna(row['referente']) else ""
        pdf.cell(w_ref, 7, f" {ref[:25]}", 'B', 0, "L", fill)
        
        pdf.set_text_color(40, 167, 69) if row['pagato'] == 'Pagato' else pdf.set_text_color(220, 53, 69)
        pdf.cell(w_stato, 7, "REGOLARE" if row['pagato'] == 'Pagato' else "IN ATTESA", 'B', 1, "C", fill)
        pdf.set_text_color(40, 40, 40)
        fill = not fill

    file_path = "Analisi_Network_Assafrica_2026.pdf"
    pdf.output(file_path)
    return file_path