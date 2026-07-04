from typing import List

from app.retrieval.schemas import HybridSearchResult


def build_grounded_prompt(question: str, contexts: List[HybridSearchResult]) -> str:
    context_blocks = []

    for index, result in enumerate(contexts, start=1):
        pages = (
            str(result.start_page)
            if result.start_page == result.end_page
            else f"{result.start_page}-{result.end_page}"
        )

        context_blocks.append(
            f"[Source {index}]\n"
            f"Section: {result.section or 'unknown'}\n"
            f"Pages: {pages}\n"
            f"Text:\n{result.text}"
        )

    context_text = "\n\n".join(context_blocks)

    return f"""
You are ProteinScope, a scientific research assistant.

Answer the user's question using ONLY the provided sources.

Rules:
- Do not use outside knowledge.
- If the sources do not contain enough information, say that the answer is not clear from the provided document.
- Cite sources inline using [Source 1], [Source 2], etc.
- Be concise but complete.
- Prefer scientific accuracy over sounding confident.

Question:
{question}

Sources:
{context_text}

Answer:
""".strip()
