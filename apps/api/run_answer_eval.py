import argparse

from app.evaluation.answer_eval import evaluate_answer_logs, export_answer_eval_report


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

    args = parser.parse_args()

    results = evaluate_answer_logs(args.log_path)
    output_path = export_answer_eval_report(results, args.output_path)

    print(f"Saved answer evaluation report to: {output_path}")
    print(f"Answer count: {results['answer_count']}")
    print(f"Pass rate: {results['pass_rate']}")
    print(f"Citation usage rate: {results['citation_usage_rate']}")


if __name__ == "__main__":
    main()
