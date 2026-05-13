# Personal Development Guidelines

*Personal preferences for LLM agents working across all projects.*

## worktrunk (wt)

Git worktree manager for branch-based development. Worktrees are stored at `~/w/<branch-name>` (`~/w` → platform-specific: `~/code/_worktrees` on macOS, `/mnt/metropolitan/jonah/code/_worktrees` on Linux).

### Common Commands

```bash
wt switch --create <branch>                # Create worktree from default branch
wt switch --create <branch> --base <ref>   # Create worktree from specific branch
wt switch <branch>                         # Switch to existing worktree
wt list                                    # List all worktrees
wt merge                                   # Squash-merge current branch to main, cleanup
wt remove                                  # Remove current worktree
```

### Workflow

1. `wt switch --create feature-x` - creates worktree, switches to it
2. Make changes, commit as usual
3. `wt merge` - squashes commits, merges to main, removes worktree

Config: `~/.config/worktrunk/config.toml`. A `post-create` hook runs `direnv allow .` on each new worktree so repos with an `.envrc` (e.g. osmo) load secrets automatically on first entry instead of blocking with "direnv: error .envrc is blocked".

## Coding Standards
- **Always use absolute imports**: Never use relative imports
- **Prioritize brevity**: Use clear naming over excessive comments
- **No unnecessary documentation**: Only add comments when specifically requested

## Function Classification System

| Class | Purpose | Typing | Docstring | Tests | Naming |
|-------|---------|--------|-----------|-------|--------|
| **A: Public External** | Called from outside module | Full | Detailed | Required | Clean, e.g. `predict_molecules` |
| **B: Public Internal** | Called within module | Full | Basic | Required | Descriptive, e.g. `predict_molecules_by_consensus` |
| **C: Private Module** | Internal helpers | Optional | Simple | Encouraged | Underscore prefix, e.g. `_predict_internal` |
| **D: Private Sub-Module** | Sub-module helpers | Optional | Optional | Optional | Underscore prefix, short, e.g. `_calc` |

## Required Development Workflow

When implementing new code:

1. **Plan architecture**: Identify modules, assign tiers, verify dependencies
2. **Design functions**: Define inputs/outputs, classify (A-D), write docstrings
3. **Create structure**: Create files, import submodules, implement skeletons
4. **Document**: Add purpose, tier level, dependencies to each file

## Module Architecture: Tiered Clean Architecture

ML pipeline architecture enforcing strict dependency rules for modularity.

### Principles
1. **Unidirectional Dependencies**: Higher tiers → lower tiers only
2. **Tier Isolation**: Same-tier modules cannot depend on each other
3. **Core Independence**: T0 has no internal dependencies
4. **Testability**: Mock dependencies for independent testing

### Tier Summary

| Tier | Modules | Purpose |
|------|---------|---------|
| **T0** | structs, algorithms, config, utils | Pure domain logic, no dependencies |
| **T1** | dataloaders, plotting, *_api | Application services using T0 |
| **T2** | train_fit, inference, evaluate | Orchestration combining T0+T1 |
| **T3** | experiment, etl, tests, notebooks | External interfaces, highest level |

### Standard Structure

```
src/mypkg/
  structs.py           # T0: Dataclasses, types
  algorithms.py        # T0: Pure functions
  config.py            # T0: Config schema + loader
  utils.py             # T0: Small helpers
  dataloaders.py       # T1: GCS/BQ I/O
  plotting.py          # T1: Visualizations
  train_api.py         # T1: Training interface
  infer_api.py         # T1: Inference interface
  eval_api.py          # T1: Evaluation interface
  train_fit.py         # T2: Training orchestration
  inference.py         # T2: Inference orchestration
  evaluate.py          # T2: Evaluation orchestration
  experiment.py        # T3: End-to-end workflows
  etl/                 # T3: Data pipelines
  tests/               # T3: Tests
  notebooks/           # T3: Analysis
```

**Rules**:
- Prefer files over directories (unless >3000 lines)
- Always make `etl/`, `tests/`, `notebooks/` directories
- Each subdirectory gets its own CLAUDE.md

## Notion

- **Default workspace**: Always write to the "CLAUDE [Jonah]" page and its subpages/sub-databases only
- **Never** create or modify pages outside "CLAUDE [Jonah]" unless explicitly instructed
- When creating new pages or database entries, place them under "CLAUDE [Jonah]" or one of its existing sub-databases
- **Workspace details**: See the `notion-workspace` skill for database IDs, schemas, and routing rules

## Secrets / API Keys

- **Storage**: `~/.creds/<NAME>.txt`, one file per secret, dir `700`, files `600`.
- **Filename = env var name + `.txt`** (e.g., `OPENAI_API_KEY.txt` → `$OPENAI_API_KEY`).
- **Project-scoped keys**: suffix the env var name (`OPENAI_API_KEY_DEFORMULATION.txt`).
- **Loading**: env vars only; never read `~/.creds/*.txt` from Python or pass keys as function args. In the osmo repo, `.envrc` + `tools/load_cred` does this via `direnv`.
- **Full convention**: Notion page "Secrets / API Keys — Official Pattern" under "CLAUDE [Jonah]" (https://www.notion.so/35f0f22f7b6e81cfa370e60aaf5979d9).

## CLAUDE.md File Management

- **File naming**: Use `CLAUDE.md` (check for existing on case-sensitive filesystems)
- **One per directory**: Don't duplicate
- **Keep brief**: Push details to subdirectory CLAUDE.md files
- **Avoid redundancy**: Don't duplicate info available elsewhere
