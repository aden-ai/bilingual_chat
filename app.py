import streamlit as st
import time
from langdetect import detect
from googletrans import Translator
import re

from retriever import Retriever
from prompt_templates import make_prompt
from api_client import call_ollama


st.set_page_config(page_title="Gov Schemes Chatbot", layout="wide")
st.title("Government Schemes Chatbot (English / Marathi)")

translator = Translator()

@st.cache_resource
def get_retriever():
    return Retriever(csv_path="data/updated_data.csv")

retriever = get_retriever()

if "history" not in st.session_state:
    st.session_state.history = []

# ---------------------
# Language + Translation Helpers
# ---------------------
def llm_detect_language(text):
    try:
        return detect(text)
    except:
        return "en"

def detect_and_translate_to_en(text):
    lang = llm_detect_language(text)
    if lang == "mr":
        try:
            translated = translator.translate(text, src='mr', dest='en').text
            return translated, lang
        except:
            return text, lang
    return text, lang

def translate_back_to_mr(text, user_lang):
    if user_lang == "mr":
        try:
            return translator.translate(text, src='en', dest='mr').text
        except:
            return text
    return text

def strip_think(text: str) -> str:
    # Remove any <think>...</think> block, non-greedy
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()

# ---------------------
# Main Chat Flow
# ---------------------
query = st.text_input("Ask your question (English or Marathi)")

if st.button("Send") and query.strip():
    user_q = query.strip()

    en_query, user_lang = detect_and_translate_to_en(user_q)

    if len(en_query.split()) <= 1:
        bot_reply = (
            "तुमचा प्रश्न थोडा अपूर्ण आहे. कृपया अधिक माहिती द्या "
            "(उदा. शिक्षण योजना, निवास योजना, कर्ज योजना, निवृत्तीवेतन योजना)."
            if user_lang == "mr"
            else "Your question seems incomplete. Please give more details "
                 "(e.g., education scheme, housing scheme, loan scheme, pension scheme)."
        )
        st.session_state.history.append(("user", user_q))
        st.session_state.history.append(("bot", bot_reply))

    else:
        with st.spinner("Fetching relevant schemes..."):
            # Retrieve top 3 relevant rows
            results = retriever.search(en_query, top_k=3)

        if not results or all(r.get('score',0) < 0.2 for r in results):
            bot_reply = (
                "क्षमस्व, तुमच्या प्रश्नासंबंधित कोणतीही योजना सापडली नाही. "
                "कृपया इतर कीवर्ड वापरून प्रयत्न करा."
                if user_lang == "mr"
                else "Sorry, I couldn’t find any related schemes. Please try different keywords."
            )
            st.session_state.history.append(("user", user_q))
            st.session_state.history.append(("bot", bot_reply))

        else:
            # Use raw retrieved texts directly, truncated for speed
            texts = [r['text'][:1200] for r in results]
            final_results = [{"text": t, "score": r['score']} for t, r in zip(texts, results)]

            prompt = make_prompt(user_q, "en", final_results)
            print("Final RAG prompt length:", len(prompt))

            # Call LLM with spinner
            with st.spinner("Generating answer..."):
                try:
                    start = time.time()
                    answer_en = call_ollama(prompt)
                    answer_en = strip_think(answer_en)  # Remove <think> blocks
                    end = time.time()
                    print("Ollama response time:", round(end-start,2), "s | Preview:", answer_en[:300])
                except Exception as e:
                    print("Error calling Ollama:", e)
                    answer_en = "Sorry, could not get a response from the LLM."

            final_answer = translate_back_to_mr(answer_en, user_lang)

            st.session_state.history.append(("user", user_q))
            st.session_state.history.append(("bot", final_answer))

# Display chat history
for role, text in st.session_state.history:
    if role == "user":
        st.markdown(f"**You:** {text}")
    else:
        st.markdown(f"**Bot:** {text}")
