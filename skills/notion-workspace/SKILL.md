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
