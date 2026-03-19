import json
import os
import tempfile

from filelock import FileLock

ROOT_PAGE_ID = "3190f22f7b6e80188099e1454419dfec"

ALLOWED_PARENT_IDS = {
    "3190f22f7b6e80188099e1454419dfec",  # Root: CLAUDE [Jonah]
    "3190f22f7b6e8012b3b1c1c3e2b48e0f",  # Database: Tasks Tracker
    "3190f22f7b6e80df89f0dc24e09d7f00",  # Database: Documents
    "1a90f22f7b6e80e89bcbcc6c5e49cdae",  # Data source: Tasks Tracker
    "1a90f22f7b6e80178e3ac89c57032ce9",  # Data source: Documents
}

CREATE_TOOLS = {
    "mcp__plugin_Notion_notion__notion-create-pages",
    "mcp__plugin_Notion_notion__notion-move-pages",
    "mcp__plugin_Notion_notion__notion-create-database",
}

UPDATE_TOOLS = {
    "mcp__plugin_Notion_notion__notion-update-page",
    "mcp__plugin_Notion_notion__notion-duplicate-page",
    "mcp__plugin_Notion_notion__notion-create-comment",
}

DATA_SOURCE_TOOLS = {
    "mcp__plugin_Notion_notion__notion-update-data-source",
}

VIEW_TOOLS = {
    "mcp__plugin_Notion_notion__notion-update-view",
    "mcp__plugin_Notion_notion__notion-create-view",
}

CACHE_FILE = os.environ.get(
    "_TEST_CACHE_OVERRIDE",
    os.path.expanduser("~/.claude/notion-workspace-cache.json"),
)
LOCK_FILE = CACHE_FILE + ".lock"
MAX_CACHE_ENTRIES = 1000


def normalize_id(page_id: str) -> str:
    return page_id.replace("-", "").lower()


def load_cache() -> dict:
    try:
        with open(CACHE_FILE) as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        pass
    return {}


def save_cache(cache: dict) -> None:
    if len(cache) > MAX_CACHE_ENTRIES:
        items = list(cache.items())
        cache = dict(items[-MAX_CACHE_ENTRIES:])

    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    lock = FileLock(LOCK_FILE)
    with lock:
        fd, tmp_path = tempfile.mkstemp(
            dir=os.path.dirname(CACHE_FILE), suffix=".tmp"
        )
        try:
            with os.fdopen(fd, "w") as f:
                json.dump(cache, f)
            os.replace(tmp_path, CACHE_FILE)
        except Exception:
            os.unlink(tmp_path)
            raise
