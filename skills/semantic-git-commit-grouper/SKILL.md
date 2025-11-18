---
name: semantic-git-commit-grouper
description: Intelligently group git changes into semantic commits based on purpose (refactor, feature, bugfix, docs). Analyzes git status and diffs to suggest logical commit groupings with descriptive messages. Use when preparing to commit multiple changes, when user has many unstaged files, when user mentions "commit", "group changes", or "organize commits", or when encountering GitHub permission/authentication errors during git operations.
allowed-tools: Bash, Read, Grep, WebFetch
---

# Semantic Git Commit Grouper Skill

Organize git changes into logical, semantic commits rather than one monolithic commit.

## Core Capabilities

1. **Change Analysis**: Scan `git status` and `git diff` to understand modifications
2. **Semantic Grouping**: Categorize changes by purpose and relationship
3. **Commit Planning**: Suggest logical commit groups with rationale
4. **Message Generation**: Create descriptive commit messages following conventions
5. **Selective Staging**: Guide user through staging each group separately

## When to Use This Skill

Activate when:
- User has many modified/new files and wants to commit
- Preparing commits after a coding session
- User mentions "commit changes", "organize commits", "group changes"
- Multiple unrelated changes exist in working directory
- User wants clean, semantic git history

## Workflow

### Phase 1: Assess Current State

1. **Run git status**:
   ```bash
   git status
   ```

2. **Categorize files**:
   - **Modified**: Changed existing files
   - **New**: Untracked files
   - **Deleted**: Removed files
   - **Renamed**: Moved files (git may detect automatically)

3. **Run git diff** for each modified file to understand changes:
   ```bash
   git diff path/to/file
   ```

4. **Read new files** to understand their purpose

### Phase 2: Identify Change Patterns

Analyze changes to identify:

**By Change Type**:
- **Refactoring**: Code reorganization, no behavior change
- **Feature**: New functionality added
- **Bugfix**: Fixing incorrect behavior
- **Documentation**: README, comments, docs
- **Tests**: New or updated tests
- **Configuration**: Build files, configs, settings
- **Dependencies**: Package updates, new imports

**By Scope**:
- **Module**: Changes within a single module/package
- **Cross-cutting**: Changes across multiple modules
- **Infrastructure**: Build system, CI/CD
- **Tooling**: Scripts, utilities, developer tools

**By Relationship**:
- **Tightly coupled**: Changes must go together
- **Loosely coupled**: Changes could be separate
- **Independent**: Completely unrelated changes

### Phase 3: Create Logical Groups

Group files into commits based on:

1. **Single Responsibility**: Each commit should have one clear purpose
2. **Atomic Changes**: Commit should be complete and functional
3. **Logical Boundaries**: Respect module/package boundaries
4. **Dependency Order**: Commit dependencies before dependents

**Example Grouping Rules**:

```
Group 1: Refactoring - Split module X
  - new package structure
  - deleted old file
  - updated BUILD.bazel
  - updated test imports
  Why: All part of the refactoring, must go together

Group 2: Bugfix - Missing dependencies
  - BUILD.bazel in package Y
  - BUILD.bazel in package Z
  Why: Both fixing the same category of issue

Group 3: Documentation - Update README
  - README.md
  - docs/guide.md
  Why: Documentation updates, independent of code
```

### Phase 4: Generate Commit Messages

For each group, generate a commit message following conventions:

**Format**:
```
<type>: <subject>

<body>

<footer>
```

**Types**:
- `feat:` New feature
- `fix:` Bug fix
- `refactor:` Code restructuring
- `docs:` Documentation only
- `test:` Test additions/changes
- `chore:` Build/tooling/dependencies
- `style:` Formatting (no code change)
- `perf:` Performance improvement

**Subject Line**:
- Start with lowercase (unless proper noun)
- No period at end
- Max 50 characters
- Imperative mood ("Add feature" not "Added feature")

**Body** (optional but recommended):
- Explain what and why, not how
- Wrap at 72 characters
- Separate from subject with blank line
- Can use bullet points

**Footer** (optional):
- Breaking changes: `BREAKING CHANGE: description`
- Issue references: `Fixes #123`, `Closes #456`
- Co-authors: `Co-Authored-By: Name <email>`

### Phase 5: Present Plan to User

Show the proposed commit groups:

```markdown
# Git Commit Plan

I've analyzed your changes and suggest organizing them into 3 commits:

## Commit 1: Refactor - Split interactivity module
**Files** (10):
- src/.../interactivity/ (6 new files)
- src/.../interactivity.py (deleted)
- src/.../BUILD.bazel (modified)
- src/.../test_structure_introspection.py (modified)
- src/.../utils/BUILD.bazel (new)

**Why**: All changes are part of the module refactoring and must go together
for backward compatibility.

**Message**:
```
Refactor: Split interactivity module into focused submodules

