# Claude Code Personal Configuration

Personal Claude Code configuration synced across machines via git and symlinks.

## Repository Contents

- **CLAUDE.md** - Personal development guidelines and coding standards
- **agents/** - Custom agent definitions (11 specialized agents)
- **skills/** - Custom skill definitions
- **.gitignore** - Excludes runtime/cache files

## Setup on New Machine

### Prerequisites

- Claude Code installed
- Git configured
- GitHub CLI authenticated (`gh auth login`)
- (Optional but recommended) claude-code-transcripts for readable session exports: `uv tool install claude-code-transcripts`

### Installation Steps

```bash
# 1. Clone this repository
cd ~
git clone https://github.com/jonah-osmo/claude-config.git

# 2. Create symlinks from ~/.claude/ to the repo
ln -s ~/claude-config/CLAUDE.md ~/.claude/CLAUDE.md
ln -s ~/claude-config/agents ~/.claude/agents
ln -s ~/claude-config/skills ~/.claude/skills

# 3. Verify symlinks
ls -la ~/.claude/ | grep -E '(CLAUDE.md|agents|skills)'

# 4. Restart Claude Code or start a new session
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
- Custom skills (skills/*.md)

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
ls -la ~/.claude/ | grep -E '(CLAUDE.md|agents|skills)'
```

Should show entries like:
```
lrwxrwxrwx ... CLAUDE.md -> /home/jonah/claude-config/CLAUDE.md
lrwxrwxrwx ... agents -> /home/jonah/claude-config/agents
lrwxrwxrwx ... skills -> /home/jonah/claude-config/skills
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
