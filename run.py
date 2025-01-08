# run.py
import streamlit as st
import os
from dotenv import load_dotenv
from utils.models import LLMFactory
from invoke import generate_instructions
import logging
import time
import openai
from openai import OpenAI

# ATTENZIONE: Questa è una soluzione temporanea solo per testing
# NON committare mai la chiave API nel codice!
OPENAI_API_KEY = "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" # Inserisci qui la tua chiave

# Configurazione diretta di OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

st.write("DEBUG - Chiave API configurata:", OPENAI_API_KEY[:10] + "...")

# Test immediato della connessione
try:
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Say hello!"}],
        temperature=0.7
    )
    st.write("DEBUG - Test connessione OpenAI riuscito!")
except Exception as e:
    st.write("DEBUG - Errore connessione OpenAI:", str(e))

# Configure logging per catturare i messaggi anche nell'UI
class StreamlitHandler(logging.Handler):
    def __init__(self, progress_placeholder, log_placeholder):
        super().__init__()
        self.progress_placeholder = progress_placeholder
        self.log_placeholder = log_placeholder
        self.log_text = ""
        self.current_section = ""
        self.total_sections = 0
        self.completed_sections = 0

    def emit(self, record):
        try:
            # Filtra i messaggi HTTP
            if "HTTP Request" in record.getMessage():
                return
                
            log_entry = self.format(record)
            self.log_text = log_entry + "\n" + self.log_text  # Aggiunge nuovi log in cima
            
            # Aggiorna progress bar e stato
            if "PLANNING THE WRITING" in log_entry:
                self.progress_placeholder.progress(0.2)
                self.current_section = "📝 Pianificazione in corso..."
            elif "Piano generato con successo" in log_entry:
                self.progress_placeholder.progress(0.4)
                self.current_section = "✅ Piano completato!"
            elif "WRITING THE DOC" in log_entry:
                self.progress_placeholder.progress(0.6)
                self.current_section = "✍️ Scrittura articolo..."
            elif "Sezione" in log_entry and "completata" in log_entry:
                self.completed_sections += 1
                progress = 0.6 + (0.3 * (self.completed_sections / max(5, self.total_sections)))
                self.progress_placeholder.progress(min(0.9, progress))
            elif "SAVING THE DOC" in log_entry:
                self.progress_placeholder.progress(1.0)
                self.current_section = "💾 Salvataggio completato!"

            # Aggiorna status e log
            status_html = f"""
            <div style="padding: 10px; border-radius: 5px; background-color: #f0f2f6; margin-bottom: 10px">
                <h3 style="color: #0066cc; margin: 0;">Status: {self.current_section}</h3>
            </div>
            """
            self.log_placeholder.markdown(status_html, unsafe_allow_html=True)
            
            # Mostra gli ultimi log in un'area scrollabile
            self.log_placeholder.code(self.log_text, language=None)
            
        except Exception:
            self.handleError(record)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

# Load environment variables
load_dotenv()

# Initialize LLM Factory and get model instance
llm_factory = LLMFactory()
LLM = llm_factory.get_llm(
        # Seleziona il provider del modello LLM:
        # - 'huggingface': Utilizza i modelli di HuggingFace Hub (es. StarCoderBase)
        # - 'claude': Utilizza i modelli di Anthropic Claude
        # - 'openai': Utilizza i modelli di OpenAI (es. GPT-3.5, GPT-4)
        # - 'ollama': Utilizza modelli locali tramite Ollama
        # - 'huggingface': Utilizza modelli su HuggingFace
        provider='openai',
        
        # Specifica il modello da utilizzare:
        # Per HuggingFace:
        # - "bigcode/starcoderbase-1b": Versione leggera ottimizzata per Mac M3 (8GB RAM)
        # Per OpenAI:
        # - None: Usa il default (gpt-3.5-turbo)
        # Per Claude:
        # - None: Usa il default (claude-3-sonnet-20240229)
        # Per Ollama:
        # - "mistral": Modello Mistral base
        # - "llama3.2": Modello Llama 2
        # Per HuggingFace_
        # - "HFModels.LLAMA.value": modello llama3.2
        model=None,
        
        # Controlla la creatività del modello:
        # - 0.0: Risposte più deterministiche e conservative
        # - 1.0: Risposte più creative e variabili
        # - 0.1: Valore basso consigliato per compiti di programmazione
        temperature=0.7
)

def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "topic" not in st.session_state:
        st.session_state.topic = None
    if "plan" not in st.session_state:
        st.session_state.plan = None
    if "article" not in st.session_state:
        st.session_state.article = None
    if "writing_complete" not in st.session_state:
        st.session_state.writing_complete = False

