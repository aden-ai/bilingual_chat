import streamlit as st
import time
import re
from langdetect import detect
from deep_translator import GoogleTranslator
from retriever import Retriever
from prompt_templates import make_prompt
from api_client import call_ollama


def strip_think(text: str) -> str:
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()


st.set_page_config(page_title="Gov Schemes Chatbot", layout="wide")
st.title("Bilingual Chatbot (English / Marathi)")


def is_probably_marathi(text):
    return bool(re.search(r'[\u0900-\u097F]', text))


def translate_text(text, source, target):
    try:
        return GoogleTranslator(source=source, target=target).translate(text)
    except:
        return text


def llm_detect_language(text):
    try:
        lang = detect(text)
    except:
        lang = "en"
    if is_probably_marathi(text):
        return "mr"
    return lang


def detect_and_translate_to_en(user_text):
    lang = llm_detect_language(user_text)
    if lang == "mr":
        translated = translate_text(user_text, "mr", "en")
        return translated, "mr"
    return user_text, "en"


def translate_back_to_mr(answer_text, user_lang):
    if user_lang == "mr":
        return translate_text(answer_text, "en", "mr")
    return answer_text


@st.cache_resource
def get_retriever():
    return Retriever(csv_path="data/updated_data.csv")


retriever = get_retriever()

if "history" not in st.session_state:
    st.session_state.history = []

query = st.text_input("Ask your question (English or Marathi)")

if st.button("Send") and query.strip():
    user_q = query.strip()
    en_query, user_lang = detect_and_translate_to_en(user_q)

    if len(en_query.split()) <= 1:
        bot_reply = (
            "तुमचा प्रश्न अपूर्ण आहे. कृपया अधिक माहिती द्या."
            if user_lang == "mr"
            else "Your question is incomplete. Please provide more details."
        )
        st.session_state.history.append(("user", user_q))
        st.session_state.history.append(("bot", bot_reply))

    else:
        with st.spinner("Fetching relevant schemes..."):
            results = retriever.search(en_query, top_k=2)

        if not results:
            bot_reply = (
                "क्षमस्व, कोणतीही योजना सापडली नाही."
                if user_lang == "mr"
                else "Sorry, no relevant schemes found."
            )
            st.session_state.history.append(("user", user_q))
            st.session_state.history.append(("bot", bot_reply))

        else:
            texts = [r["text"][:350] for r in results]
            final_results = [{"text": t, "score": r["score"]} for t, r in zip(texts, results)]

            prompt = make_prompt(user_q, "en", final_results)
            print("Final RAG prompt length:", len(prompt))

            with st.spinner("Generating answer..."):
                try:
                    start = time.time()
                    answer_en = call_ollama(prompt)
                    answer_en = strip_think(answer_en)
                    end = time.time()
                    print("Ollama response:", round(end - start, 2), "seconds")
                    print("Preview:", answer_en[:200])
                except Exception:
                    answer_en = "Sorry, the LLM failed to respond."

            final_answer = translate_back_to_mr(answer_en, user_lang)
            st.session_state.history.append(("user", user_q))
            st.session_state.history.append(("bot", final_answer))


for role, text in st.session_state.history:
    if role == "user":
        st.markdown(f"**You:** {text}")
    else:
        st.markdown(f"**Bot:** {text}")
