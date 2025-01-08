from langchain.schema import Document
from chains.write_chain import write_chain
import logging

def count_words(text: str) -> int:
    """
    Conta il numero di parole nel testo.
    
    Args:
        text (str): Il testo da analizzare
    
    Returns:
        int: Numero di parole
    """
    return len(text.split())

def extract_word_target(step: str) -> int:
    """
    Estrae il target di parole dal piano.
    
    Args:
        step (str): Riga del piano con il conteggio parole
    
    Returns:
        int: Numero target di parole o 0 se non trovato
    """
    try:
        if 'Word Count:' in step:
            count_part = step.split('Word Count:')[1]
            # Estrae il primo numero trovato
            import re
            numbers = re.findall(r'\d+', count_part)
            if numbers:
                return int(numbers[0])
    except Exception:
        pass
    return 0

def writing_node(state):
    """
    Nodo per la scrittura del documento basato sul piano.
    Scrive ogni sezione seguendo il piano e monitora il conteggio parole.
    """
    logging.info("---WRITING THE DOC---")
    
    # Estrazione e validazione input
    initial_instruction = state.get('initial_prompt')
    plan = state.get('plan', '').strip()
    num_steps = int(state.get('num_steps', 0))
    
    if not plan or not initial_instruction:
        logging.error("Piano o istruzioni mancanti")
        raise ValueError("Piano e istruzioni sono richiesti")
    
    # Preparazione del piano
    plan = plan.replace('\n\n', '\n')
    planning_steps = [step for step in plan.split('\n') if step.strip()]
    
    if len(planning_steps) > 50:
        logging.error("Piano troppo lungo - più di 50 step")
        raise ValueError("Piano troppo lungo")
        
    logging.info(f"Inizio scrittura di {len(planning_steps)} sezioni")
    
    text = ""
    responses = []
    total_target_words = 0
    target_words_per_section = 500  # Target fisso di 500 parole per sezione
    
    # Scrittura sezione per sezione
    for idx, step in enumerate(planning_steps, 1):
        try:
            logging.info(f"Scrittura sezione {idx}/{len(planning_steps)}")
            logging.info(f"Target parole per questa sezione: {target_words_per_section}")
            
            # Invoca la chain di scrittura con le variabili corrette
            result = write_chain.invoke({
                "instructions": initial_instruction,
                "plan": step,
                "text": text,
                "STEP": f"Paragraph {idx}",
                "target_words": target_words_per_section  # Aggiungiamo il target fisso
            })
            
            section_words = count_words(result)
            logging.info(f"Sezione {idx} completata: {section_words} parole scritte")
            
            responses.append(result)
            text += result + '\n\n'
            total_target_words += target_words_per_section
            
        except Exception as e:
            logging.error(f"Errore durante la scrittura della sezione {idx}: {str(e)}")
            raise
    
    # Assemblaggio documento finale
    final_doc = '\n\n'.join(responses)
    word_count = count_words(final_doc)
    
    logging.info(f"Documento completato:")
    logging.info(f"- Parole totali: {word_count}")
    logging.info(f"- Target parole: {total_target_words}")
    logging.info(f"- Sezioni completate: {len(responses)}/{len(planning_steps)}")
    
    return {
        "final_doc": final_doc,
        "word_count": word_count,
        "target_word_count": total_target_words,
        "sections_completed": len(responses),
        "total_sections": len(planning_steps),
        "num_steps": num_steps + 1
    }