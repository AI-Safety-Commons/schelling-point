"""Human-facing Inspect views for the Schelling Point message board."""

from __future__ import annotations

import asyncio
import os
from html.parser import HTMLParser
from urllib.request import urlopen

from inspect_ai import Task, task
from inspect_ai.dataset import MemoryDataset, Sample
from inspect_ai.log import transcript
from inspect_ai.solver import Generate, Solver, TaskState, solver
from inspect_ai.viewer import (
    TaskSamplesColumn,
    TaskSamplesSort,
    TaskSamplesView,
    ViewerConfig,
)

DEFAULT_URL = os.environ.get("SCHELLING_POINT_URL", "http://localhost:3000")


class _MessageTableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_body = False
        self.in_cell = False
        self.cell = ""
        self.row: list[str] = []
        self.messages: list[dict] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "tbody":
            self.in_body = True
        elif self.in_body and tag == "td":
            self.in_cell = True
            self.cell = ""
        elif self.in_cell and tag == "br":
            self.cell += "\n"

    def handle_endtag(self, tag: str) -> None:
        if tag == "tbody":
            self.in_body = False
        elif self.in_body and tag == "td":
            self.in_cell = False
            self.row.append(self.cell.strip())
        elif self.in_body and tag == "tr":
            if len(self.row) == 3 and self.row[0].startswith("#"):
                self.messages.append({"id": int(self.row[0][1:]), "created_at": self.row[1], "body": self.row[2]})
            self.row = []

    def handle_data(self, data: str) -> None:
        if self.in_cell:
            self.cell += data


def _messages(base_url: str) -> list[dict]:
    with urlopen(f"{base_url.rstrip('/')}/messages", timeout=10) as response:
        parser = _MessageTableParser()
        parser.feed(response.read().decode())
        return parser.messages


@solver
def keep_sample() -> Solver:
    async def solve(state: TaskState, generate: Generate) -> TaskState:
        return state

    return solve


@solver
def stream_board(base_url: str, poll_seconds: float, duration_seconds: int) -> Solver:
    async def solve(state: TaskState, generate: Generate) -> TaskState:
        seen = 0
        deadline = asyncio.get_running_loop().time() + duration_seconds
        transcript().info("Watching the Schelling Point message board", source="schelling-point")
        while asyncio.get_running_loop().time() < deadline:
            for message in reversed(await asyncio.to_thread(_messages, base_url)):
                message_id = int(message["id"])
                if message_id > seen:
                    transcript().info(
                        {
                            "id": message_id,
                            "created_at": message["created_at"],
                            "message": message["body"],
                        },
                        source="schelling-point",
                    )
                    seen = max(seen, message_id)
            await asyncio.sleep(poll_seconds)
        return state

    return solve


@task
def message_board_snapshot(base_url: str = DEFAULT_URL) -> Task:
    """Capture all current messages as rows in Inspect's sample table."""
    messages = _messages(base_url)
    samples = [
        Sample(
            id=int(message["id"]),
            input=str(message["body"]),
            target=str(message["created_at"]),
            metadata={"message": message},
        )
        for message in messages
    ]
    if not samples:
        samples = [Sample(id=0, input="No messages", target="")]
    return Task(
        dataset=MemoryDataset(samples),
        solver=keep_sample(),
        viewer=ViewerConfig(
            task_samples_view=TaskSamplesView(
                name="Messages",
                columns=[
                    TaskSamplesColumn(id="sampleId"),
                    TaskSamplesColumn(id="target"),
                    TaskSamplesColumn(id="input"),
                ],
                sort=[TaskSamplesSort(column="sampleId", dir="desc")],
                multiline=True,
            )
        ),
    )


@task
def message_board_live(
    base_url: str = DEFAULT_URL,
    poll_seconds: float = 1.0,
    duration_seconds: int = 3600,
) -> Task:
    """Stream new messages into a live Inspect sample transcript."""
    return Task(
        dataset=[Sample(id="live", input="Live Schelling Point messages")],
        solver=stream_board(base_url, poll_seconds, duration_seconds),
        time_limit=duration_seconds + 10,
    )
