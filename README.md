# Claude Code Personal Configuration

Personal Claude Code configuration synced across machines via git and symlinks.

## Repository Contents

- **CLAUDE.md** - Personal development guidelines and coding standards
- **commands/** - Custom slash commands
- **skills/** - Custom skill definitions
- **statusline-command.sh** - Custom status line script (shows cwd, git info, context used %, model)
- **hooks/** - Permission hooks (e.g., Notion workspace gate)
- **.gitignore** - Excludes runtime/cache files

## Setup on New Machine

### Prerequisites

- Claude Code installed
- Git configured
- GitHub CLI authenticated (`gh auth login`)
- (Optional but recommended) claude-code-transcripts for readable session exports: `uv tool install claude-code-transcripts`
- (Optional but recommended) [claude-frecency](https://github.com/murphy-osmo/claude-frecency) for frecency-based `@file` suggestions

### Installation Steps

```bash
# 1. Clone this repository
cd ~
git clone https://github.com/jonah-osmo/claude-config.git

# 2. Create symlinks from ~/.claude/ to the repo
ln -s ~/claude-config/CLAUDE.md ~/.claude/CLAUDE.md
ln -s ~/claude-config/commands ~/.claude/commands
ln -s ~/claude-config/skills ~/.claude/skills
ln -s ~/claude-config/statusline-command.sh ~/.claude/statusline-command.sh

# 3. Verify symlinks
ls -la ~/.claude/ | grep -E '(CLAUDE.md|commands|skills|statusline)'

# 4. (Optional) Install claude-frecency for better @file suggestions
git clone https://github.com/murphy-osmo/claude-frecency.git ~/.claude/claude-frecency

# 5. Restart Claude Code or start a new session
```

### Verification

After setup, verify Claude Code loads your configuration:
1. Start a new Claude Code session
2. Check that personal guidelines are being followed
3. Verify custom commands and skills are available

## Syncing Changes

### Pulling Latest Changes

```bash
cd ~/claude-config
git pull
```

That's it! Since `~/.claude/` uses symlinks, changes are immediately available.

### Committing Local Changes

If you modify configuration on one machine:

```bash
cd ~/claude-config
git add -A
git commit -m "Description of changes"
git push
```

Then pull on other machines:

```bash
cd ~/claude-config
git pull
```

## What's Version Controlled

**Tracked in git:**
- Personal development guidelines (CLAUDE.md)
- Custom commands (commands/*.md)
- Custom skills (skills/*.md)
- Status line script (statusline-command.sh)

**NOT tracked (runtime files remain in ~/.claude/):**
- `.credentials.json` - Authentication tokens
- `history.jsonl` - Command history
- `projects/` - Per-project session data
- `debug/`, `todos/`, `shell-snapshots/`, `file-history/`, `statsig/`, `ide/` - Runtime directories

## Architecture Benefits

This approach provides:
1. **Simple sync** - Just `git pull` to update
2. **Clean separation** - Configuration in git, runtime files stay local
3. **Cross-machine portability** - Works on any machine with Claude Code
4. **Version history** - Track changes to your configuration over time
5. **No NAS issues** - Local filesystem, no file locking problems

## Troubleshooting

### Symlinks Not Working

Check symlinks exist:
```bash
ls -la ~/.claude/ | grep -E '(CLAUDE.md|commands|skills|statusline)'
```

Should show entries like:
```
lrwxrwxrwx ... CLAUDE.md -> /home/jonah/claude-config/CLAUDE.md
lrwxrwxrwx ... commands -> /home/jonah/claude-config/commands
lrwxrwxrwx ... skills -> /home/jonah/claude-config/skills
lrwxrwxrwx ... statusline-command.sh -> /home/jonah/claude-config/statusline-command.sh
```

### Configuration Not Loading

1. Verify symlinks point to correct locations
2. Check file permissions are readable
3. Restart Claude Code session
4. Run `claude doctor` to check installation health

### Merge Conflicts

If you modify configuration on multiple machines simultaneously:
```bash
cd ~/claude-config
git pull  # Will show conflicts
# Resolve conflicts in your editor
git add -A
git commit -m "Resolve merge conflict"
git push
```

## Claude Frecency

[claude-frecency](https://github.com/murphy-osmo/claude-frecency) provides frecency-ranked file suggestions when using `@file` in Claude Code. It tracks file access patterns and suggests files based on frequency + recency.

After cloning (see Installation Steps above), add the following to `~/.claude/settings.json`:

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "matcher": "",
        "hooks": [{"type": "command", "command": "python3 ~/.claude/claude-frecency/frecency_track.py"}]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Write|Edit|Bash",
        "hooks": [{"type": "command", "command": "python3 ~/.claude/claude-frecency/frecency_track.py"}]
      }
    ]
  },
  "fileSuggestion": {
    "type": "command",
    "command": "python3 ~/.claude/claude-frecency/file_suggestion.py"
  }
}
```

## Notion Workspace Permission Hooks

Auto-allows Notion writes within the "CLAUDE [Jonah]" workspace and prompts for confirmation (with a reason message) on writes outside it.

### How it works

- **PreToolUse**: Checks the target page ID against `ALLOWED_PARENT_IDS` and a local cache. If the page is in the workspace → auto-allow. If not → prompt with a message explaining the page is outside the workspace.
- **PostToolUse**: Intended to populate the cache from `notion-fetch` results, but Claude Code does not pass `tool_result` content for MCP tools. **The cache must be manually seeded** (see below).

### Prerequisites

```bash
pip install filelock
```

### Hook Registration

Add the following entries to `~/.claude/settings.json` under `"hooks"`. Merge into existing hook arrays — don't replace them.

**PreToolUse** — permission gate for Notion write tools:
```json
{
  "matcher": "mcp__plugin_Notion_notion__notion-(create-pages|update-page|move-pages|duplicate-page|create-comment|create-database|update-data-source|update-view|create-view)",
  "hooks": [
    {
      "type": "command",
      "command": "python3 ~/claude-config/hooks/notion-workspace-gate/pretooluse.py",
      "timeout": 5
    }
  ]
}
```

**PostToolUse** — cache populator (passive; currently no-ops due to MCP tool result limitation):
```json
{
  "matcher": "mcp__plugin_Notion_notion__notion-(fetch|create-pages|create-database)",
  "hooks": [
    {
      "type": "command",
      "command": "python3 ~/claude-config/hooks/notion-workspace-gate/posttooluse.py",
      "timeout": 5
    }
  ]
}
```

### Seeding the cache

Pages within the workspace that are not in `ALLOWED_PARENT_IDS` need to be added to `~/.claude/notion-workspace-cache.json` manually. The cache maps normalized page IDs (no dashes, lowercase) to the root page ID:

```python
import json

ROOT = "3190f22f7b6e80188099e1454419dfec"  # CLAUDE [Jonah]
cache = {
    "3190f22f7b6e806cbe36000b0c4091ac": ROOT,  # Document Hub data source
    "3190f22f7b6e80be8065ea5656df56b2": ROOT,  # Document Hub database
    "3220f22f7b6e8130a2a8ee7bd7f0433e": ROOT,  # e.g. a specific page
    # add more as needed
}
with open("~/.claude/notion-workspace-cache.json", "w") as f:
    json.dump(cache, f)
```

### Notes

- Allowed parent IDs (auto-allowed without cache lookup) are in `hooks/notion-workspace-gate/config.py`
- The `hookEventName: "PreToolUse"` field is required in the hook output — without it Claude Code treats the response as an error and falls through to allow
- The `permissionDecision` values are `"allow"`, `"ask"`, and `"deny"`. Use `"ask"` for a prompt-with-reason (overridable); `"deny"` for a hard block

## Recommended Plugins

Install via `/plugins` command in Claude Code:

- **code-review** - Code review capabilities
- **code-simplifier** - Simplify and refine code
- **pr-review-toolkit** - Comprehensive PR review agents
- **pyright-lsp** - Python type checking via Pyright
- **context7** - Up-to-date library documentation lookup
- **hookify** - Create hooks to prevent unwanted behaviors

## Custom Commands

- **/transcript** - Upload current session to GitHub Gist (requires `claude-code-transcripts`)

