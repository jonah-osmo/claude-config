---
description: Generate and share a transcript of the current Claude Code session as a GitHub Gist
allowed-tools: Bash(claude-code-transcripts:*)
---

Upload the current session transcript to GitHub Gist by running this exact command:

```bash
claude-code-transcripts json "`ls -t ~/.claude/projects/${PWD//\//-}/*.jsonl 2>/dev/null | head -1`" --gist $ARGUMENTS
```

After running, provide the user with:
1. The GitHub Gist URL
2. The gisthost.github.io preview link for easy viewing
