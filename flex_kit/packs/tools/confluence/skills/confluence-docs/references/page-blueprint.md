# Page Blueprint

A repeatable skeleton for a clean Confluence page, plus a full worked example. Adapt
sections to the content; keep the shape.

## Skeleton (top to bottom)

1. **Lead panel** — one `panel-info` summarizing what the page is, who it's for, and
   current status. First thing the reader sees.
2. **Status line** — one or more `status` badges (e.g. `Stable`, `v1`, owner).
3. **Table of contents** — for any page longer than ~2 screens.
4. **Body sections** — `<h2>` per topic, `<h3>` for sub-topics. Prefer tables for
   comparative data, code blocks for code, panels for warnings/tips.
5. **Deep detail in expands** — long examples, edge cases, raw payloads go inside
   `<details>` so the main flow stays scannable.
6. **Footer** — related links (as inline smart-cards), last-reviewed date, owner.

## Worked example (an API doc)

```html
<div data-type="panel-info">
  <p><strong>License Activation API</strong> — how the desktop app activates a
  seat and validates a license. Audience: desktop + backend engineers.</p>
</div>

<p>
  <span data-type="status" data-color="green">Stable</span>
  <span data-type="status" data-color="blue">v1</span>
  <span data-type="status" data-color="neutral">Owner: Backend</span>
</p>

<div data-type="extension" data-extension-type="com.atlassian.confluence.macro.core" data-extension-key="toc"></div>

<h2>Overview</h2>
<p>The client treats <code>activation_token</code> as opaque and calls a fixed
set of endpoints. All responses are RFC 7807 <code>problem+json</code> on error.</p>

<div data-type="panel-warning">
  <p>Never rename or reshape the fixed client endpoints — the desktop app depends
  on the exact wire contract.</p>
</div>

<h2>Endpoints</h2>
<table data-layout="default">
  <thead><tr><th>Method</th><th>Path</th><th>Purpose</th><th>Status</th></tr></thead>
  <tbody>
    <tr><td>POST</td><td>/v1/activations</td><td>Activate a seat</td><td>201 / 409</td></tr>
    <tr><td>DELETE</td><td>/v1/activations/{id}</td><td>Release a seat</td><td>204</td></tr>
    <tr><td>GET</td><td>/v1/crl</td><td>Revocation list</td><td>200</td></tr>
  </tbody>
</table>

<h2>Example</h2>
<details><summary>Activation request / response</summary>
  <pre><code class="language-bash">curl -X POST https://api.example.com/v1/activations \
  -H "Idempotency-Key: 5f...c1" \
  -d '{"license_key":"...","device_id":"..."}'</code></pre>
  <pre><code class="language-json">{ "activation_token": "eyJ...", "seat": 2, "seats_total": 5 }</code></pre>
</details>

<h2>Decisions</h2>
<ul data-type="decision-list">
  <li data-type="decision-item" data-state="DECIDED">activation_token stays opaque to the client.</li>
</ul>

<p>Related: <a href="https://.../webapp-spec" data-card-appearance="inline">Webapp backend spec</a>
 · Last reviewed <time datetime="2026-08-14">14 Aug 2026</time>.</p>
```

## Reformatting an existing ugly page

1. `getConfluencePage` with `contentFormat: "html"` — keep the original HTML and every
   `data-local-id`.
2. Map the mess to the skeleton: find the implicit summary → lead panel; bare URL lists →
   a table or inline smart-cards; pasted code → `<pre><code>`; "note:" / "warning:" prose →
   the matching panel; long dumps → `<details>`.
3. Preserve all real content and existing IDs; change structure/format, not facts.
4. `updateConfluencePage` with a `versionMessage` like
   `"Reformat: lead panel, TOC, panels, code blocks"`.

## Two-column layouts — gotchas (learned in practice)

- **Do NOT put a panel (`data-type="panel-*"`) inside a layout column.** Confluence does
  not equalize column/panel heights — each panel is only as tall as its content, so columns
  of unequal length render as a tall box next to a short box (visually lopsided). Instead,
  head each column with a **status chip** (e.g. green "Good", yellow "Trade-off") or an
  `<h3>`, then a plain `<ul>`. No box = no height mismatch; uneven text just reads as normal
  columns.
- **Inline smart-cards only look good for links Confluence can resolve.** Same-site
  Confluence page links resolve to a clean title chip — keep `data-card-appearance="inline"`.
  External links (e.g. GitHub) with no connected integration render as a raw-URL chip plus a
  "Connect your account" prompt that breaks layout — use a **plain labeled link**
  (`<a href="...">yourrepo#527</a>`).

## Diagrams

This MCP embeds media by opaque `data-media-id` (from an existing upload) — you cannot
invent one. Options, best first:
- Attach a rendered PNG/SVG to the page out-of-band, then reference its real media id.
- Render Mermaid locally (`mmdc -i d.mmd -o d.png`) and attach.
- As a last resort, keep the Mermaid source inside a `<details>` code block so it is at
  least copy-runnable, and note that it needs rendering.

Never draw architecture with ASCII boxes in a `<pre>` — it reads as clutter.
