---
name: using-git-worktrees
description: Use when starting feature work that needs isolation from current workspace — creates isolated git worktrees using the `wt` CLI
autoInvoke: true
---

# Git Worktrees with `wt` (worktrunk)

**Always use `wt`** — never raw `git worktree` commands. The `wt` CLI handles worktree paths, directory structure, and cleanup automatically.

## Commands

| Command | Purpose |
|---------|---------|
| `wt switch --create <branch>` | Create worktree from default branch |
| `wt switch --create <branch> --base <ref>` | Create worktree from a specific branch |
| `wt switch <branch>` | Switch to an existing worktree |
| `wt list` | List all worktrees |
| `wt merge` | Squash-merge current branch to main, cleanup |
| `wt remove` | Remove current worktree |

## Creating a Worktree

**From default branch (main):**
```bash
wt switch --create feature-x
```

**From the current branch** (use `--base`):
```bash
wt switch --create feature-x --base jonah/dev-2026-march
```

Always specify `--base` when you intend to branch from something other than main.

## Working Directory

After `wt switch`, the worktree is created at a path managed by worktrunk (configured in `~/.config/worktrunk/config.toml`). Claude Code cannot `cd` persistently, so:

1. Capture the worktree path from `wt switch` output
2. Prefix all commands with `cd <worktree-path> && <command>`

## What NOT to Do

- **No raw `git worktree add/remove`** — use `wt` commands
- **No directory selection / gitignore steps** — `wt` handles paths automatically
- **No project setup** — bazel handles deps, conda env is shared across worktrees
- **No `wt new`** — this subcommand does not exist; use `wt switch --create`

## Checklist

- [ ] Announce worktree creation and target branch at start
- [ ] Use `wt switch --create` with `--base` when branching from non-default
- [ ] Report worktree location after creation
- [ ] Verify tests pass before considering work complete
