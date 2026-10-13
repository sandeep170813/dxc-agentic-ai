from __future__ import annotations

import argparse
from fastmcp import FastMCP

from gatekeeper import needs_approval as gatekeeper_needs_approval, route


server = FastMCP("AskIT Gatekeeper")


@server.tool(description="Route an IT ticket text to the best support team.")
def route_ticket(text: str) -> str:
    return route(text)


@server.tool(description="Decide whether a ticket action needs approval for a user at a given hour.")
def needs_approval(action: str, user_id: str, hour: int) -> bool:
    return bool(gatekeeper_needs_approval(action, user_id, hour)["approval"])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--http", action="store_true")
    args = parser.parse_args()

    if args.http:
        server.run(transport="http", host="127.0.0.1", port=8778)
    else:
        server.run()


if __name__ == "__main__":
    main()