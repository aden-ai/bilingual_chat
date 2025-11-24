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

        # Load CSV once
        self.df = pd.read_csv(self.csv_path, encoding="utf-8")
        self.df.fillna("", inplace=True)

        index_exists = os.path.exists(INDEX_PATH)
        meta_exists = os.path.exists(META_PATH)

        if force_rebuild or not index_exists or not meta_exists:
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
        docs = []

        for _, row in self.df.iterrows():

            scheme_name = str(row.get("scheme_name", "")).strip()
            details = str(row.get("details", "")).strip()
            benefits = str(row.get("benefits", "")).strip()
            elig = str(row.get("eligibility", "")).strip()
            tags = str(row.get("tags", "")).strip()

            # BOOST scheme name heavily ×5
            # BOOST tags ×3
            combined_text = (
                (scheme_name + " ") * 5 +
                (tags + " ") * 3 +
                details + " " +
                benefits + " " +
                elig
            )

            docs.append(combined_text)

        embeddings = self.model.encode(docs, show_progress_bar=True, convert_to_numpy=True)

        d = embeddings.shape[1]
        faiss.normalize_L2(embeddings)

        index = faiss.IndexFlatIP(d)
        index.add(embeddings)

        self.index = index
        self.meta = {"docs": docs}

        faiss.write_index(self.index, INDEX_PATH)
        with open(META_PATH, "wb") as f:
            pickle.dump(self.meta, f)

    def search(self, query, top_k=3):
        q_emb = self.model.encode([query], convert_to_numpy=True)
        faiss.normalize_L2(q_emb)

        D, I = self.index.search(q_emb, top_k)

        results = []

        for score, idx in zip(D[0], I[0]):
            if idx < 0:
                continue

            row = self.df.iloc[idx].to_dict()

            # Short clean passage
            text = " ".join([
                str(row.get("scheme_name", "")),
                str(row.get("details", ""))[:350],
                str(row.get("benefits", ""))[:200],
                str(row.get("eligibility", ""))[:200]
            ])

            results.append({
                "score": float(score),
                "text": text.strip(),
                "row": row
            })

        return results