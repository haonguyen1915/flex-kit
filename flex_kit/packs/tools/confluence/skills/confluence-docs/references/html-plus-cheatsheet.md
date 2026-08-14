# Confluence HTML+ Cheatsheet (Atlassian MCP)

Publish with `contentFormat: "html"`. Everything below is standard HTML plus Confluence's
`data-type` attributes. **Never** use storage XML (`<ac:structured-macro>`, `<ri:...>`) -
this MCP rejects it. **Never** wrap the body in `<html>`, `<head>`, or `<body>`.

## Text, headings, links, code

```html
<h2>Section</h2>
<h3>Subsection</h3>
<p>Paragraph with <strong>bold</strong>, <em>italic</em>, <code>inline code</code>.</p>
<a href="https://example.com">External link</a>
<a href="https://example.com" data-card-appearance="inline">Inline smart-card link</a>

<pre><code class="language-python">def hello():
    print("hi")
</code></pre>
```

## Panels (colored callout boxes)

```html
<div data-type="panel-info"><p>Summary / context.</p></div>
<div data-type="panel-note"><p>Aside or side note.</p></div>
<div data-type="panel-success"><p>Recommended path.</p></div>
<div data-type="panel-warning"><p>Gotcha — read before proceeding.</p></div>
<div data-type="panel-error"><p>Do NOT do this.</p></div>
```

## Status badges (inline state chips)

Colors: `green | red | yellow | blue | neutral | purple`.

```html
<span data-type="status" data-color="green">Stable</span>
<span data-type="status" data-color="yellow">In review</span>
<span data-type="status" data-color="red">Deprecated</span>
<span data-type="status" data-color="blue">v1</span>
<span data-type="status" data-color="neutral">Draft</span>
```

## Expand (collapsible section)

```html
<details><summary>Show request/response example</summary>
  <pre><code class="language-json">{ "ok": true }</code></pre>
</details>
```

## Task list & decision list

```html
<ul data-type="task-list">
  <li data-type="task-item"><input type="checkbox"> Open item</li>
  <li data-type="task-item"><input type="checkbox" checked> Done item</li>
</ul>

<ul data-type="decision-list">
  <li data-type="decision-item" data-state="DECIDED">Publish via MCP HTML+.</li>
  <li data-type="decision-item" data-state="UNDECIDED">Whether to auto-render Mermaid.</li>
</ul>
```

## Layout columns

```html
<section data-type="layout-two-equal">
  <div data-type="column"><p>Left column</p></div>
  <div data-type="column"><p>Right column</p></div>
</section>
<!-- also: layout-three-equal -->
```

## Tables

```html
<table data-layout="default">
  <thead><tr><th>Method</th><th>Endpoint</th><th>Notes</th></tr></thead>
  <tbody>
    <tr><td>GET</td><td>/v1/items</td><td>List</td></tr>
    <tr><td>POST</td><td>/v1/items</td><td>Create</td></tr>
  </tbody>
</table>
```

`data-layout`: `default | center | wide | full-width`. Cells accept `data-background` for a
highlight color; columns accept `data-colwidth`.

## Table of contents

The TOC is a native macro (extension). Use the extension node with the core macro type:

```html
<div data-type="extension"
     data-extension-type="com.atlassian.confluence.macro.core"
     data-extension-key="toc"></div>
```

If a specific macro node is rejected, fall back to a manual on-page index: a short
`panel-note` with anchor links to each `<h2>`.

## Dates & mentions

```html
<time datetime="2026-08-14">14 Aug 2026</time>
<span data-type="mention" data-user-id="ACCOUNT_ID">@Name</span>
```

Only ever copy a real `data-user-id` from tool output — never invent one.

## Native macros / extensions (general form)

```html
<div data-type="extension"
     data-extension-type="com.atlassian.confluence.macro.core"
     data-extension-key="KEY"
     data-parameters='{"param":"value"}'></div>
```

Omit `macroId`. Use `bodied-extension` when the macro wraps content.

## Opaque IDs — hard rules

Only copy these from existing content or tool output; never fabricate: `data-user-id`,
`data-id`, `data-collection`, `data-media-id`, `data-media-collection`, `data-resource-id`,
`data-local-id`.
- **New** nodes: omit `data-local-id`.
- **Editing** fetched HTML: preserve every existing `data-local-id` as-is.

## ADF nesting rules (strict — violations are rejected)

- Inline-only content (no block children): task items, decision items, headings,
  table/media captions.
- A **list item** cannot contain headings, tables, panels, or expands.
- A **panel** cannot contain tables, expands, blockquotes, or another panel.
- A **table cell** may contain headings, panels, lists, media, blockquote, decision list,
  and a **nested** expand (`<details data-type="nested-expand">`) — but NOT a nested table
  or a normal `<details>` expand.
- Do not self-nest: no panel-in-panel, expand-in-expand, table-in-table,
  blockquote-in-blockquote.

When the API rejects a body, the error names the offending node — fix its placement per the
rules above and retry rather than guessing.
