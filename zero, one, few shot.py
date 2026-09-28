import config
from openai import OpenAI

GROQ_URL = "https://api.groq.com/openai/v1"
MODELS = getattr(config, "GROQ_MODELS", ["llama-3.1-8b-instant", "mixtral-8x7b-32768"])

def generate_response(prompt: str, temperature: float = 0.3, max_tokens: int = 512) -> str:
    key = getattr(config, "GROQ_API_KEY", None)
    if not key:
        return "Error: GROQ_API_KEY missing in config.py"
    c = OpenAI(api_key=key, base_url=GROQ_URL)

    last_err = None
    for m in MODELS:
        try:
            r = c.chat.completions.create(
                model=m,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return r.choices[0].message.content
        except Exception as e:
            last_err = e

    return (
        "Groq model failed.\n"
        f"Tried models: {MODELS}\n"
        "Fix:\n"
        "1) Switch to hf by importing hf.py in main.py OR\n"
        "2) Replace Groq model in groq.py (GROQ_MODELS).\n"
        f"Details: {type(last_err).__name__}: {last_err}"
    )

import config
from huggingface_hub import InferenceClient

MODELS = getattr(
    config,
    "HF_MODELS",
    ["meta-llama/Llama-3.1-8B-Instruct"],
)

def generate_response(prompt: str, temperature: float = 0.3, max_tokens: int = 512) -> str:
    key = getattr(config, "HF_API_KEY", None)
    if not key:
        return "Error: HF_API_KEY missing in config.py"

    last_err = None
    for m in MODELS:
        try:
            c = InferenceClient(model=m, token=key)
            r = c.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return r.choices[0].message.content
        except Exception as e:
            last_err = e

    return (
        "Hugging Face model failed.\n"
        f"Tried models: {MODELS}\n"
        "Fix:\n"
        "1) Switch to Groq by importing groq.py in main.py OR\n"
        "2) Replace HF model in hf.py (HF_MODELS).\n"
        f"Details: {type(last_err).__name__}: {last_err}"
    )

# main.py
# Change groq --> hf to use Hugging Face API
# Change hf --> groq to use Groq API
from groq import generate_response
# from hf import generate_response

def run_activity():
    category = input("Enter a category (e.g., fruit, city, animal): ").strip()
    item = input(f"Enter a specific {category}: ").strip()

    print("\n--- ZERO-SHOT ---")
    zero_prompt = f"Is {item} a {category}? Answer yes or no."
    print(f"Prompt: {zero_prompt}")
    print("Response:", generate_response(zero_prompt, temperature=0.3, max_tokens=1024))

    print("\n--- ONE-SHOT ---")
    one_prompt = f"""Determine if the item belongs to the category.

Example:
Category: fruit
Item: apple
Answer: Yes, apple is a fruit.

Now you try:
Category: {category}
Item: {item}
Answer:"""
    print("Response:", generate_response(one_prompt, temperature=0.3, max_tokens=1024))

    print("\n--- FEW-SHOT ---")
    few_prompt = f"""Determine if the item belongs to the category.

Example 1:
Category: fruit
Item: apple
Answer: Yes, apple is a fruit.

Example 2:
Category: fruit
Item: carrot
Answer: No, carrot is not a fruit. It's a vegetable.

Example 3:
Category: vehicle
Item: bicycle
Answer: Yes, bicycle is a vehicle.

Now you try:
Category: {category}
Item: {item}
Answer:"""
    print("Response:", generate_response(few_prompt, temperature=0.3, max_tokens=1024))

    print("\n--- CREATIVE FEW-SHOT ---")
    creative_prompt = f"""Write a one-sentence story about the given word.

Example 1:
Word: moon
Story: The moon winked at the lovers as they shared their first kiss.

Example 2:
Word: computer
Story: The computer sighed as another cup of coffee was spilled on its keyboard.

Word: {item}
Story:"""
    print("Response:", generate_response(creative_prompt, temperature=0.7, max_tokens=1024))

    print("\n--- REFLECTION QUESTIONS ---")
    print("1. How did the responses differ between each approach?")
    print("2. Which approach gave the most helpful or creative response?")
    print("3. How did examples in few-shot prompts guide the output?")
    print("4. How could you apply these techniques to your own tasks?")

if __name__ == "__main__":
    run_activity()
