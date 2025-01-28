import streamlit as st
import os
from dotenv import load_dotenv
from invoke import generate_instructions
import logging
import time
from LLMs.llm import LLM
from datetime import datetime

def load_custom_css():
    # Carica il CSS da file esterno
    with open('static/style.css', 'r') as f:
        st.markdown(f"""
            <style>
                {f.read()}
            </style>
        """, unsafe_allow_html=True)

def main_chat():
    load_custom_css()
    initialize_session_state()
    
    # Wrapper per il contenuto principale
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    
    # Enhanced header con nuovo stile
    st.markdown("""
        <div class="title-box">
            <h1>✍️ iNexus Writer Pro</h1>
            <p>AI Powered by <a href="https://inexus.it" target="_blank">iNexus</a></p>    
            <h3>Genera contenuti ottimizzati e professionali con tecnologie AI all'avanguardia</h3>
        </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.topic:
        # Form per input e pulsante
        with st.form(key="input_form"):
            topic = st.text_input(
                "Argomento",
                placeholder="Es: Intelligenza Artificiale nel 2024",
                help="Inserisci l'argomento principale del tuo articolo",
                label_visibility="collapsed"
            )
            
            col1, col2, col3 = st.columns([1,2,1])
            with col2:
                submitted = st.form_submit_button(
                    "🚀 Inizia a Scrivere",
                    type="primary",
                    use_container_width=True
                )
                
                # Footer con anno dinamico
                st.markdown(f"""
                    <div style="text-align: center; margin-top: 2rem; color: #666; font-size: 0.9rem; font-family: 'Inter', sans-serif;">
                        All rights reserved © {datetime.now().year} - Powered by <a href="https://inexus.it" target="_blank" style="color: #1E4D92; text-decoration: none; border-bottom: 1px solid rgba(30, 77, 146, 0.3);">iNexus</a>
                    </div>
                """, unsafe_allow_html=True)

        if submitted:
            if topic:
                st.session_state.topic = topic
                
                # Create containers for progress tracking
                progress_container = st.empty()
                status_container = st.empty()
                log_container = st.empty()
                
                with st.spinner(""):
                    progress_bar = progress_container.progress(0)
                    streamlit_handler = StreamlitHandler(progress_bar, status_container)
                    logging.getLogger().addHandler(streamlit_handler)
                    
                    try:
                        result = generate_instructions(LLM, topic)
                        if result.get('plan'):
                            st.session_state.plan = result['plan']
                            if result.get('final_doc'):
                                st.session_state.article = result['final_doc']
                                st.session_state.writing_complete = True
                                st.balloons()
                    except Exception as e:
                        st.error(f"Si è verificato un errore: {str(e)}")
                    finally:
                        logging.getLogger().removeHandler(streamlit_handler)
                
                st.rerun()
            else:
                st.warning("⚠️ Per favore, inserisci un argomento per continuare")
    else:
        # Enhanced sidebar
        with st.sidebar:
            # Project sections - solo tab Articolo con stile migliorato
            tabs = st.tabs(["📄 Articolo"])
            

            with tabs[0]:
                if st.session_state.article:
                    # Stili per l'articolo
                    st.markdown("""
                        <style>
                        .article-container {
                            background: white;
                            padding: 2rem;
                            border-radius: 12px;
                            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
                            margin: 1rem 0;
                        }
                        .article-header {
                            font-family: 'Inter', sans-serif;
                            color: #1E4D92;
                            font-size: 1.8rem;
                            font-weight: 700;
                            margin-bottom: 1rem;
                        }
                        .article-text {
                            font-family: 'Inter', sans-serif;
                            line-height: 1.8;
                            color: #2C3E50;
                            font-size: 1.1rem;
                        }
                        .article-text p {
                            margin-bottom: 1.5rem;
                            text-align: justify;
                        }
                        </style>
                    """, unsafe_allow_html=True)
                    
                    # Mostra solo il contenuto dell'articolo
                    formatted_article = st.session_state.article.strip()  # Rimuove spazi extra
                    
                    # Mostra l'articolo con il pulsante di copia
                    st.markdown(f"""
                        <div class="article-container">
                            <div class="article-text">
                                {formatted_article}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.info("Articolo in elaborazione...")
                        
        if st.button("🔄 Nuovo Progetto", type="primary"):
                reset_session_state()
        
        # Main content area
        if st.session_state.writing_complete:
            st.markdown("""
                <div class="glass-container fade-in">
                    <h2 class="section-header">✨ Perfeziona il tuo articolo</h2>
                </div>
            """, unsafe_allow_html=True)
            
            improvement_prompt = st.text_area(
                "Suggerisci miglioramenti",
                placeholder="Es: Vorrei approfondire la sezione su...",
                help="Descrivi come vorresti migliorare l'articolo",
                height=100
            )
            
            if st.button("💡 Suggerisci", type="primary"):
                if improvement_prompt:
                    with st.spinner("Elaboro le tue richieste..."):
                        full_prompt = get_improvement_prompt(
                            st.session_state.topic,
                            st.session_state.plan,
                            st.session_state.article,
                            improvement_prompt
                        )
                        
                        st.session_state.messages.append({
                            "role": "user",
                            "content": improvement_prompt
                        })
                        
                        response = LLM.invoke(full_prompt)
                        
                        if response:
                            st.markdown("""
                                <div class="glass-container">
                                    <h3 style="color: #1e3a8a;">💡 Suggerimenti di miglioramento:</h3>
                                    <div style="margin-top: 1rem;">
                                        {}
                                    </div>
                                </div>
                            """.format(response.content), unsafe_allow_html=True)
                            
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": response.content
                            })
            
            # Enhanced chat history
            if st.session_state.messages:
                st.markdown("""
                    <div class="glass-container">
                        <h3 class="section-header">📜 Cronologia delle revisioni</h3>
                    </div>
                """, unsafe_allow_html=True)
                
                for message in st.session_state.messages:
                    with st.chat_message(
                        message["role"],
                        avatar="👤" if message["role"] == "user" else "🤖"
                    ):
                        st.markdown(message["content"])

    # Chiudi il wrapper
    st.markdown('</div>', unsafe_allow_html=True)

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

