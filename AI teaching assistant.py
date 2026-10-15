# groq.py  (pip install openai)
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
# main.py (Streamlit) — Role-based Teaching Assistant (Groq/HF switch by import)
# Switch provider by changing ONE line:
from hf import generate_response
# from groq import generate_response

import streamlit as st
import io

def role_prompt(role: str, q: str) -> str:
    if role == "Teacher":
        return f"You are a teacher. Explain clearly with simple words and 3-5 bullet points.\nQuestion: {q}"
    if role == "Expert":
        return f"You are an expert. Give a detailed, technical explanation with examples.\nQuestion: {q}"
    return f"You are a friendly helper. Answer warmly and simply with a short example.\nQuestion: {q}"

def setup_ui():
    st.title("Enhanced AI Teaching Assistant")
    st.write("Ask questions and get AI responses tailored by role. Your conversation history is saved below!")

    st.session_state.setdefault("conversation", [])

    role = st.selectbox("Select AI Role", ["Teacher", "Expert", "Friendly Helper"])
    user_input = st.text_input("Enter your question here:", placeholder="Example: What is photosynthesis?")

    c1, c2 = st.columns([1, 1])
    with c1:
        ask = st.button("Ask")
    with c2:
        clear = st.button("Clear Conversation")

    if ask:
        if user_input.strip():
            prompt = role_prompt(role, user_input.strip())
            with st.spinner("Generating response..."):
                answer = generate_response(prompt, temperature=0.3, max_tokens=1024)
            st.session_state.conversation.append({"role": role, "question": user_input.strip(), "answer": answer})
            st.rerun()
        else:
            st.warning("⚠️ Please enter a question before clicking Ask.")

    if clear:
        st.session_state.conversation = []
        st.rerun()

    if st.session_state.conversation:
        # Export
        export_text = ""
        for i, chat in enumerate(st.session_state.conversation, 1):
            export_text += f"Q{i} ({chat['role']}): {chat['question']}\nA{i}: {chat['answer']}\n\n"
        st.download_button(
            "📄 Export Chat History",
            io.BytesIO(export_text.encode("utf-8")),
            "Enhanced_AI_Teaching_Assistant_Conversation.txt",
            "text/plain",
        )

        st.markdown("### Conversation History")
        for i, chat in enumerate(st.session_state.conversation, 1):
            st.markdown(f"**You:** {chat['question']}")
            st.markdown(f"**AI ({chat['role']}):** {chat['answer']}")
            st.markdown("---")

def main():
    setup_ui()

if __name__ == "__main__":
    main()
