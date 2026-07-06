import json
import time
from datetime import datetime, timezone
from pathlib import Path

from starlette.middleware.base import BaseHTTPMiddleware


class LatencyLoggingMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        output_path: str = "outputs/observability/api_latency_logs.jsonl",
    ):
        super().__init__(app)
        self.output_path = Path(output_path)

    async def dispatch(self, request, call_next):
        start_time = time.perf_counter()

        response = await call_next(request)

        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

        self.output_path.parent.mkdir(parents=True, exist_ok=True)

        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
        }

        with self.output_path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(event) + "\n")

        response.headers["X-Process-Time-ms"] = str(duration_ms)

        return response
