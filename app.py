import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

from llama_index.core import VectorStoreIndex
from llama_index.core import SimpleDirectoryReader
from llama_index.core import Settings

from llama_index.llms.google_genai import GoogleGenAI

document = SimpleDirectoryReader("./Data").load_data()
print(f"Loaded {len(document)} Document")