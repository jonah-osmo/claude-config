#!/usr/bin/env python3
"""Smoke tests for Notion workspace permission hooks."""

import json
import os
import subprocess
import sys
import tempfile

HOOKS_DIR = os.path.join(
    os.path.dirname(__file__),
    "..",
    "hooks",
    "notion-workspace-gate",
)

# Use a temp cache file for tests
TEST_CACHE = tempfile.mktemp(suffix=".json")
os.environ["_TEST_CACHE_OVERRIDE"] = TEST_CACHE


def run_hook(script: str, stdin_data: dict) -> dict:
    result = subprocess.run(
        [sys.executable, os.path.join(HOOKS_DIR, script)],
        input=json.dumps(stdin_data),
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONPATH": HOOKS_DIR},
    )
    if result.returncode != 0:
        print(f"STDERR: {result.stderr}", file=sys.stderr)
    output = result.stdout.strip()
    if not output:
        return {}
    return json.loads(output)


def is_allow(result: dict) -> bool:
    return result.get("hookSpecificOutput", {}).get("permissionDecision") == "allow"


def is_ask(result: dict) -> bool:
    return result == {} or "permissionDecision" not in result.get(
        "hookSpecificOutput", {}
    )


def cleanup_cache():
    for f in [TEST_CACHE, TEST_CACHE + ".lock"]:
        try:
            os.unlink(f)
        except FileNotFoundError:
            pass


def test_create_known_parent():
    """create-pages with known parent → allow"""
    result = run_hook(
        "pretooluse.py",
        {
            "tool_name": "mcp__plugin_Notion_notion__notion-create-pages",
            "tool_input": {
                "parent": {"database_id": "3190f22f-7b6e-8012-b3b1-c1c3e2b48e0f"}
            },
        },
    )
    assert is_allow(result), f"Expected allow, got {result}"
    print("PASS: create with known parent → allow")


