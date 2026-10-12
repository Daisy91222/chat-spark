#!/usr/bin/env python3
"""Deterministic spark and boat scorer for aggregated desktop chat turns."""

import argparse
import json
import os
from datetime import date, timedelta
from pathlib import Path


def day(value):
    return date.fromisoformat(value)


def read_json(path, default=None):
    path = Path(path)
    if not path.exists():
        return default
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    os.replace(temporary, path)


def fire_badge(days, as_of):
    streak = 0
    cursor = as_of
    while days.get(cursor.isoformat(), {}).get("user_messages", 0) > 0:
        streak += 1
        cursor -= timedelta(days=1)
    if streak >= 30:
        return "🔥🔥🔥", streak
    if streak >= 7:
        return "🔥🔥", streak
    if streak >= 3:
        return "🔥", streak
    return "", streak


def daily_winner(threads, target):
    key = target.isoformat()
    contenders = [
        (record["days"].get(key, {}).get("completed_rounds", 0), thread_id)
        for thread_id, record in threads.items()
        if day(record["joinedDate"]) <= target
    ]
    if not contenders:
        return None
    highest = max(rounds for rounds, _ in contenders)
    if highest == 0:
        return None
    winners = [thread_id for rounds, thread_id in contenders if rounds == highest]
    return winners[0] if len(winners) == 1 else None


def compute_plan(snapshot, previous, start_date):
    as_of = day(snapshot["as_of"])
    start = day(previous["startDate"]) if previous else day(start_date)
    if start > as_of + timedelta(days=1):
        raise ValueError("start date is after the current local day")
    state = json.loads(json.dumps(previous)) if previous else {
        "schemaVersion": 1,
        "startDate": start.isoformat(),
        "lastProcessedDate": (start - timedelta(days=1)).isoformat(),
        "boatWinner": None,
        "boatStreak": 0,
        "threads": {},
    }
    if state.get("schemaVersion") != 1:
        raise ValueError("unsupported state version")
    last_processed = day(state["lastProcessedDate"])
    if as_of < last_processed:
        raise ValueError("snapshot is older than the committed state")
    if as_of - last_processed > timedelta(days=30):
        raise ValueError("more than 30 unverified days; restore coverage before scoring")

    seen = set()
    current_titles = {}
    for item in snapshot["threads"]:
        thread_id = item["id"]
        if thread_id in seen:
            raise ValueError("duplicate thread in snapshot: " + thread_id)
        seen.add(thread_id)
        first = day(item["scanned_from"])
        through = day(item["scanned_through"])
        if through != as_of or first > as_of:
            raise ValueError("incomplete scan for " + thread_id)
        required = as_of - timedelta(days=29)
        if first > required:
            raise ValueError("missing required dates for " + thread_id)
        current_titles[thread_id] = item["title"]
        record = state["threads"].setdefault(thread_id, {
            "kind": item["kind"],
            "joinedDate": (start if previous is None else max(start, as_of)).isoformat(),
            "lastSuffix": "",
            "days": {},
        })
        if record["kind"] != item["kind"]:
            raise ValueError("chat kind changed for " + thread_id)
        for key in list(record["days"]):
            if first <= day(key) <= through:
                del record["days"][key]
        for key, counts in item["days"].items():
            target = day(key)
            if not first <= target <= through:
                raise ValueError("day outside scan window for " + thread_id)
            messages = counts["user_messages"]
            rounds = counts["completed_rounds"]
            if not isinstance(messages, int) or not isinstance(rounds, int) or messages < 0 or rounds < 0 or rounds > messages:
                raise ValueError("invalid counts for " + thread_id)
            if messages or rounds:
                record["days"][key] = {"user_messages": messages, "completed_rounds": rounds}

    if previous and as_of > last_processed:
        critical_missing = [
            thread_id for thread_id, record in previous["threads"].items()
            if thread_id not in current_titles and (record["lastSuffix"] or thread_id == previous["boatWinner"])
        ]
        if critical_missing:
            raise ValueError("unreadable badge holder or boat leader: " + ", ".join(critical_missing))

    cursor = last_processed + timedelta(days=1)
    while cursor <= as_of:
        winner = daily_winner(state["threads"], cursor)
        if winner is not None and winner == state["boatWinner"]:
            state["boatStreak"] += 1
        else:
            state["boatWinner"] = winner
            state["boatStreak"] = 1 if winner else 0
        cursor += timedelta(days=1)
    state["lastProcessedDate"] = as_of.isoformat()

    actions = []
    badges = {}
    missing_titles = []
    for thread_id, record in state["threads"].items():
        fire, fire_streak = fire_badge(record["days"], as_of)
        boat = ""
        if thread_id == state["boatWinner"]:
            if state["boatStreak"] >= 30:
                boat = "🚢"
            elif state["boatStreak"] >= 7:
                boat = "⛵️"
        suffix = " " + " ".join(part for part in (fire, boat) if part) if fire or boat else ""
        badges[thread_id] = {"fireStreak": fire_streak, "boatStreak": state["boatStreak"] if boat else 0, "suffix": suffix}
        if thread_id not in current_titles:
            if record["lastSuffix"]:
                missing_titles.append(thread_id)
            continue
        old_title = current_titles[thread_id]
        old_suffix = record["lastSuffix"]
        base = old_title[:-len(old_suffix)] if old_suffix and old_title.endswith(old_suffix) else old_title
        new_title = base + suffix
        if new_title != old_title:
            actions.append({"threadId": thread_id, "oldTitle": old_title, "newTitle": new_title, "newSuffix": suffix})

    cutoff = as_of - timedelta(days=29)
    for record in state["threads"].values():
        record["days"] = {key: value for key, value in record["days"].items() if day(key) >= cutoff}
    return {"actions": actions, "nextState": state, "badges": badges, "missingTitles": missing_titles}


def main():
    parser = argparse.ArgumentParser()
    subcommands = parser.add_subparsers(dest="command", required=True)
    plan = subcommands.add_parser("plan")
    plan.add_argument("--snapshot", required=True)
    plan.add_argument("--state", required=True)
    plan.add_argument("--start-date", required=True)
    plan.add_argument("--output", required=True)
    commit = subcommands.add_parser("commit")
    commit.add_argument("--plan", required=True)
    commit.add_argument("--state", required=True)
    commit.add_argument("--applied", required=True)
    args = parser.parse_args()
    if args.command == "plan":
        result = compute_plan(read_json(args.snapshot), read_json(args.state), args.start_date)
        write_json(args.output, result)
        print(json.dumps({"actions": result["actions"], "missingTitles": result["missingTitles"]}, ensure_ascii=False))
    else:
        result = read_json(args.plan)
        prior = read_json(args.state, {"threads": {}})
        applied = set(read_json(args.applied))
        expected = {action["threadId"] for action in result["actions"]}
        if not applied <= expected:
            raise ValueError("applied IDs must be a subset of planned actions")
        next_state = result["nextState"]
        for action in result["actions"]:
            thread_id = action["threadId"]
            next_state["threads"][thread_id]["lastSuffix"] = (
                action["newSuffix"] if thread_id in applied
                else prior.get("threads", {}).get(thread_id, {}).get("lastSuffix", "")
            )
        write_json(args.state, next_state)
        print(json.dumps({"committed": True, "renamed": len(applied), "pending": len(expected - applied)}))


if __name__ == "__main__":
    main()
