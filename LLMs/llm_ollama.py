import os
from dotenv import load_dotenv

# from langchain_fireworks import ChatFireworks
from langchain_ollama import ChatOllama

# Load environment variables from .env file
load_dotenv()


LLM = ChatOllama(model="llama3.2",
                         temperature=0,
                         # format="json"
                         )
