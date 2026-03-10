# ollama.py
import ollama

def ask_ollama(prompt: str, model: str = "llama2") -> str:
    """
    Send a prompt to Ollama and return the response text.
    """
    response = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    return response["message"]["content"]

def ask_with_context(context: str, question: str, model: str = "llama2") -> str:
    """
    Provide context + question to Ollama for better answers.
    """
    response = ollama.chat(
        model=model,
        messages=[
            {"role": "system", "content": context},
            {"role": "user", "content": question}
        ]
    )
    return response["message"]["content"]

def generate_ideas(topic: str, model: str = "llama2") -> str:
    """
    Ask Ollama to generate creative ideas for a given topic.
    """
    prompt = f"Give me 3 creative project ideas about {topic}."
    return ask_ollama(prompt, model=model)