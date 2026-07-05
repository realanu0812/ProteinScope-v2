import argparse
import json
from pathlib import Path

from app.evaluation.answer_eval import evaluate_answer_logs, export_answer_eval_report, load_answer_logs
from app.evaluation.llm_judge import judge_answer_event


def export_json(results, output_path: str) -> str:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(results, file, indent=2, ensure_ascii=False)

    return str(path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--log-path",
        default="outputs/generation/answer_logs.jsonl",
    )
    parser.add_argument(
        "--output-path",
        default="outputs/evals/answer_eval_results.json",
    )
    parser.add_argument(
        "--judge-output-path",
        default="outputs/evals/answer_judge_results.json",
    )
    parser.add_argument(
        "--use-llm-judge",
        action="store_true",
    )
    parser.add_argument(
        "--max-events",
        type=int,
        default=10,
    )

    args = parser.parse_args()

    results = evaluate_answer_logs(args.log_path)
    output_path = export_answer_eval_report(results, args.output_path)

    print(f"Saved answer evaluation report to: {output_path}")
    print(f"Answer count: {results['answer_count']}")
    print(f"Pass rate: {results['pass_rate']}")
    print(f"Citation usage rate: {results['citation_usage_rate']}")

    if args.use_llm_judge:
        events = load_answer_logs(args.log_path)[: args.max_events]

        judge_results = [
            judge_answer_event(event)
            for event in events
        ]

        judge_output_path = export_json(
            judge_results,
            args.judge_output_path,
        )

        print(f"Saved LLM judge report to: {judge_output_path}")


if __name__ == "__main__":
    main()
