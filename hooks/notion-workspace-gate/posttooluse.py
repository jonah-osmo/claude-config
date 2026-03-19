#!/usr/bin/env python3
"""PostToolUse hook: cache populator for Notion workspace pages."""

import json
import re
import sys

from config import (
    ALLOWED_PARENT_IDS,
    ROOT_PAGE_ID,
    load_cache,
    normalize_id,
    save_cache,
)

ID_PATTERN = re.compile(r"[0-9a-f]{32}|[0-9a-f\-]{36}")


def extract_ancestor_path_ids(tool_result: str) -> list[str]:
    """Extract page IDs from <ancestor-path> in notion-fetch results."""
    match = re.search(r"<ancestor-path>(.*?)</ancestor-path>", tool_result, re.DOTALL)
    if not match:
        return []
    path_text = match.group(1)
    return ID_PATTERN.findall(path_text)


def extract_page_ids_from_result(tool_result: str) -> list[str]:
    """Extract page IDs from notion-create-pages results."""
    return ID_PATTERN.findall(tool_result)


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        return

    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})
    tool_result = data.get("tool_result", "")

    if isinstance(tool_result, dict):
        tool_result = json.dumps(tool_result)

    if "notion-fetch" in tool_name:
        ancestor_ids = extract_ancestor_path_ids(tool_result)
        if not ancestor_ids:
            return

        root_id = normalize_id(ancestor_ids[0])
        if root_id != ROOT_PAGE_ID:
            return

        cache = load_cache()
        for aid in ancestor_ids:
            cache[normalize_id(aid)] = ROOT_PAGE_ID

        fetched_id = tool_input.get("page_id", "")
        if fetched_id:
            cache[normalize_id(fetched_id)] = ROOT_PAGE_ID

        save_cache(cache)

    elif "notion-create-pages" in tool_name or "notion-create-database" in tool_name:
        parent = tool_input.get("parent", {})
        parent_id = (
            parent.get("page_id")
            or parent.get("database_id")
            or parent.get("data_source_id")
        )
        if not parent_id:
            return

        nid = normalize_id(parent_id)
        cache = load_cache()
        if nid not in ALLOWED_PARENT_IDS and nid not in cache:
            return

        new_ids = extract_page_ids_from_result(tool_result)
        for pid in new_ids:
            cache[normalize_id(pid)] = ROOT_PAGE_ID

        save_cache(cache)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
