import argparse
import json
from collections import defaultdict
from pathlib import Path


def percentile(values, p):
    if not values:
        return 0

    sorted_values = sorted(values)
    index = int((len(sorted_values) - 1) * p)
    return sorted_values[index]


def load_latency_logs(log_path: str):
    path = Path(log_path)

    if not path.exists():
        raise FileNotFoundError(f"Latency log not found: {log_path}")

    events = []

    with path.open("r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                events.append(json.loads(line))

    return events


def summarize_latency(events):
    grouped = defaultdict(list)

    for event in events:
        key = f"{event['method']} {event['path']}"
        grouped[key].append(event["duration_ms"])

    summary = {}

    for endpoint, durations in grouped.items():
        summary[endpoint] = {
            "count": len(durations),
            "avg_ms": round(sum(durations) / len(durations), 2),
            "min_ms": round(min(durations), 2),
            "max_ms": round(max(durations), 2),
            "p50_ms": round(percentile(durations, 0.50), 2),
            "p95_ms": round(percentile(durations, 0.95), 2),
        }

    return summary


def export_json(data, output_path: str):
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)

    return str(path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--log-path",
        default="outputs/observability/api_latency_logs.jsonl",
    )
    parser.add_argument(
        "--output-path",
        default="outputs/observability/api_latency_summary.json",
    )

    args = parser.parse_args()

    events = load_latency_logs(args.log_path)
    summary = summarize_latency(events)
    output_path = export_json(summary, args.output_path)

    print(f"Saved latency summary to: {output_path}")

    for endpoint, stats in summary.items():
        print(
            f"{endpoint}: "
            f"count={stats['count']}, "
            f"avg={stats['avg_ms']}ms, "
            f"p95={stats['p95_ms']}ms"
        )


if __name__ == "__main__":
    main()
