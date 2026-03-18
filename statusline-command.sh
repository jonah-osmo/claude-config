#!/usr/bin/env bash
# Claude Code status line - inspired by asciiship zsh theme

export GIT_OPTIONAL_LOCKS=0

input=$(cat)

cwd=$(echo "$input" | jq -r '.workspace.current_dir // .cwd')
model=$(echo "$input" | jq -r '.model.display_name // empty')
remaining=$(echo "$input" | jq -r '.context_window.remaining_percentage // empty')
used=$(if [ -n "$remaining" ]; then echo $((100 - remaining)); fi)

# Shorten home directory to ~
home="$HOME"
short_cwd="${cwd/#$home/\~}"

# Git info (skip optional locks to avoid blocking)
git_part=""
if git -C "$cwd" rev-parse --git-dir > /dev/null 2>&1; then
  branch=$(git -C "$cwd" symbolic-ref --short HEAD 2>/dev/null || git -C "$cwd" rev-parse --short HEAD 2>/dev/null)
  if [ -n "$branch" ]; then
    status_flags=""
    git_status=$(git -C "$cwd" status --porcelain 2>/dev/null)
    if echo "$git_status" | grep -q '^ *[MADRCU]'; then
      status_flags="${status_flags}+"
    fi
    if echo "$git_status" | grep -q '^?'; then
      status_flags="${status_flags}!"
    fi
    ahead=$(git -C "$cwd" rev-list --count @{u}..HEAD 2>/dev/null || echo "0")
    behind=$(git -C "$cwd" rev-list --count HEAD..@{u} 2>/dev/null || echo "0")
    [ "$ahead" -gt 0 ] 2>/dev/null && status_flags="${status_flags}>"
    [ "$behind" -gt 0 ] 2>/dev/null && status_flags="${status_flags}<"
    if [ -n "$status_flags" ]; then
      git_part=" on ${branch} [${status_flags}]"
    else
      git_part=" on ${branch}"
    fi
  fi
fi

# Context window
ctx_part=""
if [ -n "$used" ]; then
  ctx_part=" ctx:${used}%"
fi

# Model
model_part=""
if [ -n "$model" ]; then
  model_part=" | ${model}"
fi

printf '\033[36m%s\033[0m\033[35m%s\033[0m\033[2m%s%s\033[0m' \
  "$short_cwd" "$git_part" "$ctx_part" "$model_part"
