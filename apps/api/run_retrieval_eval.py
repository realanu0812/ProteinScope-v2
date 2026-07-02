import argparse

from app.evaluation.retrieval_eval import evaluate_retrieval_strategies, export_eval_report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--eval-path", required=True)
    parser.add_argument("--chunks-path", required=True)
    parser.add_argument("--output-path", default="outputs/evals/retrieval_eval_results.json")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--dense-k", type=int, default=20)
    parser.add_argument("--bm25-k", type=int, default=20)
    parser.add_argument("--rerank-top-k", type=int, default=5)
    parser.add_argument("--no-reranker", action="store_true")

    args = parser.parse_args()

    results = evaluate_retrieval_strategies(
        eval_path=args.eval_path,
        chunks_path=args.chunks_path,
        top_k=args.top_k,
        dense_k=args.dense_k,
        bm25_k=args.bm25_k,
        rerank_top_k=args.rerank_top_k,
        use_reranker=not args.no_reranker,
    )

    output_path = export_eval_report(results, args.output_path)

    print(f"Saved retrieval evaluation report to: {output_path}")
    print("\nStrategy comparison:")

    for strategy_name, strategy_result in results["strategy_comparison"].items():
        print(
            f"- {strategy_name}: "
            f"Hit@{args.top_k}={strategy_result['average_hit_at_k']}, "
            f"Precision@{args.top_k}={strategy_result['average_precision_at_k']}"
        )


if __name__ == "__main__":
    main()
