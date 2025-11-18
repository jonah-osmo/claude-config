# Claude Code Skills for Osmo Development

This directory contains custom Claude Code skills designed to streamline development workflows based on real refactoring and testing experiences.

## Available Skills

### 1. Python Module Refactoring (`python-module-refactoring/`)

Safely split large Python files into focused modules while preserving functionality.

**Key features**:
- Automatic import dependency analysis
- BUILD.bazel updates
- Test import migration
- Backward compatibility via __init__.py
- Static analysis verification

**Use when**: Refactoring monolithic Python files, splitting modules, reorganizing packages

**Created from**: Experience refactoring interactivity.py (2,359 lines → 5 focused modules)

---

### 2. Bazel Dependency Validator (`bazel-dependency-validator/`)

Validate that BUILD.bazel dependencies match actual Python imports.

**Key features**:
- Import scanning from Python files
- Dependency mapping to Bazel syntax
- Missing dependency detection
- Fix suggestions with exact syntax

**Use when**: BUILD.bazel tests fail, after refactoring, creating new BUILD files

**Created from**: Missing plotly, gcs_utils, and sls_ilp_match dependency issues

---

### 3. Test Regression Analyzer (`test-regression-analyzer/`)

Compare test results before/after changes to identify regressions.

**Key features**:
- Baseline vs current test comparison
- Categorization (newly failing, newly passing, still failing, still passing)
- Root cause analysis for new failures
- Comprehensive reports with log excerpts

**Use when**: Validating refactoring, investigating test failures, comparing test results

**Created from**: Validating that refactoring didn't introduce new test failures

---

### 4. Semantic Git Commit Grouper (`semantic-git-commit-grouper/`)

Intelligently group git changes into logical, semantic commits.

**Key features**:
- Change analysis and categorization
- Semantic grouping by purpose
- Descriptive commit message generation
- Selective staging guidance

**Use when**: Committing multiple changes, organizing commits, preparing clean git history

**Created from**: Need to commit refactoring separately from unrelated gcms_library_api changes

---

### 5. CLI Migration Assistant (`cli-migration-assistant/`)

Migrate argparse CLIs to Click framework with advanced type support.

**Key features**:
- Migrates argparse to Click
- Supports complex types (comma-separated lists, nested dicts)
- Type inference from config schema
- Backwards compatibility with hyphen/underscore variants
- Dot notation for nested parameters

**Use when**: Converting argparse to Click, adding list/dict CLI parameters, improving CLI UX

**Created from**: Migrating gcms_library_api from argparse to Click with complex parameter types

---

### 6. Configuration Refactoring Expert (`configuration-refactoring-expert/`)

Transform rigid configuration systems into flexible, validated, override-capable systems.

**Key features**:
- Identifies hardcoded values and config rigidity
- Implements override hierarchy (CLI > env vars > config file > defaults)
- Type-safe config schemas (dataclasses/Pydantic)
- Environment variable support
- Validation with clear error messages

**Use when**: Config parameters are hardcoded, need CLI/env overrides, deploying to multiple environments

**Created from**: Need to override machine_filter and other hardcoded params at runtime

---

### 7. Test Suite Generator (`test-suite-generator/`)

Auto-generate comprehensive pytest test suites for Python modules.

**Key features**:
- Generates 60+ tests covering happy path, edge cases, errors, integration
- Follows project patterns (fixtures, parametrize, mocking)
- Organizes tests by functionality
- Achieves >90% code coverage
- Auto-updates BUILD.bazel with test targets

**Use when**: Writing tests for new code, improving test coverage, regression testing after refactoring

**Created from**: Need for comprehensive test coverage following Click CLI migration

---

### 8. Tiered Architecture Validator (`tiered-architecture-validator/`)

Validate Tiered Clean Architecture compliance for Python modules.

**Key features**:
- Validates tier dependencies (unidirectional flow)
- Checks function classification (A/B/C/D types)
- Verifies file organization and structure
- Validates CLAUDE.md compliance
- Reports violations with fix suggestions

**Use when**: Implementing new modules, reviewing PRs, checking architecture compliance, fixing tier violations

**Created from**: Need to enforce consistent architecture across research and production modules

---

## Installation

### Personal Skills (Recommended for Experimentation)

Install to `~/.claude/skills/` for personal use across all projects:

```bash
# Create skills directory if it doesn't exist
mkdir -p ~/.claude/skills/

# Copy desired skill(s)
cp -r /home/jonah/osmo/src/sandbox/jonah/notes/claude/skills/python-module-refactoring ~/.claude/skills/
cp -r /home/jonah/osmo/src/sandbox/jonah/notes/claude/skills/bazel-dependency-validator ~/.claude/skills/
cp -r /home/jonah/osmo/src/sandbox/jonah/notes/claude/skills/test-regression-analyzer ~/.claude/skills/
cp -r /home/jonah/osmo/src/sandbox/jonah/notes/claude/skills/semantic-git-commit-grouper ~/.claude/skills/
cp -r /home/jonah/osmo/src/sandbox/jonah/notes/claude/skills/cli-migration-assistant ~/.claude/skills/
cp -r /home/jonah/osmo/src/sandbox/jonah/notes/claude/skills/configuration-refactoring-expert ~/.claude/skills/
cp -r /home/jonah/osmo/src/sandbox/jonah/notes/claude/skills/test-suite-generator ~/.claude/skills/
cp -r /home/jonah/osmo/src/sandbox/jonah/notes/claude/skills/tiered-architecture-validator ~/.claude/skills/

# Restart Claude Code to load the skills
```

### Project Skills (Recommended for Team Use)

