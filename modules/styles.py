import streamlit as st

# --- COLORI ISTITUZIONALI ---
BLU_ASSAFRICA = "#002d5a"  # Il blu profondo usato nei PDF
ORO_ASSAFRICA = "#b8975d"  # L'oro usato per le linee di divisione
BIANCO = "#ffffff"
SFONDO_GRIGIO = "#f8f9fa"

def apply_styles():
    """Applica il CSS per ottimizzare lo spazio e il brand"""
    st.markdown(f"""
        <style>
            /* 1. OTTIMIZZAZIONE SPAZIO VERTICALE (Riduzione padding) */
            .block-container {{
                padding-top: 1rem !important;
                padding-bottom: 0rem !important;
                max-width: 95% !important;
            }}
            
            /* Nasconde il menu Streamlit e il footer per un look "embedded" */
            #MainMenu, footer {{visibility: hidden;}}
            header {{visibility: hidden;}}

            /* 2. STILE TAB (Brand Assafrica) */
            .stTabs [data-baseweb="tab-list"] {{
                gap: 8px;
                background-color: transparent;
            }}
            .stTabs [data-baseweb="tab"] {{
                background-color: {BIANCO};
                border: 1px solid #eee;
                border-radius: 5px 5px 0 0;
                padding: 5px 15px;
                height: 40px;
                font-weight: 600;
                color: #666;
            }}
            .stTabs [data-baseweb="tab"]:hover {{
                color: {BLU_ASSAFRICA};
            }}
            .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {{
                background-color: {BLU_ASSAFRICA} !important;
                color: {BIANCO} !important;
                border-bottom: 3px solid {ORO_ASSAFRICA} !important;
            }}

            /* 3. STILE PULSANTI */
            .stButton>button {{
                width: 100%;
                border-radius: 6px;
                border: 1px solid {BLU_ASSAFRICA};
                background-color: {BIANCO};
                color: {BLU_ASSAFRICA};
                font-weight: 700;
                transition: 0.3s;
            }}
            .stButton>button:hover {{
                background-color: {BLU_ASSAFRICA};
                color: {BIANCO};
                border-color: {ORO_ASSAFRICA};
            }}
            
            /* Pulsanti 'Primary' (quelli importanti) */
            div[data-testid="stMarkdownContainer"] + div button {{
                /* Se vuoi differenziare i pulsanti primari */
            }}

            /* 4. ALTRI DETTAGLI */
            .main {{ background-color: {SFONDO_GRIGIO}; }}
            h1, h2, h3 {{ 
                color: {BLU_ASSAFRICA}; 
                margin-top: -20px !important; 
                padding-bottom: 10px;
            }}
            .stExpander {{ border: 1px solid {ORO_ASSAFRICA} !important; }}
        </style>
    """, unsafe_allow_html=True)