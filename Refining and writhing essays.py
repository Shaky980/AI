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

# main.py
# Change groq --> hf to use Hugging Face API
# Change hf --> groq to use Groq API
from groq import generate_response
# from hf import generate_response

def get_essay_details():
    print("\n=== AI Writing Assistant ===\n")

    topic = input("What is the topic of your essay? ").strip()
    essay_type = input(
        "What type of essay are you writing? (Argumentative/Expository/Descriptive/Persuasive/Analytical): "
    ).strip()

    print("\nSelect the desired essay word count:")
    print("1) 300 words\n2) 900 words\n3) 1200 words\n4) 2000 words")
    wc = input("Enter choice (1-4): ").strip()
    length_map = {"1": "300", "2": "900", "3": "1200", "4": "2000"}
    length = length_map.get(wc, "300")

    target_audience = input("Who is the target audience? (e.g., High school students): ").strip()
    specific_points = input("Any specific points that must be included? ").strip()
    stance = input("What is your stance? (For/Against/Neutral): ").strip()
    references = input("Any sources/quotes/references to include? ").strip()
    writing_style = input("Preferred writing style? (Formal/Conversational/Academic/Creative): ").strip()
    outline_needed = input("Would you like an outline first? (Yes/No): ").strip().lower()

    return {
        "topic": topic,
        "essay_type": essay_type,
        "length": length,
        "target_audience": target_audience,
        "specific_points": specific_points,
        "stance": stance,
        "references": references,
        "writing_style": writing_style,
        "outline_needed": outline_needed,
    }

def generate_essay_content(d):
    try:
        temp = float(input("Enter temperature (0.2 structured, 0.7 creative): ").strip())
        if not (0.0 <= temp <= 1.0): raise ValueError
    except ValueError:
        print("Invalid temperature. Using 0.3.")
        temp = 0.3

    # Optional outline
    if d["outline_needed"] in ("yes", "y"):
        outline_p = (
            f"Create a clear outline for a {d['essay_type']} essay on '{d['topic']}' "
            f"({d['length']} words). Stance: {d['stance']}. "
            f"Audience: {d['target_audience']}. Style: {d['writing_style']}. "
            f"Must include: {d['specific_points']}. References: {d['references']}."
        )
        outline = generate_response(outline_p, temperature=temp, max_tokens=1024)
        print("\n=== Suggested Outline ===\n")
        print(outline)

    intro_p = (
        f"Write an introduction for a {d['essay_type']} essay on '{d['topic']}' "
        f"({d['length']} words). Stance: {d['stance']}. "
        f"Audience: {d['target_audience']}. Style: {d['writing_style']}. "
        f"Must include: {d['specific_points']}. References: {d['references']}."
    )
    intro = generate_response(intro_p, temperature=temp, max_tokens=1024)
    print("\n=== Generated Introduction ===\n")
    print(intro)

    print("\nWould you like the body step-by-step or a full draft?")
    print("1) Step-by-step\n2) Full draft")
    body_choice = input("> ").strip()

    if body_choice == "2":
        body_p = (
            f"Write the full body of a {d['essay_type']} essay on '{d['topic']}' "
            f"({d['length']} words). Stance: {d['stance']}. "
            f"Audience: {d['target_audience']}. Style: {d['writing_style']}. "
            f"Include these points: {d['specific_points']}. "
            f"Use/mention references if provided: {d['references']}."
        )
        body = generate_response(body_p, temperature=temp, max_tokens=1024)
        print("\n=== Generated Full Body ===\n")
        print(body)
    else:
        step_p = (
            f"Write step-by-step arguments for a {d['essay_type']} essay on '{d['topic']}'. "
            f"Stance: {d['stance']}. Audience: {d['target_audience']}. Style: {d['writing_style']}. "
            f"Include: {d['specific_points']}. Provide evidence and reasoning for each step."
        )
        body_step = generate_response(step_p, temperature=temp, max_tokens=1024)
        print("\n=== Generated Step-by-Step Body ===\n")
        print(body_step)

    concl_p = (
        f"Write a conclusion for a {d['essay_type']} essay on '{d['topic']}'. "
        f"Stance: {d['stance']}. Audience: {d['target_audience']}. Style: {d['writing_style']}."
    )
    concl = generate_response(concl_p, temperature=temp, max_tokens=1024)
    print("\n=== Generated Conclusion ===\n")
    print(concl)

def feedback_and_refinement():
    rating = input("\nHow satisfied are you? (1-5): ").strip()
    if rating != "5":
        feedback = input("Provide feedback (tone, structure, etc.): ").strip()
        print(f"\nThank you for your feedback! We will refine based on: {feedback}")
    else:
        print("\nThank you! The essay looks good.")

def run_activity():
    print("\nWelcome to the AI Writing Assistant!")
    details = get_essay_details()
    if not details["topic"] or not details["essay_type"]:
        print("Please provide at least a topic and essay type to continue.")
        return
    generate_essay_content(details)
    feedback_and_refinement()

if __name__ == "__main__":
    run_activity()

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
