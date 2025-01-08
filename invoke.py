# invoke.py
from graph import create_workflow
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def generate_instructions(llm, topic):
    """
    Generate customized instructions based on the chosen topic
    using the existing workflow graph
    """
    logging.info(f"Initializing generation for topic: {topic}")
    
    # Create the workflow
    logging.info("Creating workflow")
    app = create_workflow(llm)
    
    # Prepare the initial prompt based on the topic
    initial_prompt = f"""Please create a detailed article plan about: {topic}

The article should be comprehensive, well-structured, and written in Italian. 
Consider the target audience and provide valuable insights on the topic."""

    logging.info("Initial prompt created")
    
    # Get the actual LLM model name
    llm_name = getattr(llm, 'model_name', 'default_model')
    
    # Prepare inputs according to GraphState requirements
    inputs = {
        "initial_prompt": initial_prompt,
        "plan": "",
        "num_steps": 0,
        "final_doc": "",
        "write_steps": [],
        "word_count": 0,
        "llm_name": llm_name
    }
    logging.info(f"Input prepared for workflow with model: {llm_name}")
    
    try:
        # Execute the workflow
        logging.info("Starting workflow execution")
        output = app.invoke(inputs)
        logging.info("Workflow completed successfully")
        
        # Validate the output
        if not output:
            logging.error("No output received from workflow")
            raise ValueError("Workflow produced no output")
            
        logging.info(f"Output keys available: {output.keys()}")
        
        # Validate the plan
        if not output.get('plan'):
            logging.error("No plan was generated")
            raise ValueError("No plan was generated")
            
        # Log output details
        logging.info(f"Generated plan length: {len(output.get('plan', ''))}")
        logging.info(f"Generated final document length: {len(output.get('final_doc', ''))}")
        logging.info(f"Word count: {output.get('word_count', 0)}")
        
        return output
        
    except Exception as e:
        logging.error(f"Error during workflow execution: {str(e)}")
        raise