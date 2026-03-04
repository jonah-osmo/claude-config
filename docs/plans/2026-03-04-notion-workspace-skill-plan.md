# Notion Workspace Skill Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create an auto-invoke skill that gives Claude full context about Jonah's Notion workspace structure whenever it interacts with Notion.

**Architecture:** Two files — SKILL.md (routing logic + instructions) and reference.md (hardcoded IDs, schemas, property values). The skill auto-invokes on any Notion interaction.

**Tech Stack:** Claude Code plugin skill (Markdown with YAML frontmatter)

---

### Task 1: Create reference.md (workspace map)

**Files:**
- Create: `skills/notion-workspace/reference.md`

**Step 1: Create the skill directory**

```bash
mkdir -p skills/notion-workspace
```

**Step 2: Write reference.md**

Create `skills/notion-workspace/reference.md` with the complete workspace map:

```markdown
# Jonah's Notion Workspace Map

## Root Page

- **Name**: CLAUDE [Jonah]
- **ID**: `3190f22f-7b6e-8018-8099-e1454419dfec`
- **URL**: https://www.notion.so/3190f22f7b6e80188099e1454419dfec

All content must be created under this page unless the user explicitly specifies another location.

## Databases

### Document Hub

- **Database URL**: https://www.notion.so/3190f22f7b6e80be8065ea5656df56b2
- **Data Source**: `collection://3190f22f-7b6e-806c-be36-000b0c4091ac`

| Property | Type | Values |
|----------|------|--------|
| Doc name | title | (required) |
| Category | multi_select | Proposal, Customer research, Strategy doc, Planning |
| Created by | created_by | (auto) |
| Created time | created_time | (auto) |
| Last edited by | last_edited_by | (auto) |
| Last updated time | last_edited_time | (auto) |

### Tasks Tracker

- **Database URL**: https://www.notion.so/3190f22f7b6e8053838fd88198146c4f
- **Data Source**: `collection://3190f22f-7b6e-80c6-ba9c-000b9942d257`

| Property | Type | Values |
|----------|------|--------|
| Task name | title | (required) |
| Status | status | Not started, In progress, Done |
| Priority | select | High, Medium, Low |
| Effort level | select | Small, Medium, Large |
| Task type | multi_select | 🐞 Bug, 💬 Feature request, 💅 Polish |
| Assignee | person | (user ID) |
| Due date | date | (ISO-8601) |
| Description | text | (freeform) |
| Updated at | last_edited_time | (auto) |
```

**Step 3: Commit**

```bash
git add skills/notion-workspace/reference.md
git commit -m "Add notion workspace reference map with IDs and schemas"
```

---

### Task 2: Create SKILL.md (routing logic)

**Files:**
- Create: `skills/notion-workspace/SKILL.md`

**Step 1: Write SKILL.md**

Create `skills/notion-workspace/SKILL.md` with:

```markdown
---
name: notion-workspace
description: Use when interacting with Jonah's Notion workspace — creating pages, querying databases, adding tasks, writing documents, or searching Notion content. Provides workspace structure, database schemas, and routing rules for the "CLAUDE [Jonah]" page. Use this skill whenever Notion MCP tools are involved, even for simple reads or searches.
autoInvoke: true
---

# Notion Workspace

Jonah's personal Notion workspace is organized under a single root page called "CLAUDE [Jonah]". All reads, writes, and searches should be scoped to this page and its children.

Read `reference.md` (in this skill's directory) for the complete workspace map including page IDs, database schemas, and valid property values. Use those hardcoded IDs directly — never search for databases by name.

## Routing Rules

| Content type | Destination | Action |
|---|---|---|
| Tasks, bugs, feature requests, todos | **Tasks Tracker** database | Create database row |
| Documents, research, proposals, plans | **Document Hub** database | Create database row |
| Freeform notes, subpages | **Root page** | Create subpage under "CLAUDE [Jonah]" |

When unsure where content belongs, ask the user.

## Creating Tasks

Use `notion-create-pages` with the Tasks Tracker data source URL from reference.md. Defaults:
- **Status**: "Not started"
- **Task name**: required

## Creating Documents

Use `notion-create-pages` with the Document Hub data source URL from reference.md. Defaults:
- **Doc name**: required
- Suggest **Category** based on content type

## Searching

Always scope searches to the root page using the `page_url` parameter:
```
page_url: "3190f22f-7b6e-8018-8099-e1454419dfec"
```

## Querying Databases

Use `notion-query-database-view` with the data source URLs from reference.md.

## Key Rules

- Always use hardcoded IDs from reference.md — never search for databases by name
- Never create content outside "CLAUDE [Jonah]" unless the user explicitly says to
- When creating rows, use exact property names and valid values from reference.md
- Prefer database rows over subpages for structured content
```

**Step 2: Commit**

```bash
git add skills/notion-workspace/SKILL.md
git commit -m "Add notion-workspace auto-invoke skill with routing logic"
```

---

### Task 3: Update CLAUDE.md to reference the skill

**Files:**
- Modify: `CLAUDE.md` (the Notion section)

**Step 1: Update the Notion section in CLAUDE.md**

Add a pointer to the skill so Claude knows detailed instructions exist:

```markdown
## Notion

- **Default workspace**: Always write to the "CLAUDE [Jonah]" page and its subpages/sub-databases only
- **Never** create or modify pages outside "CLAUDE [Jonah]" unless explicitly instructed
- When creating new pages or database entries, place them under "CLAUDE [Jonah]" or one of its existing sub-databases
- **Workspace details**: See the `notion-workspace` skill for database IDs, schemas, and routing rules
```

**Step 2: Commit**

```bash
git add CLAUDE.md
git commit -m "Reference notion-workspace skill from CLAUDE.md"
```

---

### Task 4: Test the skill with a dry run

**Step 1: Verify skill structure**

```bash
ls -la skills/notion-workspace/
# Expected: SKILL.md, reference.md
```

**Step 2: Verify frontmatter parses correctly**

```bash
head -5 skills/notion-workspace/SKILL.md
# Expected: valid YAML frontmatter with name, description, autoInvoke
```

**Step 3: Push all changes**

```bash
git push
```
