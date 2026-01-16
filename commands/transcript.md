---
description: Generate and share a transcript of the current Claude Code session as a GitHub Gist
allowed-tools: Bash(claude-code-transcripts:*), Bash(ls:*), Bash(find:*), Bash(realpath:*)
---

Upload the current session transcript to GitHub Gist.

First, find the session file (using realpath to handle symlinked directories):

```bash
ls -t ~/.claude/projects/"$(realpath "$PWD" | tr '/' '-')"/*.jsonl 2>/dev/null | head -1
```

Then run the transcript command with the session file path:

```bash
claude-code-transcripts json "<session-file-path>" --gist $ARGUMENTS
```

If no session file is found for the current project, search all projects for the most recent session:

```bash
find ~/.claude/projects -name "*.jsonl" -type f -exec ls -t {} + 2>/dev/null | head -1
```

After running, provide the user with:
1. The GitHub Gist URL
2. The gisthost.github.io preview link for easy viewing
