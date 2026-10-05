import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")


def get_llm():

    return ChatGroq(groq_api_key=groq_api_key, model_name="openai/gpt-oss-20b")


# response = llm.invoke("Hello, who are you?")
# print(response.content)