Install to `.claude/skills/` in project root to share with team via git:

```bash
# From osmo repo root
mkdir -p .claude/skills/

# Copy desired skill(s)
cp -r src/sandbox/jonah/notes/claude/skills/python-module-refactoring .claude/skills/
cp -r src/sandbox/jonah/notes/claude/skills/bazel-dependency-validator .claude/skills/
cp -r src/sandbox/jonah/notes/claude/skills/test-regression-analyzer .claude/skills/
cp -r src/sandbox/jonah/notes/claude/skills/semantic-git-commit-grouper .claude/skills/
cp -r src/sandbox/jonah/notes/claude/skills/cli-migration-assistant .claude/skills/
cp -r src/sandbox/jonah/notes/claude/skills/configuration-refactoring-expert .claude/skills/
cp -r src/sandbox/jonah/notes/claude/skills/test-suite-generator .claude/skills/
cp -r src/sandbox/jonah/notes/claude/skills/tiered-architecture-validator .claude/skills/

# Add to git
git add .claude/skills/
git commit -m "Add Claude Code skills for development workflows"
```

## Usage

Skills are **model-invoked** - Claude automatically activates them based on context and descriptions. You don't need to call them explicitly.

### Examples

**Automatic activation**:
```
You: "I need to split this large Python file into smaller modules"
→ Claude activates python-module-refactoring skill

You: "My Bazel tests are failing with import errors"
→ Claude activates bazel-dependency-validator skill

You: "Did my refactoring break any tests?"
→ Claude activates test-regression-analyzer skill

You: "I have a bunch of changes to commit"
→ Claude activates semantic-git-commit-grouper skill

You: "Migrate this argparse CLI to Click"
→ Claude activates cli-migration-assistant skill

You: "I need to override this hardcoded config parameter"
→ Claude activates configuration-refactoring-expert skill

You: "Generate comprehensive tests for this module"
→ Claude activates test-suite-generator skill

You: "Check if this code follows our tiered architecture"
→ Claude activates tiered-architecture-validator skill
```

### Debugging

If a skill doesn't activate when expected:

```bash
# Run Claude Code with debug flag
claude --debug

# Check skill descriptions match your query
# Improve description specificity if needed
```

## Skill Descriptions (for Discovery)

Claude uses these descriptions to decide when to activate skills. They're optimized for the queries we commonly make:

| Skill | Trigger Keywords |
|-------|------------------|
| python-module-refactoring | "refactor", "split module", "reorganize", "extract to separate file" |
| bazel-dependency-validator | "bazel dependencies", "BUILD.bazel", "import error", "missing dependency" |
| test-regression-analyzer | "test regression", "which tests broke", "compare tests", "test diff" |
| semantic-git-commit-grouper | "commit", "group changes", "organize commits", "semantic commits" |
| cli-migration-assistant | "migrate to click", "convert argparse", "CLI refactor", "list support", "nested dict arguments" |
| configuration-refactoring-expert | "make config flexible", "add CLI overrides", "refactor configuration", "config too rigid", "runtime overrides" |
| test-suite-generator | "generate tests", "write test suite", "comprehensive tests", "add test coverage", "test this code" |
| tiered-architecture-validator | "check architecture", "validate tiers", "verify dependencies", "tier violations", "check compliance" |

## Maintenance

### Updating Skills

Edit the `SKILL.md` file directly:

```bash
# Edit skill
vim ~/.claude/skills/python-module-refactoring/SKILL.md

# Restart Claude Code to reload
```

### Adding Supporting Files

Skills can have supporting documentation, scripts, and templates:

```
skill-name/
├── SKILL.md (required)
├── reference.md (optional documentation)
├── examples.md (optional examples)
├── scripts/
│   └── helper.py (optional utility)
└── templates/
    └── template.txt (optional template)
```

Claude progressively loads supporting files only when needed.

### Version Tracking

Each skill has a "Version History" section at the end of SKILL.md. Update it when making changes:

```markdown
## Version History

- v1.1 (2025-11-20): Added support for pytest output parsing
- v1.0 (2025-11-18): Initial skill creation
```

## Best Practices

1. **Keep skills focused**: One capability per skill
2. **Write specific descriptions**: Include concrete trigger words
3. **Test with team members**: Verify activation works as expected
4. **Update based on usage**: Improve based on real-world use
5. **Document learnings**: Add to skill based on new patterns

## Future Skills to Consider

Based on our development patterns, consider creating:

- **Bazel Build Optimizer**: Analyze and optimize BUILD.bazel structure for better caching
- **Import Organizer**: Auto-organize and sort Python imports (isort/ruff integration)
- **Documentation Generator**: Generate docstrings from code and type hints
- **Code Review Checklist**: Automated pre-commit checks and PR validation
- **Data Pipeline Builder**: Generate ETL pipelines following tiered architecture
- **API Schema Generator**: Generate gRPC/REST API schemas from Python types

## Feedback and Improvements

These skills were created based on real refactoring challenges. As you use them:

1. **Note what works well** - reinforce successful patterns
2. **Identify gaps** - what should be added?
3. **Update descriptions** - improve activation accuracy
4. **Share learnings** - update this README

## References

- [Claude Code Skills Documentation](https://code.claude.com/docs/en/skills)
- [Git Commit Conventions](https://www.conventionalcommits.org/)
- [Bazel Python Rules](https://github.com/aspect-build/rules_py)

---

**Created**: 2025-11-18
**Last Updated**: 2025-11-18 (Added 4 new skills: CLI Migration, Configuration Refactoring, Test Suite Generator, Tiered Architecture Validator)
**Author**: Jonah (with Claude Code assistance)
