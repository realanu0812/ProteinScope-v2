import argparse
import json
from pathlib import Path

from app.evaluation.llm_judge import judge_answer_event
from app.evaluation.topic_coverage import evaluate_topic_coverage
from app.generation.answer_pipeline import generate_grounded_answer
from app.generation.schemas import AnswerRequest


def load_eval_set(eval_path: str):
    with Path(eval_path).open("r", encoding="utf-8") as file:
        return json.load(file)


def export_json(data, output_path: str) -> str:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)

    return str(path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--eval-path", required=True)
    parser.add_argument("--chunks-path", required=True)
    parser.add_argument("--output-path", default="outputs/evals/batch_answer_results.json")
    parser.add_argument("--judge-output-path", default="outputs/evals/batch_answer_judge_results.json")
    parser.add_argument("--summary-output-path", default="outputs/evals/batch_answer_summary.json")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--dense-k", type=int, default=30)
    parser.add_argument("--bm25-k", type=int, default=30)
    parser.add_argument("--use-llm-judge", action="store_true")

    args = parser.parse_args()

    eval_items = load_eval_set(args.eval_path)
    answer_results = []

    for item in eval_items:
        request = AnswerRequest(
            question=item["question"],
            chunks_path=args.chunks_path,
            top_k=args.top_k,
            dense_k=args.dense_k,
            bm25_k=args.bm25_k,
            source_type="scientific_paper",
            trust_level="verified",
        )

        response = generate_grounded_answer(request)

        expected_topics = item.get("expected_topics", [])
        topic_coverage = evaluate_topic_coverage(
            answer=response.answer,
            expected_topics=expected_topics,
        )

        answer_results.append(
            {
                "question": item["question"],
                "expected_topics": expected_topics,
                "topic_coverage": topic_coverage,
                "answer": response.answer,
                "generator_model": response.generator_model,
                "retrieval_strategy": response.retrieval_strategy,
                "citations": [citation.model_dump() for citation in response.citations],
                "retrieved_sections": [
                    result.section for result in response.retrieved_context
                ],
            }
        )

    output_path = export_json(answer_results, args.output_path)
    print(f"Saved batch answer results to: {output_path}")

    average_topic_coverage = (
        sum(
            item["topic_coverage"]["topic_coverage"]
            for item in answer_results
        ) / len(answer_results)
        if answer_results
        else 0
    )

    summary = {
        "answer_count": len(answer_results),
        "average_topic_coverage": round(average_topic_coverage, 4),
        "top_k": args.top_k,
        "dense_k": args.dense_k,
        "bm25_k": args.bm25_k,
    }

    summary_output_path = export_json(summary, args.summary_output_path)
    print(f"Saved batch answer summary to: {summary_output_path}")
    print(f"Average topic coverage: {summary['average_topic_coverage']}")

    if args.use_llm_judge:
        judge_results = []

        for answer_result in answer_results:
            event = {
                "question": answer_result["question"],
                "answer": answer_result["answer"],
                "generator_model": answer_result["generator_model"],
                "retrieved_context": [
                    {
                        "section": citation["section"],
                        "start_page": citation["start_page"],
                        "end_page": citation["end_page"],
                        "preview": citation["text_preview"],
                    }
                    for citation in answer_result["citations"]
                ],
            }

            judge_results.append(judge_answer_event(event))

        judge_output_path = export_json(judge_results, args.judge_output_path)
        print(f"Saved batch answer judge results to: {judge_output_path}")


if __name__ == "__main__":
    main()