Split the monolithic interactivity.py (2,359 lines) into a package
with 5 focused modules following clean architecture principles:
- input_parsing: Parse user input and format material names
- display_utils: Rich console display utilities
- inspection_commands: Material/structure introspection commands
- iteration_display: Iteration state display and visualizations
- command_parser: Main command loop and action parsing

Also fixed missing BUILD.bazel dependencies.
Maintains backward compatibility via __init__.py re-exports.
```

## Commit 2: Docs - Update README for new structure
**Files** (2):
- README.md (modified)
- docs/refactoring.md (new)

**Why**: Documentation updates, independent of the refactoring code.

**Message**:
```
docs: Update README for refactored interactivity module

Document the new package structure and module organization.
Add refactoring guide for future reference.
```

---

**Would you like to proceed with these commits? Or should I adjust the grouping?**
```

### Phase 6: Execute Commits

For each approved group:

1. **Stage files**:
   ```bash
   git add file1 file2 file3
   ```

2. **Create commit** with message:
   ```bash
   git commit -m "$(cat <<'EOF'
   Type: Subject line

   Body paragraph explaining what and why.

   Co-Authored-By: Claude <noreply@anthropic.com>
   EOF
   )"
   ```

3. **Handle errors**:
   - If git push/pull fails with **permission denied** or **authentication** errors:
     - Check GitHub status at https://www.githubstatus.com/
     - Use WebFetch to retrieve current status
     - Inform user if there's a GitHub outage vs. local auth issue

4. **Verify commit**:
   ```bash
   git log -1 --stat
   ```

5. **Proceed to next group**

## Commit Message Templates

### Refactoring

```
refactor: <what was refactored>

<Explain the structure change>
<List key improvements>
<Note backward compatibility if relevant>

Co-Authored-By: Claude <noreply@anthropic.com>
```

### New Feature

```
feat: <feature description>

<What the feature does>
<Why it was needed>
<Any configuration or usage notes>

Co-Authored-By: Claude <noreply@anthropic.com>
```

### Bug Fix

```
fix: <what was fixed>

<Describe the bug>
<Explain the fix>
<Note any side effects>

Fixes #<issue_number>
Co-Authored-By: Claude <noreply@anthropic.com>
```

### Documentation

```
docs: <what docs were updated>

<Summarize documentation changes>
<Note any new sections or restructuring>

Co-Authored-By: Claude <noreply@anthropic.com>
```

### Build/Configuration

```
chore: <build system change>

<What was changed and why>
<Impact on build process>

Co-Authored-By: Claude <noreply@anthropic.com>
```

## Decision Rules for Grouping

### When to Combine into One Commit

✅ **Combine when**:
- Changes are part of same refactoring
- One change depends on another
- Changes implement single feature
- Splitting would break functionality
- All changes serve same purpose

Example: Refactoring a module requires updating:
- New module files
- Deleted old file
- BUILD.bazel
- Test imports
→ All in ONE commit

### When to Split into Multiple Commits

✅ **Split when**:
- Changes serve different purposes
- Changes are in different domains
- Changes could be reverted independently
- Changes have different reviewers
- History would be clearer with separation

Example: During a refactoring session, you also:
- Fixed a typo in README
- Updated a dependency version
- Added a new feature
→ Each is a SEPARATE commit

### Special Cases

**Generated files**: Group with the change that generated them

**Test files**: Usually group with the code they test, unless updating many tests

**BUILD.bazel**: Group with the code that requires the dep change

**CLAUDE.md/docs**: Separate commit unless documenting the same change

## Real-World Example

### Scenario: Mixed changes in working directory

**Git status shows**:
```
Modified:
  src/research/gcms_library_api/BUILD.bazel
  src/research/gcms_library_api/config.yaml
  src/research/gcms_library_api/main.py
  src/research/gcms_library_api/tests/BUILD.bazel
  src/sandbox/jonah/iterative_deform/BUILD.bazel
  src/sandbox/jonah/iterative_deform/tests/test_structure_introspection.py

Deleted:
  src/sandbox/jonah/iterative_deform/interactivity.py

Untracked:
  src/research/gcms_library_api/config_loader_click.py
  src/research/gcms_library_api/tests/test_config_loader_click.py
  src/sandbox/jonah/iterative_deform/interactivity/
  src/sandbox/jonah/utils/BUILD.bazel
```

**Analysis**:

Two distinct change groups:
1. **gcms_library_api**: New config loader feature
2. **iterative_deform**: Module refactoring

**Grouping decision**:

