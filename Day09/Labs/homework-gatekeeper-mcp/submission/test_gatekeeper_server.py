from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

from fastmcp import Client


ROOT = Path(__file__).resolve().parent
SERVER = ROOT / "gatekeeper_server.py"
PYTHON = sys.executable


def start_server() -> subprocess.Popen[str]:
    return subprocess.Popen(
        [PYTHON, str(SERVER), "--http"],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        text=True,
    )


def wait_for_server(timeout_seconds: float = 10.0) -> None:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        if SERVER.exists():
            return
        time.sleep(0.2)
    raise RuntimeError("server did not become ready")


def main() -> None:
    process = start_server()
    checks = [
        ("route_ticket", {"text": "phishing email reported"}),
        ("route_ticket", {"text": "wifi is down"}),
        ("route_ticket", {"text": "printer jam"}),
        ("needs_approval", {"action": "search_kb", "user_id": "EMP-1001", "hour": 9}),
        ("needs_approval", {"action": "update_ticket", "user_id": "EMP-2000", "hour": 21}),
        ("needs_approval", {"action": "grant_access", "user_id": "EMP-2000", "hour": 10}),
    ]

    try:
        wait_for_server()
        with Client("http://127.0.0.1:8778/mcp") as client:
            tools = client.list_tools()
            tool_names = sorted(tool.name for tool in tools)
            print("PASS: listed tools" if tool_names == ["needs_approval", "route_ticket"] else f"FAIL: listed tools {tool_names}")

            for name, payload in checks:
                try:
                    result = client.call_tool(name, payload)
                    print(f"PASS: {name} {payload} -> {result}")
                except Exception as exc:
                    print(f"FAIL: {name} {payload} -> {exc}")
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()


if __name__ == "__main__":
    main()