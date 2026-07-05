import json
import re
from pathlib import Path
from typing import Dict, List


def load_answer_logs(log_path: str) -> List[Dict]:
    path = Path(log_path)

    if not path.exists():
        raise FileNotFoundError(f"Answer log not found: {log_path}")

    events = []

    with path.open("r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                events.append(json.loads(line))

    return events


def extract_citation_numbers(answer: str) -> List[int]:
    matches = re.findall(r"\[Source\s+(\d+)\]", answer)
    return [int(match) for match in matches]


def evaluate_answer_event(event: Dict) -> Dict:
    answer = event.get("answer", "")
    citations = event.get("citations", [])
    retrieved_context = event.get("retrieved_context", [])

    citation_numbers = extract_citation_numbers(answer)
    valid_citation_ids = {citation["citation_id"] for citation in citations}

    has_answer = bool(answer.strip())
    has_context = len(retrieved_context) > 0
    has_citations_in_answer = len(citation_numbers) > 0

    invalid_citations = [
        citation_number
        for citation_number in citation_numbers
        if citation_number not in valid_citation_ids
    ]

    citation_validity = len(invalid_citations) == 0

    return {
        "question": event.get("question"),
        "generator_model": event.get("generator_model"),
        "has_answer": has_answer,
        "has_context": has_context,
        "has_citations_in_answer": has_citations_in_answer,
        "citation_validity": citation_validity,
        "invalid_citations": invalid_citations,
        "retrieved_context_count": len(retrieved_context),
        "citation_count": len(citations),
        "answer_char_count": len(answer),
        "passed": (
            has_answer
            and has_context
            and has_citations_in_answer
            and citation_validity
        ),
    }


def evaluate_answer_logs(log_path: str) -> Dict:
    events = load_answer_logs(log_path)

    evaluated_events = [
        evaluate_answer_event(event)
        for event in events
    ]

    if evaluated_events:
        pass_rate = sum(event["passed"] for event in evaluated_events) / len(evaluated_events)
        citation_usage_rate = sum(
            event["has_citations_in_answer"] for event in evaluated_events
        ) / len(evaluated_events)
    else:
        pass_rate = 0
        citation_usage_rate = 0

    return {
        "answer_count": len(evaluated_events),
        "pass_rate": round(pass_rate, 4),
        "citation_usage_rate": round(citation_usage_rate, 4),
        "events": evaluated_events,
    }


def export_answer_eval_report(results: Dict, output_path: str) -> str:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(results, file, indent=2, ensure_ascii=False)

    return str(path)