def test_create_unknown_parent():
    """create-pages with unknown parent → ask"""
    result = run_hook(
        "pretooluse.py",
        {
            "tool_name": "mcp__plugin_Notion_notion__notion-create-pages",
            "tool_input": {
                "parent": {"page_id": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"}
            },
        },
    )
    assert is_ask(result), f"Expected ask, got {result}"
    print("PASS: create with unknown parent → ask")


def test_create_no_parent():
    """create-pages with no parent → ask"""
    result = run_hook(
        "pretooluse.py",
        {
            "tool_name": "mcp__plugin_Notion_notion__notion-create-pages",
            "tool_input": {},
        },
    )
    assert is_ask(result), f"Expected ask, got {result}"
    print("PASS: create with no parent → ask")


def test_posttooluse_fetch_caches():
    """PostToolUse fetch with ancestor-path → cache populated"""
    cleanup_cache()
    fetched_id = "abcdef1234567890abcdef1234567890"
    ancestor_in_path = "1111111111111111111111111111111a"
    run_hook(
        "posttooluse.py",
        {
            "tool_name": "mcp__plugin_Notion_notion__notion-fetch",
            "tool_input": {"page_id": fetched_id},
            "tool_result": (
                f"<ancestor-path>"
                f"3190f22f7b6e80188099e1454419dfec > {ancestor_in_path} > {fetched_id}"
                f"</ancestor-path>"
            ),
        },
    )
    with open(TEST_CACHE) as f:
        cache = json.load(f)
    assert fetched_id in cache, f"Fetched ID not in cache: {cache}"
    assert ancestor_in_path in cache, f"Ancestor ID not in cache: {cache}"
    print("PASS: PostToolUse fetch populates cache")


def test_update_cached_page():
    """update-page with cached page ID → allow"""
    result = run_hook(
        "pretooluse.py",
        {
            "tool_name": "mcp__plugin_Notion_notion__notion-update-page",
            "tool_input": {"page_id": "abcdef1234567890abcdef1234567890"},
        },
    )
    assert is_allow(result), f"Expected allow, got {result}"
    print("PASS: update cached page → allow")


def test_update_uncached_page():
    """update-page with uncached page ID → ask"""
    result = run_hook(
        "pretooluse.py",
        {
            "tool_name": "mcp__plugin_Notion_notion__notion-update-page",
            "tool_input": {"page_id": "ffffffffffffffffffffffffffffffff"},
        },
    )
    assert is_ask(result), f"Expected ask, got {result}"
    print("PASS: update uncached page → ask")


def test_id_normalization():
    """Dashed ID resolves same as undashed"""
    result = run_hook(
        "pretooluse.py",
        {
            "tool_name": "mcp__plugin_Notion_notion__notion-create-pages",
            "tool_input": {
                "parent": {"page_id": "3190f22f-7b6e-8018-8099-e1454419dfec"}
            },
        },
    )
    assert is_allow(result), f"Expected allow for dashed ID, got {result}"
    print("PASS: dashed ID normalization works")


def test_corrupted_cache():
    """Corrupted cache → graceful fallback"""
    with open(TEST_CACHE, "w") as f:
        f.write("NOT JSON{{{")
    result = run_hook(
        "pretooluse.py",
        {
            "tool_name": "mcp__plugin_Notion_notion__notion-update-page",
            "tool_input": {"page_id": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"},
        },
    )
    assert is_ask(result), f"Expected ask with corrupted cache, got {result}"
    print("PASS: corrupted cache → graceful fallback")


def test_update_root_page():
    """update-page targeting root page → allow"""
    result = run_hook(
        "pretooluse.py",
        {
            "tool_name": "mcp__plugin_Notion_notion__notion-update-page",
            "tool_input": {"page_id": "3190f22f7b6e80188099e1454419dfec"},
        },
    )
    assert is_allow(result), f"Expected allow for root page, got {result}"
    print("PASS: update root page → allow")


def test_data_source_tool():
    """update-data-source with known ID → allow"""
    result = run_hook(
        "pretooluse.py",
        {
            "tool_name": "mcp__plugin_Notion_notion__notion-update-data-source",
            "tool_input": {
                "data_source_id": "1a90f22f-7b6e-80e8-9bcb-cc6c5e49cdae"
            },
        },
    )
    assert is_allow(result), f"Expected allow for known data source, got {result}"
    print("PASS: update known data source → allow")


def test_view_tool_known_db():
    """create-view with known database → allow"""
    result = run_hook(
        "pretooluse.py",
        {
            "tool_name": "mcp__plugin_Notion_notion__notion-create-view",
            "tool_input": {
                "database_id": "3190f22f7b6e8012b3b1c1c3e2b48e0f"
            },
        },
    )
    assert is_allow(result), f"Expected allow for known db view, got {result}"
    print("PASS: create view with known database → allow")


def test_posttooluse_create_caches():
    """PostToolUse create-pages with workspace parent → new IDs cached"""
    cleanup_cache()
    new_page_id = "deadbeef12345678deadbeef12345678"
    run_hook(
        "posttooluse.py",
        {
            "tool_name": "mcp__plugin_Notion_notion__notion-create-pages",
            "tool_input": {
                "parent": {"database_id": "3190f22f7b6e8012b3b1c1c3e2b48e0f"}
            },
            "tool_result": f"Created page https://notion.so/{new_page_id}",
        },
    )
    with open(TEST_CACHE) as f:
        cache = json.load(f)
    assert new_page_id in cache, f"New page ID not in cache: {cache}"
    print("PASS: PostToolUse create-pages caches new IDs")


if __name__ == "__main__":
    tests = [
        test_create_known_parent,
        test_create_unknown_parent,
        test_create_no_parent,
        test_posttooluse_fetch_caches,
        test_update_cached_page,
        test_update_uncached_page,
        test_id_normalization,
        test_corrupted_cache,
        test_update_root_page,
        test_data_source_tool,
        test_view_tool_known_db,
        test_posttooluse_create_caches,
    ]

    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"FAIL: {test.__name__}: {e}")
            failed += 1

    cleanup_cache()
    print(f"\n{passed}/{passed + failed} tests passed")
    if failed:
        sys.exit(1)
