import os
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic

# Load environment variables from .env file
load_dotenv()

# Initialize Claude model
LLM = ChatAnthropic(
    model="claude-3-sonnet-20240229",
    anthropic_api_key=os.getenv('ANTHROPIC_API_KEY'),
    temperature=0,
    max_tokens=4096
)