def reset_session_state():
    st.session_state.topic = None
    st.session_state.plan = None
    st.session_state.article = None
    st.session_state.messages = []
    st.session_state.writing_complete = False
    st.rerun()

def get_improvement_prompt(topic, plan, article, improvement_request):
    return f"""Sei un editor esperto nella revisione di articoli. 
    Stai lavorando sulla revisione di un articolo sul tema: {topic}

    STRUTTURA PIANIFICATA:
    {plan}

    CONTENUTO ATTUALE:
    {article}

    RICHIESTA DI MODIFICA: 
    {improvement_request}

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

class StreamlitHandler(logging.Handler):
    def __init__(self, progress_placeholder, log_placeholder):
        super().__init__()
        self.progress_placeholder = progress_placeholder
        self.log_placeholder = log_placeholder
        self.log_text = ""
        self.current_section = ""
        self.total_sections = 0
        self.completed_sections = 0

    # Replace # 3 the problematic part in the emit method:
    def emit(self, record):
        try:
            if "HTTP Request" in record.getMessage():
                return
                
            log_entry = self.format(record)
            self.log_text = log_entry + "\n" + self.log_text
            
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

            status_html = '<div style="padding: 10px; border-radius: 5px; background-color: #f0f2f6; margin-bottom: 10px"><h3 style="color: #0066cc; margin: 0;">Status: ' + self.current_section + '</h3></div>'
            self.log_placeholder.markdown(status_html, unsafe_allow_html=True)
            
            log_html = '<div class="log-container">' + self.log_text.replace("\n", "<br>") + '</div>'
            self.log_placeholder.markdown(log_html, unsafe_allow_html=True)
            
        except Exception:
            self.handleError(record)
# Change 4
if __name__ == "__main__":
    main_chat()