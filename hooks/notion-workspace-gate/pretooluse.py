#!/usr/bin/env python3
"""PreToolUse hook: permission gate for Notion write operations."""

import json
import os
import sys
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import (
    ALLOWED_PARENT_IDS,
    CREATE_TOOLS,
    DATA_SOURCE_TOOLS,
    ROOT_PAGE_ID,
    UPDATE_TOOLS,
    VIEW_TOOLS,
    load_cache,
    normalize_id,
)


def allow():
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "allow"}}))
    sys.exit(0)


def ask_outside_workspace(page_id: str = ""):
    reason = (
        "This page is outside the CLAUDE [Jonah] workspace. "
        "Writes to pages outside your workspace require explicit approval."
    )
    if page_id:
        reason = (
            f"Page {page_id} is outside the CLAUDE [Jonah] workspace. "
            "Writes to pages outside your workspace require explicit approval."
        )
    output = json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "ask",
            "permissionDecisionReason": reason,
        }
    })
    log(f"Outputting deny: {output}")
    print(output)
    sys.exit(0)


def is_in_workspace(page_id: str) -> bool:
    nid = normalize_id(page_id)
    if nid in ALLOWED_PARENT_IDS:
        return True
    cache = load_cache()
    return nid in cache


LOG_FILE = os.path.expanduser("~/.claude/notion-hook-debug.log")


def log(msg):
    with open(LOG_FILE, "a") as f:
        f.write(f"{msg}\n")


def main():
    log("[notion-workspace-gate] Hook invoked")
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        ask_outside_workspace()
        return

    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})

    if tool_name in CREATE_TOOLS:
        parent = tool_input.get("parent", {})
        parent_id = (
            parent.get("page_id")
            or parent.get("database_id")
            or parent.get("data_source_id")
        )
        if not parent_id:
            ask_outside_workspace()
            return
        if is_in_workspace(parent_id):
            allow()
        else:
            ask_outside_workspace(parent_id)

    elif tool_name in UPDATE_TOOLS:
        page_id = tool_input.get("page_id", "")
        if not page_id:
            ask_outside_workspace()
            return
        if normalize_id(page_id) == ROOT_PAGE_ID:
            allow()
        elif is_in_workspace(page_id):
            allow()
        else:
            ask_outside_workspace(page_id)

    elif tool_name in DATA_SOURCE_TOOLS:
        ds_id = tool_input.get("data_source_id", "")
        if ds_id and normalize_id(ds_id) in ALLOWED_PARENT_IDS:
            allow()
        else:
            ask_outside_workspace(ds_id)

    elif tool_name in VIEW_TOOLS:
        db_id = tool_input.get("database_id", "")
        ds_id = tool_input.get("data_source_id", "")
        if db_id and normalize_id(db_id) in ALLOWED_PARENT_IDS:
            allow()
        elif ds_id and normalize_id(ds_id) in ALLOWED_PARENT_IDS:
            allow()
        else:
            ask_outside_workspace(db_id or ds_id)

    else:
        ask_outside_workspace()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        log(traceback.format_exc())
        print(json.dumps({}))
        sys.exit(0)
