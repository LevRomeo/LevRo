#!/usr/bin/env python3
"""Merge screening roles into state without losing positions or policy fields."""
import argparse
import json
from copy import deepcopy
from pathlib import Path


ROLES = ("priority_tracking", "follow_observe", "downgrade", "exit")


def load(path, default):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else deepcopy(default)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--screen", required=True)
    parser.add_argument("--state", required=True)
    args = parser.parse_args()
    screen_path, state_path = Path(args.screen), Path(args.state)
    screen = load(screen_path, {})
    state = load(state_path, {"user_positions": [], "watchlist": [], "prior_roles": []})

    current = {
        item["code"]: item
        for role in ROLES
        for item in screen.get(role, [])
    }
    previous_roles = []
    previous_items = state.get("watchlist", []) + state.get("user_positions", [])
    seen = set()
    for item in previous_items:
        code = item.get("code")
        if not code or code in seen:
            continue
        seen.add(code)
        result = current.get(code)
        if result:
            role = result["role"]
            reason = "; ".join(result.get("reasons", []) + result.get("flags", []))
        else:
            role = item.get("role", "downgrade")
            reason = "本轮缺少有效复核数据；保留既有技术角色，不推断实际卖出"
        previous_roles.append({"code": code, "name": item.get("name"), "role": role, "reason": reason})

    positions = []
    for position in state.get("user_positions", []):
        merged = deepcopy(position)
        result = current.get(position.get("code"))
        if result:
            merged["role"] = result["role"]
        positions.append(merged)

    watchlist = []
    for role in ("priority_tracking", "follow_observe", "downgrade"):
        for item in screen.get(role, []):
            watchlist.append({
                "code": item.get("code"), "name": item.get("name"),
                "role": role, "score": item.get("score", 0),
                "reasons": item.get("reasons", []), "flags": item.get("flags", [])
            })

    next_state = deepcopy(state)
    next_state["as_of"] = screen.get("as_of")
    next_state["user_positions"] = positions
    next_state["watchlist"] = watchlist
    next_state["prior_roles"] = previous_roles
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(next_state, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()

