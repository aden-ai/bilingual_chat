SYSTEM_INSTRUCTIONS = """
You are an assistant that answers questions about government schemes using ONLY the provided passages.
Rules:
1. Do NOT provide reasoning, thoughts, or <think> tags.
2. Reply directly and concisely to the user's question.
3. Answer in the SAME LANGUAGE as the user's question.
4. Use only the facts from the passages; do NOT hallucinate.
5. Include Scheme Name, Short Description, Benefits, Eligibility, Required Documents, Ministry/Authority, Application Mode, Tags if available.
6. If no schemes match, say so politely.
7.Critically review your final answer to ensure it adheres to all rules, especially Rule 1 (No reasoning/thoughts).
"""


def make_prompt(user_question, lang, retrieved_snippets):
    user_question_clean = user_question.strip().replace('"', "'").replace("`", "")

    passages = []
    for i, item in enumerate(retrieved_snippets):
        text = item.get("text", "")
        passages.append(f"PASSAGE {i+1}:\n{text}")

    passage_block = "\n\n".join(passages) if passages else "NO PASSAGES FOUND."

    instruction = f"""{SYSTEM_INSTRUCTIONS}

**CRITICAL INSTRUCTION: Your answer MUST be based ONLY on the facts within the PASSAGES block.**

User Question: {user_question_clean}

Use ONLY the PASSAGES below to answer the question. If PASSAGES are not relevant, say "no relevant scheme found" and provide no other text.
{passage_block}

Answer:
"""
    return instruction

    
