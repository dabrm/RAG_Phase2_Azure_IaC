def format_answer_with_sources(answer: str, hits: list[dict]) -> str:

    lines = [answer, "\nSources:"]

    for i, h in enumerate(hits, start=1):
        lines.append(
            f"[{i}] {h['source']} — {h['chunk_id']}"
        )

    return "\n".join(lines)