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

import time

def temperature_prompt_activity():
    print("=" * 80)
    print("ADVANCED PROMPT ENGINEERING: TEMPERATURE & INSTRUCTION-BASED PROMPTS")
    print("=" * 80)

    print("\n" + "-" * 40)
    print("PART 1: TEMPERATURE EXPLORATION")
    print("-" * 40)
    base_prompt = input("Enter a creative prompt (e.g., 'Write a short story about a robot learning to paint'): ").strip()

    print("\nGenerating responses with different temperature settings...")

    print("\n--- LOW TEMPERATURE (0.1) ---")
    print(generate_response(base_prompt, temperature=0.1, max_tokens=512))
    time.sleep(1)

    print("\n--- MEDIUM TEMPERATURE (0.5) ---")
    print(generate_response(base_prompt, temperature=0.5, max_tokens=512))
    time.sleep(1)

    print("\n--- HIGH TEMPERATURE (0.9) ---")
    print(generate_response(base_prompt, temperature=0.9, max_tokens=512))
    time.sleep(1)

    print("\n" + "-" * 40)
    print("PART 2: INSTRUCTION-BASED PROMPTS")
    print("-" * 40)
    topic = input("Choose a topic (e.g., 'climate change', 'space exploration'): ").strip()

    instructions = [
        f"Summarize the key facts about {topic} in 3-4 sentences.",
        f"Explain {topic} as if I'm a 10-year-old child.",
        f"Write a pro/con list about {topic}.",
        f"Create a fictional news headline from the year 2050 about {topic}.",
    ]

    for i, instruction in enumerate(instructions, 1):
        print(f"\n--- INSTRUCTION {i}: {instruction} ---")
        print(generate_response(instruction, temperature=0.7, max_tokens=512))
        time.sleep(1)

    print("\n" + "-" * 40)
    print("PART 3: CREATE YOUR OWN PROMPT")
    print("-" * 40)
    custom_instruction = input("Enter your instruction-based prompt: ").strip()

    try:
        custom_temp = float(input("Set a temperature (0.1 to 1.0): ").strip())
        if not (0.1 <= custom_temp <= 1.0):
            print("Invalid temperature. Using default 0.7.")
            custom_temp = 0.7
    except ValueError:
        print("Invalid input. Using default temperature 0.7.")
        custom_temp = 0.7

    print(f"\n--- YOUR CUSTOM PROMPT WITH TEMPERATURE {custom_temp} ---")
    print(generate_response(custom_instruction, temperature=custom_temp, max_tokens=512))

    print("\n" + "-" * 40)
    print("REFLECTION QUESTIONS")
    print("-" * 40)
    print("1. How did changing the temperature affect the creativity and variety?")
    print("2. Which instruction-based prompt produced the most useful or creative result?")
    print("3. How would you use temperature + instructions for a real-world task?")
    print("4. What surprised you about the AI’s behavior with these changes?")

if __name__ == "__main__":
    temperature_prompt_activity()
