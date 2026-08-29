import os
from langchain.llms import Groq
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# Load Groq LLM (replace YOUR_API_KEY with actual key in .env)
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
llm = Groq(temperature=0, model_name="llama3-8b-8192", groq_api_key=api_key)

# Prompt to classify ticket type
classifier_prompt = PromptTemplate(
    input_variables=["ticket"],
    template="""Classify the following IT support request into one of these categories: vpn, email, printer, software, hardware, other. Return only the category.
Ticket: {ticket}""",
)

manager_chain = LLMChain(llm=llm, prompt=classifier_prompt)


def classify_ticket(ticket_text: str) -> str:
    """Return the classified category for a ticket."""
    return manager_chain.run({"ticket": ticket_text}).strip().lower()

if __name__ == "__main__":
    sample = "VPN is not connecting"
    print("Category:", classify_ticket(sample))
