from langchain.schema import Document
from chains.plan_chain import plan_chain
import logging

def validate_plan(plan: str) -> bool:
    """
    Valida che il piano generato rispetti il formato richiesto.
    """
    try:
        # Verifica che non ci siano bullet points
        if '*' in plan:
            logging.warning("Piano contiene bullet points non permessi")
            return False
            
        # Verifica che ogni paragrafo sia nel formato corretto
        paragraphs = plan.strip().split('\n')
        for p in paragraphs:
            if not p.strip():
                continue
            if not (p.startswith('Paragraph') and 
                   'Main Point:' in p and 
                   'Word Count:' in p and 
                   p.split('Word Count:')[1].strip().isdigit()):
                logging.warning(f"Formato paragrafo non valido: {p}")
                return False
        return True
    except Exception as e:
        logging.warning(f"Errore durante la validazione del piano: {str(e)}")
        return False

def planning_node(state):
    """
    Node for article plan generation.
    Takes the initial prompt and generates a structured plan.
    """
    logging.info("---PLANNING THE WRITING---")
    
    # Input extraction
    initial_prompt = state.get('initial_prompt')
    if not initial_prompt:
        logging.error("Missing initial prompt")
        raise ValueError("Initial prompt is required")
        
    num_steps = int(state.get('num_steps', 0))
    logging.info(f"Starting planning step {num_steps + 1}")
    
    try:
        # Plan generation with explicit format instructions
        formatted_prompt = f"""
        Create a plan for an article about: {initial_prompt}

        RESPOND ONLY WITH THE EXACT FORMAT BELOW, NO INTRODUCTION OR ADDITIONAL TEXT:

        Paragraph 1 - Main Point: [descrizione in italiano] - Word Count: 400
        Paragraph 2 - Main Point: [descrizione in italiano] - Word Count: 500
        Paragraph 3 - Main Point: [descrizione in italiano] - Word Count: 600
        ... Other Paragraph
        
        RULES:
        1. Start directly with "Paragraph 1"
        2. NO introduction text
        3. NO bullet points
        4. NO word count ranges
        5. Content in Italian
        6. Each paragraph on one line
        """
        
        logging.info(f"Generating plan with formatted prompt")
        plan = plan_chain.invoke({"instructions": formatted_prompt})
        
        # Plan validation with detailed logging
        if not validate_plan(plan):
            logging.warning("Retrying with explicit format...")
            plan = plan_chain.invoke({"instructions": formatted_prompt})
            if not validate_plan(plan):
                logging.error("Plan invalid after second attempt")
                raise ValueError("Generated plan is not in the correct format")
        
        # Log the generated plan
        logging.info("Plan generated successfully")
        logging.info(f"Number of paragraphs: {len(plan.strip().split('Paragraph')) - 1}")
        
        return {
            "plan": plan,
            "num_steps": num_steps + 1
        }
        
    except Exception as e:
        logging.error(f"Error during plan generation: {str(e)}")
        raise