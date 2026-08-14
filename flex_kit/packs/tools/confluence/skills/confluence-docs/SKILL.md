---
name: confluence-docs
description: Author and publish beautiful, well-structured Confluence pages via the Atlassian MCP using Confluence HTML+ (panels, status badges, layouts, expands, TOC) - never raw markdown or storage XML. Use when asked to publish or write a Confluence page, make an existing page prettier, or reformat a messy / plain doc. Not for in-repo docs (see the flex-docs command) or for Jira issues.
---

# Confluence pretty docs

Turn plain or messy Confluence content into clean, scannable, professionally formatted
pages. Built for the **Atlassian MCP** (e.g. `atlassian-personal` / `claude_ai_Atlassian`),
which renders **Confluence HTML+** - standard HTML plus `data-type` attributes - not
storage XML. Load the MCP tools with ToolSearch if they're deferred.

## The one golden rule

Publish with `contentFormat: "html"` and write **Confluence HTML+**. Never:
- dump raw Markdown (`contentFormat: "markdown"`) - it renders flat and plain;
- hand-write legacy storage XML (`<ac:structured-macro>`, `<ri:...>`) - this MCP
  **rejects** it. Use `data-type` nodes instead (see the cheatsheet).

## Workflow

1. **Locate the target** (once per session):
   - `cloudId` -> `getAccessibleAtlassianResources` (your site).
   - `spaceId` -> `getConfluenceSpaces`. Confirm the space + parent page with the user if
     they didn't name one; accepts a space key directly.
   - Editing an existing page? `getConfluencePage` with `contentFormat: "html"` first, so
     you edit its real HTML+ and **preserve every `data-local-id`**.
2. **Audit** (for reformat requests): read the current body, list what's ugly -
   wall-of-text, no headings, no lead summary, bare links, code as plain text. Say what
   you'll change before changing it.
3. **Draft in HTML+** following the [page blueprint](references/page-blueprint.md) and
   [HTML+ cheatsheet](references/html-plus-cheatsheet.md). Respect the ADF nesting rules
   (see cheatsheet - they are strict; invalid HTML is rejected).
4. **Publish**:
   - New: `createConfluencePage` (`cloudId`, `spaceId`, `title`, `body`,
     `contentFormat:"html"`, `parentId` to nest, `status:"draft"` to stage).
   - Update: `updateConfluencePage` (`cloudId`, `pageId`, `body`, `contentFormat:"html"`,
     a clear `versionMessage`).
5. **Verify**: re-`getConfluencePage` (or open the URL) and confirm panels, layouts, and
   code blocks render as intended. If rejected, read the error - it names the invalid node
   - fix nesting, retry.

## What "pretty" means here (apply, don't overdo)

- **Lead in with a panel**: one `panel-info`/`panel-note` summary up top - what the page
  is and who it's for. Not a naked first paragraph.
- **Structure with headings** (`<h2>`/`<h3>`) and a **table of contents** for any page
  past ~2 screens.
- **Status badges** (`data-type="status"`) for states: `Draft`, `In review`, `Stable`,
  `Deprecated`, version tags.
- **Panels for signals**: `panel-warning` for gotchas, `panel-success` for "recommended",
  `panel-error` for "do not", `panel-note` for asides.
- **Tables** for anything comparative (endpoints, config, options) - never a bullet list
  of "key: value".
- **Code blocks** with a language (`<pre><code class="language-python">`), never code
  pasted as plain `<p>`.
- **Collapse deep detail** in `<details>` expands so the page stays scannable.
- **Layout columns** (`layout-two-equal`) only when two things are genuinely side-by-side.

Restraint is the point: a clean page uses 3-4 of these deliberately, not all on every
section. Signal, not decoration.

## References

- [references/html-plus-cheatsheet.md](references/html-plus-cheatsheet.md) - every
  `data-type` node with copy-paste HTML + the ADF nesting rules.
- [references/page-blueprint.md](references/page-blueprint.md) - the standard page skeleton
  and a full worked example.

## When not to use

- Reading/searching only -> call the MCP read tools directly.
- Jira issues -> Jira tools.
- One-line comment on a page -> `createConfluenceFooterComment`.
- In-repo project docs -> the `flex-docs` command.
