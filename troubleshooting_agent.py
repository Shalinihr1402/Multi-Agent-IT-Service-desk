import os
from langchain.llms import Groq
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
llm = Groq(temperature=0, model_name="llama3-8b-8192", groq_api_key=api_key)

# Prompt for troubleshooting based on category and issue description
troubleshoot_prompt = PromptTemplate(
    input_variables=["category", "issue", "knowledge"],
    template="""You are a technical support assistant. The ticket is about {category}. Issue description: {issue}. Use the following knowledge snippets (if any) to propose a concise, step‑by‑step troubleshooting guide. Return the steps as a numbered list.
Knowledge snippets: {knowledge}""",
)

troubleshoot_chain = LLMChain(llm=llm, prompt=troubleshoot_prompt)


def troubleshoot(category: str, issue: str, knowledge_snippets: str, employee_info: dict, device_info: dict) -> str:
    """Generate troubleshooting steps for a given ticket category.
    knowledge_snippets may be empty string if no relevant article.
    """
    # Combine context (employee/device) optionally in prompt later; for simplicity we ignore here.
    return troubleshoot_chain.run({"category": category, "issue": issue, "knowledge": knowledge_snippets})
