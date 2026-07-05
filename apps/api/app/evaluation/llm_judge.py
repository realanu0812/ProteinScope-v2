import json
from typing import Dict

from app.generation.groq_provider import GroqGenerationProvider


def build_judge_prompt(event: Dict) -> str:
    question = event.get("question", "")
    answer = event.get("answer", "")
    retrieved_context = event.get("retrieved_context", [])

    context_blocks = []

    for index, item in enumerate(retrieved_context, start=1):
        context_blocks.append(
            f"[Source {index}]\n"
            f"Section: {item.get('section')}\n"
            f"Pages: {item.get('start_page')}-{item.get('end_page')}\n"
            f"Text Preview: {item.get('preview')}"
        )

    context_text = "\n\n".join(context_blocks)

    return f"""
You are evaluating a RAG answer.

Question:
{question}

Retrieved Context:
{context_text}

Answer:
{answer}

Score the answer from 1 to 5 for each metric:

1. faithfulness: Does the answer stay supported by the retrieved context?
2. relevance: Does it answer the question?
3. completeness: Does it cover the important points available in the context?
4. citation_quality: Are citations used correctly and meaningfully?

Return ONLY valid JSON in this exact format:
{{
  "faithfulness": 1,
  "relevance": 1,
  "completeness": 1,
  "citation_quality": 1,
  "reason": "brief explanation"
}}
""".strip()


def parse_judge_response(raw_response: str) -> Dict:
    try:
        return json.loads(raw_response)
    except json.JSONDecodeError:
        return {
            "faithfulness": 0,
            "relevance": 0,
            "completeness": 0,
            "citation_quality": 0,
            "reason": "Failed to parse judge response as JSON.",
            "raw_response": raw_response,
        }


def judge_answer_event(event: Dict) -> Dict:
    judge = GroqGenerationProvider()
    prompt = build_judge_prompt(event)
    raw_response = judge.generate(prompt)

    scores = parse_judge_response(raw_response)

    return {
        "question": event.get("question"),
        "generator_model": event.get("generator_model"),
        "judge_model": judge.model_name(),
        "scores": scores,
    }
