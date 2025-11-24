# 🇮🇳 Bilingual  Chatbot (English + Marathi)

This project is a simple **RAG (Retrieval-Augmented Generation) app** that answers questions about **Indian Government Schemes** using a local **CSV file**, **FAISS**, and **Ollama** as the LLM.  
It supports both **English and Marathi**, auto-detects the language, and replies in the same language.

---

## 🚀 Features
- Ask questions in **English or Marathi**
- Fast **FAISS vector search** over CSV dataset
- Uses **Ollama (Qwen2.5:3b)** as the local LLM
- Translates Marathi ↔ English automatically
- Streamlit chat UI with history
- Fully offline after installation

---

## 🛠️ Tech Stack
- **Streamlit** → UI for chat  
- **FAISS** → Vector store for fast retrieval  
- **Sentence Transformers** → Embedding model  
- **Ollama** → Local LLM backend  
- **deep-translator + langdetect** → Language detection & translation  
- **Pandas** → CSV handling  

---
## ⚡ Quick Start

Get up and running in minutes 🚀

```bash
# 1️⃣ Clone the repo
git clone https://github.com/your-username/gov-schemes-chatbot.git
cd gov-schemes-chatbot

# 2️⃣ Create & activate virtual environment
python -m venv venv
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate         # Windows

# 3️⃣ Install dependencies
pip install streamlit sentence-transformers faiss-cpu pandas langdetect deep-translator requests

# 4️⃣ Install Ollama and pull the model
ollama pull qwen2.5:3b

# 5️⃣ Launch the app 
streamlit run app.py



