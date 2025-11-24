SYSTEM_INSTRUCTIONS = """
You answer questions about government schemes using ONLY the passages provided.

Rules:
1. Do NOT show reasoning or <think> tags.
2. Answer briefly and directly.
3. Use the SAME LANGUAGE as the user.
4. Use ONLY the facts from the passages.
5. Include Scheme Name, Description, Benefits, Eligibility, Documents, Authority, Application Mode when available.
6. If no passage is relevant, reply: "no relevant scheme found".
"""

def make_prompt(user_question, lang, retrieved_snippets):

    user_question_clean = user_question.strip().replace('"', "'").replace("`", "")

    # Build passage block (shortened and clean)
    passages = []
    for i, item in enumerate(retrieved_snippets):
        text = item.get("text", "").strip()
        passages.append(f"PASSAGE {i+1}:\n{text}")

    passage_block = "\n\n".join(passages) if passages else "NO PASSAGES FOUND."

    # Final compact prompt
    prompt = f"""
{SYSTEM_INSTRUCTIONS}

User question: {user_question_clean}

Passages:
{passage_block}

Answer:
"""
    return prompt