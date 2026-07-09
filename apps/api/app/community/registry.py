import json
from pathlib import Path
from typing import List
from uuid import uuid4

from app.community.schemas import (
    CommunityIngestRequest,
    CommunitySourceRecord,
)


COMMUNITY_OUTPUT_DIR = Path("outputs/community")


def build_community_records(
    request: CommunityIngestRequest,
) -> List[CommunitySourceRecord]:
    records = []

    for source in request.sources:
        records.append(
            CommunitySourceRecord(
                community_id=str(uuid4()),
                document_id=request.document_id,
                topic=request.topic,
                query=source.query,
                platform=source.platform,
                subreddit=source.subreddit,
                thread_title=source.thread_title,
                url=source.url,
                score=source.score,
                text=source.text,
            )
        )

    return records


def export_community_sources(
    topic: str,
    records: List[CommunitySourceRecord],
) -> str:
    COMMUNITY_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    safe_topic = (
        topic.lower()
        .replace(" ", "_")
        .replace("/", "_")
        .replace("\\", "_")
    )

    output_path = COMMUNITY_OUTPUT_DIR / f"{safe_topic}_community_sources.json"

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(
            [record.model_dump() for record in records],
            file,
            indent=2,
            ensure_ascii=False,
        )

    return str(output_path)
