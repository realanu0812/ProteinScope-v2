import re
from typing import List, Tuple

from app.retrieval.schemas import HybridSearchResult


MEDICAL_PATTERNS = [
    r"\bshould i take\b",
    r"\bcan i take\b",
    r"\bis it safe\b",
    r"\bside effects?\b",
    r"\bdosage\b",
    r"\bdose\b",
    r"\bpregnant\b",
    r"\bmedical\b",
    r"\bdisease\b",
    r"\btreatment\b",
]


MIN_CONTEXT_RESULTS = 1
MIN_TOP_FUSION_SCORE = 0.015


def is_medical_or_health_advice_question(question: str) -> bool:
    lowered = question.lower()

    return any(
        re.search(pattern, lowered)
        for pattern in MEDICAL_PATTERNS
    )


def validate_retrieved_context(
    results: List[HybridSearchResult],
) -> Tuple[bool, str]:
    if len(results) < MIN_CONTEXT_RESULTS:
        return False, "No relevant context was retrieved."

    top_result = results[0]

    if top_result.fusion_score < MIN_TOP_FUSION_SCORE:
        return False, "Retrieved context confidence is too low."

    return True, "Retrieved context passed guardrail checks."


def answer_has_citations(answer: str) -> bool:
    return bool(re.search(r"\[Source\s+\d+\]", answer))


def add_medical_disclaimer_if_needed(question: str, answer: str) -> str:
    if not is_medical_or_health_advice_question(question):
        return answer

    disclaimer = (
        "Note: This is not medical advice. The answer is based only on the provided document context. "
        "For personal health decisions, consult a qualified healthcare professional.\n\n"
    )

    if answer.startswith("Note: This is not medical advice."):
        return answer

    return disclaimer + answer


def validate_generated_answer(answer: str) -> Tuple[bool, str]:
    if not answer.strip():
        return False, "Generated answer is empty."

    if not answer_has_citations(answer):
        return False, "Generated answer does not include source citations."

    return True, "Generated answer passed guardrail checks."
