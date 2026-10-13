from __future__ import annotations

import json
import subprocess
import sys
import urllib.error
import urllib.request
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SERVER = ROOT / "gatekeeper_server.py"
URL = "http://127.0.0.1:8778/mcp"
PYTHON = r"C:\Users\Admin\AppData\Local\Python\pythoncore-3.14-64\python.exe"


def rpc(method: str, params: dict | None = None, request_id: int = 1) -> dict:
    body = json.dumps({"jsonrpc": "2.0", "id": request_id, "method": method, "params": params or {}}).encode("utf-8")
    request = urllib.request.Request(URL, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def call_tool(name: str, arguments: dict, request_id: int) -> tuple[bool, str]:
    response = rpc("tools/call", {"name": name, "arguments": arguments}, request_id=request_id)
    if "error" in response:
        return False, response["error"].get("message", "error")
    return True, json.dumps(response.get("result", {}))


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
        try:
            rpc("tools/list", request_id=1)
            return
        except Exception:
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
        tools = rpc("tools/list", request_id=1)
        tool_names = sorted(tool["name"] for tool in tools.get("result", {}).get("tools", []))
        print("PASS: listed tools" if tool_names == ["needs_approval", "route_ticket"] else f"FAIL: listed tools {tool_names}")

        for index, (name, payload) in enumerate(checks, start=2):
            ok, _ = call_tool(name, payload, request_id=index)
            print(f"{'PASS' if ok else 'FAIL'}: {name} {payload}")
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()


if __name__ == "__main__":
    main()