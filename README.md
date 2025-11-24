🇮🇳 Government Schemes Chatbot (English & Marathi)

A bilingual chatbot that answers questions about Indian Government Schemes using a CSV file, FAISS search, and a local LLM (Ollama Qwen2.5-3B).

⭐ Features

Bilingual support (English + Marathi)

Fast offline retrieval using FAISS

Uses your CSV dataset

Runs completely offline

🛠️ Installation Commands

Copy and paste these into VS Code terminal:

1️⃣ Install dependencies
pip install streamlit sentence-transformers faiss-cpu pandas langdetect deep-translator requests

2️⃣ Install Ollama

Download from: https://ollama.com

3️⃣ Pull the required model
ollama pull qwen2.5:3b

▶️ Run the App

Copy this command in VS Code terminal:

streamlit run app.py


Then open in browser:

http://localhost:8501