def main_chat():
    st.title("💭 iNexus for Writing")
    st.markdown("### Your AI Article Writing Assistant")
    
    initialize_session_state()
    
    # Topic selection if not already chosen
    if not st.session_state.topic:
        st.markdown("### 📝 Prima di iniziare")
        topic = st.text_input("Su quale argomento dobbiamo scrivere l'articolo?")
        
        if st.button("Inizia", type="primary"):
            if topic:
                st.session_state.topic = topic
                
                # Crea container per progress bar e log
                progress_placeholder = st.empty()
                status_placeholder = st.empty()
                log_placeholder = st.empty()
                
                with st.spinner("Generazione in corso..."):
                    progress_bar = progress_placeholder.progress(0)
                    streamlit_handler = StreamlitHandler(progress_bar, status_placeholder)
                    logging.getLogger().addHandler(streamlit_handler)
                    
                    try:
                        result = generate_instructions(LLM, topic)
                        
                        if result.get('plan'):
                            st.session_state.plan = result['plan']
                            if result.get('final_doc'):
                                st.session_state.article = result['final_doc']
                                st.session_state.writing_complete = True
                                st.balloons()
                                # Rimossi i messaggi di sistema
                        
                    except Exception as e:
                        st.error(f"Errore durante la generazione: {str(e)}")
                    
                    finally:
                        logging.getLogger().removeHandler(streamlit_handler)
                
                st.rerun()
            else:
                st.warning("Per favore, inserisci un argomento")
    else:
        # Sidebar con piano e articolo
        with st.sidebar:
            st.markdown(f"**Argomento:** {st.session_state.topic}")
            
            with st.expander("📋 Piano dell'Articolo", expanded=True):
                if st.session_state.plan:  # Verifica che il piano esista
                    st.text_area(
                        label="Piano dell'Articolo",
                        value=st.session_state.plan,
                        height=300,
                        key="piano_text"
                    )
                    st.download_button(
                        label="📥 Download Piano",
                        data=st.session_state.plan or "",  # Fornisce stringa vuota come fallback
                        file_name=f"piano_{st.session_state.topic.lower().replace(' ', '_')}.md",
                        mime="text/markdown",
                        key="download_piano"
                    )
                else:
                    st.info("Piano non ancora generato")
            
            with st.expander("📄 Articolo Completo", expanded=True):
                if st.session_state.article:  # Verifica che l'articolo esista
                    st.text_area(
                        label="Articolo Completo",
                        value=st.session_state.article,
                        height=500,
                        key="articolo_text"
                    )
                    st.download_button(
                        label="📥 Download Articolo",
                        data=st.session_state.article or "",  # Fornisce stringa vuota come fallback
                        file_name=f"articolo_{st.session_state.topic.lower().replace(' ', '_')}.md",
                        mime="text/markdown",
                        key="download_articolo"
                    )
                else:
                    st.info("Articolo non ancora generato")
            
            if st.button("Cambia Argomento", type="primary"):
                st.session_state.topic = None
                st.session_state.plan = None
                st.session_state.article = None
                st.session_state.messages = []
                st.session_state.writing_complete = False
                st.rerun()
        
        # Area principale per la chat
        if st.session_state.writing_complete:
            st.markdown("### 💬 Suggerisci miglioramenti")
            if prompt := st.text_input("Come miglioreresti questo articolo?", key="improvement_input"):
                with st.spinner("Elaboro le modifiche..."):
                    # Prompt migliorato e più specifico
                    full_prompt = f"""Sei un editor esperto nella revisione di articoli. 
                    Stai lavorando sulla revisione di un articolo sul tema: {st.session_state.topic}

                    STRUTTURA GIA' PIANIFICATA E PRESENTE NEL CONTENUTO:
                    {st.session_state.plan}

                    RICHIESTA DI MODIFICA:
                    {prompt}

                    Per favore fornisci suggerimenti specifici e actionable per migliorare l'articolo.
                    Considera:
                    1. Aderenza al piano originale
                    2. Accuratezza e completezza delle informazioni
                    3. Chiarezza e fluidità del testo
                    4. Coerenza con il topic principale
                    5. Eventuali punti mancanti o da approfondire

                    Struttura la tua risposta in modo chiaro e specifico, indicando esattamente dove 
                    e come apportare le modifiche suggerite.
                    """
                    
                    st.session_state.messages.append({"role": "user", "content": prompt})
                    response = LLM.invoke(full_prompt)
                    
                    if response:
                        st.markdown("#### Suggerimenti di miglioramento:")
                        st.markdown(response.content)
                        st.session_state.messages.append(
                            {"role": "assistant", "content": response.content}
                        )
            
            # Mostra la storia della chat
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

if __name__ == "__main__":
    main_chat()