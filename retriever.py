import os
import pandas as pd
from sentence_transformers import SentenceTransformer
import faiss
import pickle


EMBED_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"
INDEX_PATH = "faiss_index.bin"
META_PATH = "index_meta.pkl"


class Retriever:
    def __init__(self, csv_path="data/updated_data.csv", force_rebuild=False):
        self.csv_path = csv_path
        self.model = SentenceTransformer(EMBED_MODEL)
        self.index = None
        self.meta = None

        index_exists = os.path.exists(INDEX_PATH)
        meta_exists = os.path.exists(META_PATH)
        index_not_empty = index_exists and os.path.getsize(INDEX_PATH) > 0

        if force_rebuild or not index_exists or not meta_exists or not index_not_empty:
            print("⚠️ FAISS index missing or empty — rebuilding...")
            self._build_index()
        else:
            print("📦 Loading FAISS index...")
            self._load_index()

    def _load_index(self):
        self.index = faiss.read_index(INDEX_PATH)
        with open(META_PATH, "rb") as f:
            self.meta = pickle.load(f)

    def _build_index(self):
        # Explicitly specify encoding to avoid decode errors
        df = pd.read_csv(self.csv_path, encoding="utf-8")
        df.fillna("", inplace=True)

        # Combine relevant columns into text passages
        docs = []
        for _, row in df.iterrows():
            text = " || ".join([
                str(row.get("scheme_name", "")),
                str(row.get("details", "")),
                str(row.get("benefits", "")),
                str(row.get("eligibility", "")),
                str(row.get("schemeCategory", "")),
                str(row.get("tags", ""))
            ])
            docs.append(text)

        embeddings = self.model.encode(docs, show_progress_bar=True, convert_to_numpy=True)
        d = embeddings.shape[1]
        index = faiss.IndexFlatIP(d)
        faiss.normalize_L2(embeddings)
        index.add(embeddings)

        self.index = index
        self.meta = {"csv_path": self.csv_path, "docs": docs}
        faiss.write_index(self.index, INDEX_PATH)
        with open(META_PATH, "wb") as f:
            pickle.dump(self.meta, f)

    def search(self, query, top_k=5):
        q_emb = self.model.encode([query], convert_to_numpy=True)
        faiss.normalize_L2(q_emb)
        D, I = self.index.search(q_emb, top_k)
        results = []
        df = pd.read_csv(self.csv_path, encoding="utf-8")
        for score, idx in zip(D[0], I[0]):
            if idx < 0:
                continue
            row = df.iloc[idx].to_dict()
            results.append({
                "score": float(score),
                "text": " || ".join([str(v) for v in row.values() if v]),
                "row": row
            })
        return results
