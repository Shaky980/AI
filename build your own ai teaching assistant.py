import os
from dotenv import load_dotenv

load_dotenv()

HF_API_KEY = os.getenv("HF_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
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
# main.py (Streamlit)
# Switch provider by changing the import line:
from hf import generate_response
# from groq import generate_response

import streamlit as st
import io


def setup_ui():
    st.set_page_config(page_title="AI Teaching Assistant", layout="centered")
    st.title("🤖 AI Teaching Assistant")
    st.write("Ask me anything about various subjects, and I'll provide an insightful answer.")

    if "history" not in st.session_state:
        st.session_state.history = []

    col_clear, col_export = st.columns([1, 2])

    with col_clear:
        if st.button("🧹 Clear Conversation"):
            st.session_state.history = []
            st.experimental_rerun()

    with col_export:
        if st.session_state.history:
            export_text = ""
            for idx, qa in enumerate(st.session_state.history, start=1):
                export_text += f"Q{idx}: {qa['question']}\nA{idx}: {qa['answer']}\n\n"

            bio = io.BytesIO()
            bio.write(export_text.encode("utf-8"))
            bio.seek(0)

            st.download_button(
                label="📥 Export Chat History",
                data=bio,
                file_name="AI_Teaching_Assistant_Conversation.txt",
                mime="text/plain",
            )

    user_input = st.text_input("Enter your question here:")

    if st.button("Ask"):
        if user_input.strip():
            with st.spinner("Generating AI response..."):
                
                response = generate_response(user_input.strip(), temperature=0.3)
            st.session_state.history.append(
                {"question": user_input.strip(), "answer": response}
            )
        else:
            st.warning("⚠️ Please enter a question before clicking Ask.")

    st.markdown("### Conversation History")
    st.markdown(
        """
        <style>
        .history-box {
            max-height: 400px;
            overflow-y: auto;
            border: 1px solid #ddd;
            padding: 12px;
            background-color: #f9f9f9;
            border-radius: 6px;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .question {
            font-weight: 600;
            color: #0a6ebd;
            margin-top: 12px;
            margin-bottom: 4px;
        }
        .answer {
            margin-bottom: 16px;
            white-space: pre-wrap;
            color: #333;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    history_html = '<div class="history-box">'
    for idx, qa in enumerate(st.session_state.history, start=1):
        history_html += f'<div class="question">Q{idx}: {qa["question"]}</div>'
        history_html += f'<div class="answer">A{idx}: {qa["answer"]}</div>'
    history_html += "</div>"

    st.markdown(history_html, unsafe_allow_html=True)


def main():
    setup_ui()


if __name__ == "__main__":
    main()
