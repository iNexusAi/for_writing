import os
from typing import Any, Dict
import logging
from datetime import datetime
from pathlib import Path
import re
from tools import write_markdown_file

def ensure_output_directory(directory: str = "output"):
    """
    Assicura che la directory di output esista.
    """
    Path(directory).mkdir(parents=True, exist_ok=True)
    return directory

def sanitize_filename(text: str) -> str:
    """Converte il testo in un nome file valido."""
    # Rimuove caratteri speciali e spazi
    text = re.sub(r'[^\w\s-]', '', text)
    # Sostituisce spazi con underscore
    text = re.sub(r'\s+', '_', text)
    # Limita la lunghezza
    return text[:50].lower()

def saving_node(state):
    """
    Salva il documento finale e il piano come file markdown.
    Include metadata e statistiche.
    """
    logging.info("---SAVING THE DOC---")
    
    try:
        # Estrazione dati dallo state
        initial_prompt = state.get('initial_prompt', '')
        plan = state.get('plan', '')
        final_doc = state.get('final_doc', '')
        word_count = state.get('word_count', 0)
        llm_name = state.get('llm_name', 'default')
        num_steps = int(state.get('num_steps', 0))
        
        # Estrai il topic dal prompt iniziale
        topic = initial_prompt.split("su: ")[-1].split("\n")[0] if "su: " in initial_prompt else "topic"
        topic_filename = sanitize_filename(topic)
        
        # Creazione timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Assicura che la directory output esista
        output_dir = ensure_output_directory()
        
        # Aggiunge metadata al documento finale
        final_doc_with_metadata = f"""
# {topic}
Data: {timestamp}
Modello: {llm_name}
Conteggio parole: {word_count}

## Prompt Iniziale
{initial_prompt}

## Contenuto
{final_doc}

## Statistiche
- Parole totali: {word_count}
- Passi di generazione: {num_steps}
"""

        # Aggiunge metadata al piano
        plan_with_metadata = f"""
# Piano dell'Articolo: {topic}
Data: {timestamp}
Modello: {llm_name}

## Piano
{plan}
"""

        # Definizione nomi file con topic
        doc_filename = f"article_{topic_filename}"
        plan_filename = f"plan_{topic_filename}"
        
        # Salvataggio files
        logging.info(f"Salvando il documento in {doc_filename}.md")
        write_markdown_file(final_doc_with_metadata, os.path.join(output_dir, doc_filename))
        
        logging.info(f"Salvando il piano in {plan_filename}.md")
        write_markdown_file(plan_with_metadata, os.path.join(output_dir, plan_filename))
        
        logging.info(f"Salvataggio completato con successo per topic: {topic}")
        
        return {
            "num_steps": num_steps + 1,
            "output_files": {
                "doc": f"{doc_filename}.md",
                "plan": f"{plan_filename}.md"
            },
            "topic": topic
        }
        
    except Exception as e:
        logging.error(f"Errore durante il salvataggio: {str(e)}")
        raise