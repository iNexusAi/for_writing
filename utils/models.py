from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_community.llms import Ollama
from langchain_community.llms import HuggingFaceHub
from langchain_core.language_models import BaseLLM
from typing import Optional, Literal, Dict
import os
from dotenv import load_dotenv
from enum import Enum

class OllamaModels(Enum):
    """Enum per i modelli Ollama supportati"""
    MISTRAL = "mistral"
    GEMMA = "gemma2"
    LLAMA = "llama3.2"

class HFModels(Enum):
    """Enum per i modelli HuggingFace supportati"""
    LLAMA = "meta-llama/Llama-3.2-1B"

class LLMFactory:
    """Factory class per gestire diversi modelli LLM"""
    
    USECASE_CONFIGS: Dict[str, Dict] = {
        'article_writing': {
            'provider': 'ollama',
            'model': OllamaModels.MISTRAL.value,
            'temperature': 0.7
        },
        'general': {
            'provider': 'claude',
            'model': "claude-3-sonnet-20240229",
            'temperature': 0.7
        },
        'llama_hf': {
            'provider': 'huggingface',
            'model': HFModels.LLAMA.value,
            'temperature': 0.7
        }
    }
    
    def __init__(self):
        load_dotenv()
        self._validate_env()
        
    def _validate_env(self):
        """Valida le variabili d'ambiente necessarie"""
        required_vars = {
            'ANTHROPIC_API_KEY': 'Claude',
            'OPENAI_API_KEY': 'OpenAI',
            'OLLAMA_API_BASE': 'Ollama',
            'HUGGINGFACEHUB_API_TOKEN': 'HuggingFace'
        }
        
        for var, service in required_vars.items():
            if not os.getenv(var) and var != 'OLLAMA_API_BASE':
                print(f"⚠️ Warning: {var} non trovata. {service} non sarà disponibile.")

    def get_llm(self, 
                provider: Literal['claude', 'openai', 'ollama', 'huggingface'] = 'claude',
                model: Optional[str] = None,
                temperature: float = 0.1) -> BaseLLM:
        """
        Restituisce l'istanza LLM richiesta
        """
        if provider == 'claude':
            return self._get_claude(model, temperature)
        elif provider == 'openai':
            return self._get_openai(model, temperature)
        elif provider == 'ollama':
            return self._get_ollama(model, temperature)
        elif provider == 'huggingface':
            return self._get_huggingface(model, temperature)
        else:
            raise ValueError(f"Provider {provider} non supportato")

    def _get_claude(self, model: Optional[str], temperature: float) -> ChatAnthropic:
        """Configura e restituisce un'istanza Claude"""
        if not os.getenv('ANTHROPIC_API_KEY'):
            raise ValueError("ANTHROPIC_API_KEY non trovata nelle variabili d'ambiente")
            
        return ChatAnthropic(
            model=model or "claude-3-sonnet-20240229",
            temperature=temperature,
            anthropic_api_key=os.getenv('ANTHROPIC_API_KEY')
        )

    def _get_openai(self, model: Optional[str], temperature: float) -> ChatOpenAI:
        """Configura e restituisce un'istanza OpenAI"""
        if not os.getenv('OPENAI_API_KEY'):
            raise ValueError("OPENAI_API_KEY non trovata nelle variabili d'ambiente")
            
        return ChatOpenAI(
            model=model or "gpt-3.5-turbo",
            temperature=temperature,
            api_key=os.getenv('OPENAI_API_KEY')
        )

    def _get_ollama(self, model: Optional[str], temperature: float) -> Ollama:
        """Configura e restituisce un'istanza Ollama"""
        base_url = os.getenv('OLLAMA_API_BASE', 'http://localhost:11434')
        
        # Valida che il modello sia uno di quelli supportati
        if model and model not in [m.value for m in OllamaModels]:
            raise ValueError(f"Modello Ollama non supportato. Usa uno tra: {', '.join([m.value for m in OllamaModels])}")
        
        return Ollama(
            base_url=base_url,
            model=model or OllamaModels.MISTRAL.value,
            temperature=temperature
        )

    def _get_huggingface(self, model: Optional[str], temperature: float) -> HuggingFaceHub:
        """Configura e restituisce un'istanza HuggingFaceHub"""
        if not os.getenv('HUGGINGFACEHUB_API_TOKEN'):
            raise ValueError("HUGGINGFACEHUB_API_TOKEN non trovata nelle variabili d'ambiente")
        
        # Valida che il modello sia uno di quelli supportati
        if model and model not in [m.value for m in HFModels]:
            raise ValueError(f"Modello HuggingFace non supportato. Usa uno tra: {', '.join([m.value for m in HFModels])}")
        
        return HuggingFaceHub(
            repo_id=model or HFModels.LLAMA.value,
            huggingfacehub_api_token=os.getenv('HUGGINGFACEHUB_API_TOKEN'),
            model_kwargs={
                "temperature": temperature,
                "max_length": 2048,
                "top_p": 0.95
            }
        )