# Create Workflow Reference

Full step detail and templates for the Create Workflow (creating a new document or
documentation item). The SKILL.md section carries the six-step summary; this file
holds the templates and per-step detail.

## Step 1: Determine Category

Ask the user or infer from context. Use the classification guide:

- Has a deadline or specific goal? → **Projects**
- Ongoing responsibility, no end date? → **Areas**
- Reference material for future use? → **Resources**

If uncertain, load `references/para-categories.md` for the detailed classification
flowchart.

## Step 2: Determine Structure

**Simple item** (single topic, standalone):
→ Create a single `.md` file directly in the category directory.

**Complex item** (multiple deliverables, ongoing outputs):
→ Create a directory containing multiple `.md` files as needed.

## Step 3: Choose Filename

Naming convention: `kebab-case.md`

- Use descriptive, lowercase names with hyphens.
- Include a date prefix for time-sensitive items: `YYYY-MM-DD-topic-name.md`.
- For directories: `kebab-case/<document-name>.md`.

Examples:

- `<base>/projects/website-redesign/requirements.md`
- `<base>/areas/team-onboarding.md`
- `<base>/resources/api-reference.md`
- `<base>/projects/website-redesign/2024-03-15-kickoff-notes.md`

## Step 4: Write Content

Use plain markdown. No frontmatter required. Start with an H1 title. Never use
horizontal rules (`---`).

**Simple document template:**

```markdown
# [Title]

[Content starts here]
```

**Directory with multiple files:**

```
<base>/projects/website-redesign/
├── requirements.md
├── design-spec.md
├── 2024-03-15-kickoff-notes.md
└── 2024-03-20-review-notes.md
```

**Meeting notes template:**

```markdown
# [Meeting Title] — YYYY-MM-DD

## Attendees

- [Names]

## Agenda

1. [Topic]

## Notes

[Notes here]

## Action Items

- [ ] [Action item with owner]
```

## Step 5: Connect (Networked Knowledge)

Right after creating a document, wire it into the network so it does not stay an
orphan. Follow `references/linking-rules.md`.

1. **Secure an inbound link**: make the new document receive at least one link from
   a related existing document or that folder's `README.md` (MOC). Orphan nodes get
   lost.
2. **Contextual links**: weave `[[filename]]` wikilinks naturally into the prose.
   Do not dump a "related links" list at the bottom.
3. **Update the MOC**: add a one-line link to the new document in that folder's
   `README.md`.
4. **Ground references**: if it is a `resources/` document, also link it to an
   `areas/`/`projects/` document holding your interpretation, grounding it in the
   network.

## Step 6: Confirm and Report

After creation, report:

- Full path of the created file
- Which PARA category it was placed in
- Brief summary of what was created
- Which document/MOC now links to it (connection status)
