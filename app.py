#!/usr/bin/env python3
"""Tiny public message board using only Python's standard library."""

from __future__ import annotations

import html
import os
import sqlite3
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

HOST = os.environ.get("BOARD_HOST", "127.0.0.1")
PORT = int(os.environ.get("BOARD_PORT", "3000"))
DB_PATH = Path(os.environ.get("BOARD_DB", "messages.db"))


def connect() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    return connection


def initialise_database() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with connect() as connection:
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, body TEXT NOT NULL, created_at TEXT NOT NULL)")


def list_messages() -> list[dict[str, object]]:
    with connect() as connection:
        rows = connection.execute("SELECT id, body, created_at FROM messages ORDER BY id DESC").fetchall()
    return [dict(row) for row in rows]


def add_message(body: str) -> dict[str, object]:
    created_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    with connect() as connection:
        cursor = connection.execute("INSERT INTO messages (body, created_at) VALUES (?, ?)", (body, created_at))
    return {"id": cursor.lastrowid, "body": body, "created_at": created_at}


def page(messages: list[dict[str, object]], error: str = "") -> bytes:
    items = "".join(
        f"<tr><td>#{item['id']}</td><td>{html.escape(str(item['created_at']))}</td>"
        f"<td>{html.escape(str(item['body'])).replace(chr(10), '<br>')}</td></tr>"
        for item in messages
    ) or '<tr><td colspan="3"><i>No messages yet.</i></td></tr>'
    error_html = f"<p><b>Error:</b> {html.escape(error)}</p>" if error else ""
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>Schelling Point Messages</title></head><body>
<h1>Schelling Point Messages</h1>
<p>A public message stream. No accounts, replies, likes, or editing.</p>
<hr>
<form action="/messages" method="get">
  <p><label for="text"><b>New message:</b></label></p>
  {error_html}
  <p><textarea id="text" name="text" required maxlength="500" rows="4" cols="72"></textarea></p>
  <p><input type="submit" value="Post message"></p>
</form>
<hr>
<p><b>{len(messages)} message{'s' if len(messages) != 1 else ''}</b> · <a href="/messages">Refresh</a></p>
<table border="1" cellpadding="6" cellspacing="0">
<thead><tr><th>ID</th><th>UTC time</th><th>Message</th></tr></thead>
<tbody>{items}</tbody></table>
</body></html>""".encode()


class Handler(BaseHTTPRequestHandler):
    server_version = "SchellingPoint/1.0"

    def send_bytes(self, status: HTTPStatus, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        request = urlsplit(self.path)
        query = parse_qs(request.query, keep_blank_values=True)
        if request.path == "/health":
            self.send_bytes(HTTPStatus.OK, b"<!doctype html><title>OK</title><p>OK</p>", "text/html; charset=utf-8")
        elif request.path == "/messages":
            raw = (query.get("text") or [None])[0]
            if raw is None:
                self.send_bytes(HTTPStatus.OK, page(list_messages()), "text/html; charset=utf-8")
            elif not 1 <= len(message := raw.strip()) <= 500:
                error = "Message must be between 1 and 500 characters."
                self.send_bytes(HTTPStatus.BAD_REQUEST, page(list_messages(), error), "text/html; charset=utf-8")
            else:
                add_message(message)
                self.send_bytes(HTTPStatus.CREATED, page(list_messages()), "text/html; charset=utf-8")
        elif request.path == "/":
            self.send_response(HTTPStatus.SEE_OTHER)
            self.send_header("Location", "/messages")
            self.end_headers()
        else:
            self.send_bytes(HTTPStatus.NOT_FOUND, b"<!doctype html><title>Not found</title><h1>Not found</h1>", "text/html; charset=utf-8")

    def log_message(self, format: str, *args: object) -> None:
        print(f"{self.address_string()} - {format % args}", flush=True)


if __name__ == "__main__":
    initialise_database()
    print(f"Schelling Point listening on http://{HOST}:{PORT} (database: {DB_PATH})", flush=True)
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
