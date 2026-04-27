import streamlit as st
from modules.database_manager import leggi_config

conf = leggi_config()
nome_ass = conf.get('nome_associazione', 'Assafrica')

st.title(f"🏛️ Benvenuto in MemberFlow {nome_ass}")

st.markdown(f"""
### Portale Gestionale Business Community 2026
Utilizza il menu laterale per navigare tra le diverse sezioni operative:

* **➕ Nuovo Socio**: Per registrare singole aziende o effettuare importazioni massive da Excel.
* **📊 Dashboard**: Per la gestione delle anagrafiche, analisi BI e monitoraggio pagamenti.
* **🎨 Marketing**: Per generare banner social e locandine eventi coordinati.
* **🌍 Mappa Network**: Visualizzazione geografica della presenza degli associati.
""")

st.info(f"Sede: {conf.get('indirizzo', 'Non configurata')} | Email: {conf.get('email_contatto', 'Non configurata')}")