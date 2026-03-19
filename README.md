# Claude Code Personal Configuration

Personal Claude Code configuration synced across machines via git and symlinks.

## Repository Contents

- **CLAUDE.md** - Personal development guidelines and coding standards
- **agents/** - Custom agent definitions (11 specialized agents)
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
ln -s ~/claude-config/agents ~/.claude/agents
ln -s ~/claude-config/commands ~/.claude/commands
ln -s ~/claude-config/skills ~/.claude/skills
ln -s ~/claude-config/statusline-command.sh ~/.claude/statusline-command.sh

# 3. Verify symlinks
ls -la ~/.claude/ | grep -E '(CLAUDE.md|agents|commands|skills|statusline)'

# 4. (Optional) Install claude-frecency for better @file suggestions
git clone https://github.com/murphy-osmo/claude-frecency.git ~/.claude/claude-frecency

# 5. Restart Claude Code or start a new session
```

### Verification

After setup, verify Claude Code loads your configuration:
1. Start a new Claude Code session
2. Check that personal guidelines are being followed
3. Verify custom agents are available (if configured)

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
- Custom agents (agents/*.md)
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
ls -la ~/.claude/ | grep -E '(CLAUDE.md|agents|commands|skills|statusline)'
```

Should show entries like:
```
lrwxrwxrwx ... CLAUDE.md -> /home/jonah/claude-config/CLAUDE.md
lrwxrwxrwx ... agents -> /home/jonah/claude-config/agents
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

Auto-allows Notion writes within the "CLAUDE [Jonah]" workspace and asks for confirmation on writes outside it. A PostToolUse hook caches page ancestry from `notion-fetch` results so subsequent writes to known pages are auto-allowed.

### Prerequisites

```bash
pip install filelock
```

### Hook Registration

Add the following entries to `~/.claude/settings.json` under `"hooks"`. Merge these into existing hook arrays — don't replace them.

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

**PostToolUse** — cache populator from fetch/create results:
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

### Notes

- The workspace cache (`~/.claude/notion-workspace-cache.json`) is auto-created at runtime — no manual setup needed
- Allowed parent IDs are configured in `hooks/notion-workspace-gate/config.py`

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

## Custom Agents

This repository includes 11 custom agents:
- claude-md-compliance-checker
- code-quality-pragmatist
- dashboard-builder
- data-researcher
- functional-validator
- gcms-ml-engineer
- gcms-pipeline-engineer
- git-workflow-manager
- reality-checker
- spec-validator
- ultrathink-debugger

See individual agent files in `agents/` for descriptions and usage.
