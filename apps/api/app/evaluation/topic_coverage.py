import re
from typing import Dict, List


def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9α-ωΑ-Ω\- ]+", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def topic_is_covered(answer: str, topic: str) -> bool:
    normalized_answer = normalize_text(answer)
    normalized_topic = normalize_text(topic)

    if not normalized_topic:
        return False

    return normalized_topic in normalized_answer


def evaluate_topic_coverage(answer: str, expected_topics: List[str]) -> Dict:
    matched_topics = [
        topic for topic in expected_topics
        if topic_is_covered(answer, topic)
    ]

    total_topics = len(expected_topics)

    coverage = (
        len(matched_topics) / total_topics
        if total_topics > 0
        else 0
    )

    return {
        "expected_topics": expected_topics,
        "matched_topics": matched_topics,
        "missing_topics": [
            topic for topic in expected_topics
            if topic not in matched_topics
        ],
        "topic_coverage": round(coverage, 4),
    }