```
Commit 1: iterative_deform refactoring
  Files:
  - src/sandbox/jonah/iterative_deform/BUILD.bazel
  - src/sandbox/jonah/iterative_deform/interactivity.py (deleted)
  - src/sandbox/jonah/iterative_deform/interactivity/* (new)
  - src/sandbox/jonah/iterative_deform/tests/test_structure_introspection.py
  - src/sandbox/jonah/utils/BUILD.bazel

  Rationale: Complete, atomic refactoring

Commit 2: gcms_library_api config feature
  Files:
  - src/research/gcms_library_api/BUILD.bazel
  - src/research/gcms_library_api/config.yaml
  - src/research/gcms_library_api/main.py
  - src/research/gcms_library_api/tests/BUILD.bazel
  - src/research/gcms_library_api/config_loader_click.py
  - src/research/gcms_library_api/tests/test_config_loader_click.py

  Rationale: New feature, independent of refactoring
```

**Execution**:
```bash
# Commit 1
git add src/sandbox/jonah/iterative_deform/
git add src/sandbox/jonah/utils/BUILD.bazel
git rm src/sandbox/jonah/iterative_deform/interactivity.py
git commit -m "refactor: Split interactivity module..."

# Commit 2
git add src/research/gcms_library_api/
git commit -m "feat: Add click-based config loader..."
```

## Advanced Features

### Interactive Staging

For files with mixed changes:

```bash
# Stage parts of a file interactively
git add -p path/to/file

# Review what will be committed
git diff --cached
```

### Commit Dependency Chains

When commits depend on each other:

1. **Identify dependency order**
2. **Commit in sequence**: dependency first, dependent second
3. **Verify each builds**: `bazelisk build //...` after each

### Amend vs New Commit

When to amend:
- Fixing typo in last commit message
- Adding forgotten file to last commit
- Last commit not pushed yet
- You are the author of last commit

When NOT to amend:
- Commit was pushed to shared branch
- Other developers may have pulled it
- Commit is from someone else
- Multiple commits since

## Best Practices

1. **Commit early, commit often** - but semantically
2. **Each commit should build and pass tests** - atomic changes
3. **Write commit messages for future you** - 6 months later
4. **Use imperative mood** - "Add feature" not "Added feature"
5. **Reference issues** - `Fixes #123` for traceability
6. **Credit co-authors** - AI assistance, pair programming
7. **Review diff before committing** - `git diff --cached`
8. **Keep commits focused** - resist "while I'm here" changes

## Integration with Code Review

### PR-Friendly Commits

Structure commits to make review easier:

1. **Refactoring first**: Reviewers see structure before logic
2. **Tests with features**: Tests show intended behavior
3. **Docs with changes**: Context for reviewers
4. **One concern per commit**: Easier to comment on specific changes

### Commit Messages as PR Description

Good commits can be combined into PR description:

```markdown
# PR Title: Refactor interactivity module and add config loader

## Commits:
1. refactor: Split interactivity module into focused submodules
2. feat: Add click-based config loader for gcms_library_api

## Summary:
[Explain overall goal and how commits relate]
```

## Troubleshooting

### "Too many changes to organize"

- Start with clear boundaries (packages, modules)
- Group by file path similarity
- When in doubt, ask user to prioritize

### "Changes are too intertwined"

- May need one commit after all
- Consider if refactoring is truly atomic
- Document complexity in commit message

### "Unsure what some changes do"

- Read git diff carefully
- Check file history: `git log -p path/to/file`
- Ask user to clarify purpose
- Use `git blame` to see context

### GitHub Permission/Authentication Errors

When encountering errors like:
- `Permission denied (publickey)`
- `Authentication failed`
- `Could not read from remote repository`
- `fatal: unable to access`
- `403 Forbidden`

**Immediate actions**:

1. **Check GitHub Status**:
   ```
   Use WebFetch tool:
   url: https://www.githubstatus.com/
   prompt: "Check if there are any current incidents or degraded performance affecting GitHub services, especially Git Operations. Summarize the current status."
   ```

2. **Diagnose the issue**:
   - **If GitHub shows incidents**: Inform user that GitHub is experiencing issues, show the incident details, and suggest waiting
   - **If GitHub is operational**: The issue is likely local authentication
     - Check if SSH keys are configured: `ssh -T git@github.com`
     - Verify remote URL: `git remote -v`
     - Suggest checking GitHub personal access tokens if using HTTPS
     - Recommend reviewing GitHub authentication documentation

3. **Provide context**:
   ```markdown
   GitHub Status: [Operational / Degraded / Incident]

   [If incident]: GitHub is currently experiencing issues with [affected services].
   Incident: [description]
   Status: [current status]
   Recommendation: Wait for GitHub to resolve the issue before proceeding.

   [If operational]: GitHub services are operational. This appears to be a local
   authentication issue. Please check:
   - SSH keys: ssh -T git@github.com
   - Remote URL: git remote -v
   - GitHub personal access token (if using HTTPS)
   ```

4. **Suggest workarounds**:
   - If GitHub is down: commits can still be made locally and pushed later
   - Continue with local commits while GitHub is unavailable
   - Use `git log` to track what needs to be pushed when service resumes

## Version History

- v1.1 (2025-11-18): Added GitHub status checking for permission/auth errors
- v1.0 (2025-11-18): Initial skill creation based on multi-change commit experience
