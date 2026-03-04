# Notion Workspace Skill Design

## Problem

Claude writes to the wrong Notion locations and lacks context about Jonah's workspace structure (database schemas, valid property values, routing logic). This forces Jonah to re-explain structure each session.

## Solution

A single auto-invoke skill that injects workspace context whenever Claude interacts with Notion.

## Architecture

```
skills/
  notion-workspace/
    SKILL.md          # Auto-invoke skill with routing logic
    reference.md      # Hardcoded workspace map (IDs, schemas, rules)
```

### SKILL.md

- **name**: `notion-workspace`
- **autoInvoke**: `true`
- **description**: Use when interacting with Jonah's Notion workspace — creating pages, querying databases, adding tasks, writing documents, or searching Notion content. Provides workspace structure, database schemas, and routing rules for the "CLAUDE [Jonah]" page.

The skill body:
1. Instructs Claude to read `reference.md` for the workspace map
2. Defines routing rules (what content goes where)
3. Provides examples of correct tool usage with hardcoded IDs

### reference.md

Hardcoded workspace map containing:

- **Root page**: `3190f22f-7b6e-8018-8099-e1454419dfec` ("CLAUDE [Jonah]")
- **Document Hub**: database `3190f22f-7b6e-80be-8065-ea5656df56b2`, data source `collection://3190f22f-7b6e-806c-be36-000b0c4091ac`
  - Schema: Doc name (title), Category (multi_select: Proposal, Customer research, Strategy doc, Planning)
- **Tasks Tracker**: database `3190f22f-7b6e-8053-838fd88198146c4f`, data source `collection://3190f22f-7b6e-80c6-ba9c-000b9942d257`
  - Schema: Task name (title), Status (Not started/In progress/Done), Priority (High/Medium/Low), Effort level (Small/Medium/Large), Task type (Bug/Feature request/Polish), Assignee, Due date, Description

## Routing Rules

| Content type | Destination | Method |
|---|---|---|
| Tasks, bugs, feature requests, todos | Tasks Tracker database | Create row with Status/Priority/Effort/Task type |
| Documents, research, proposals, plans | Document Hub database | Create row with Category |
| Freeform notes, subpages | Root page | Create subpage under "CLAUDE [Jonah]" |

## Key Behaviors

- Always use hardcoded IDs from reference.md — never search for databases by name
- When creating tasks: default Status to "Not started", require Task name
- When creating documents: require Doc name, suggest Category based on content
- When searching: scope to "CLAUDE [Jonah]" page using `page_url` parameter
- When unsure where something goes: ask the user

## Maintenance

To update the workspace map (e.g., after adding a new database), edit `reference.md` with the new IDs and schemas. No changes to SKILL.md needed.
