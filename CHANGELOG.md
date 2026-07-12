# Changelog

## [0.1.4] - 2026-07-12

### Release Notes

Configuration management is now more robust and user-friendly, with clearer layering and new CLI tooling.

### What's Changed
- Added `config show` and `config edit` commands to inspect and update configuration from the CLI.
- Introduced a global `~/.flex-kit` config layer (including Codex model tuning knobs) to complement per-project settings.
- Improved reliability by correctly resolving the project root so hooks don’t scatter `state.json` across directories.
- Standardized and reorganized config storage by moving project config to `.flexkit/config.json` and adopting comment-friendly TOML config files.

### Features

- feat: add config show and edit cli commands (459b78a)
- feat: add ~/.flex-kit global config layer with codex model knobs (7378dcc)

### Bug Fixes

- fix: resolve project root so hooks never scatter state.json (af032b8)

### Refactoring

- refactor: switch config files to commentable toml (f42700a)
- refactor: rename project config to .flexkit/config.json (0ed8e23)

**Contributors:** @Nguyễn Văn Hảo

**Compare changes:** [v0.1.3...v0.1.4](https://github.com/haonguyen1915/flex-kit.git/-/compare/v0.1.3...v0.1.4)

## [0.1.3] - 2026-06-27

### Release Notes

Expanded cloud and web skill packs while improving planning workflow reliability and developer tooling.

### What's Changed
- Added new AWS and FastAPI skill packs (including EC2 lifecycle plus IAM/Lambda/S3/DynamoDB and REST/auth) and rebuilt the Python pack as self-contained language skills.
- Improved planning UX with an interactive one-question-at-a-time interview, safer plan creation when another plan is active, and shorter plan slugs.
- Introduced optional desktop notifications when long-running flex commands finish.
- Hardened guardrails and status reporting by scoping the pre-tool guard to sensitive path arguments and fixing plan status checkbox counting.
- Streamlined contributor setup by migrating the build workflow from Poetry to uv.

### Features

- feat: add aws-ec2 skill with instance lifecycle (643396e)
- feat: add aws cloud pack with iam lambda s3 dynamodb skills (54f2998)
- feat: add fastapi pack with rest and auth skills (1343503)
- feat: rebuild python pack as self-contained language skills (4220f3c)
- feat: add opt-in desktop notification when a long flex command finishes (6ea07c4)
- feat: guard a new plan against an active one and shorten the slug (a25f933)
- feat: resolve planning questions via a one-at-a-time choice interview (faf14be)

### Bug Fixes

- fix: scope the pre-tool guard to sensitive path args (921837b)
- fix: count only steps-section checkboxes in plan status (8feeba1)

### Documentation

- docs: add cloud/platform axis to skill taxonomy (b536a1d)
- docs: adopt language-first skill split and discipline scope (d2edfec)

### Refactoring

- refactor: name architecture styles and sharpen boundaries (7584ee6)
- refactor: discover grouped skills and category-nested packs (c86c824)
- refactor: group packs by axis and python skills into tiers (c95624a)

### Build

- build: migrate from poetry to uv (d369ca9)

**Contributors:** @Nguyễn Văn Hảo

**Compare changes:** [v0.1.2...v0.1.3](https://github.com/haonguyen1915/flex-kit.git/-/compare/v0.1.2...v0.1.3)

## [0.1.2] - 2026-06-23

### Release Notes

Improves Codex integration controls and CLI ergonomics, with better diagnostics.

### What's Changed
- Added a `--codex` flag to flex-fix so Codex-powered review can be enabled explicitly when you want it.
- Made cross-model Codex review opt-in again, reducing unexpected behavior in default runs.
- Now surfaces Codex stderr output instead of swallowing it, making failures and misconfigurations easier to debug.
- Added a `--version` CLI flag that reports the package version directly from `pyproject`.

### Features

- feat: add --codex to flex-fix (c1d79cc)
- feat: add --version reading the version from pyproject (0b53134)

### Bug Fixes

- fix: surface codex stderr instead of swallowing it (2f3b0f9)

### Refactoring

- refactor: make the codex cross-model review opt-in again (79d5e22)

**Contributors:** @Nguyễn Văn Hảo

**Compare changes:** [v0.1.1...v0.1.2](https://github.com/haonguyen1915/flex-kit.git/-/compare/v0.1.1...v0.1.2)

## [0.1.1] - 2026-06-22

### Release Notes

A major usability and workflow upgrade that turns Flex Kit into a full planning→delivery→review toolchain with richer packs, safer init/update, and stronger automated reviews.

### What's Changed
- Introduced a front-door planning workflow with lifecycle commands, approval checkpoints, delivery modes, and hooks to guide work from plan to execution.
- Expanded the bundled ecosystem with many new language/framework packs (TypeScript, Python, Rust, Svelte, Frontend, Backend) plus interactive pack selection and one-shot install/add/remove flows.
- Upgraded Codex review to be more comprehensive and actionable: cross-model review by default, broader diff coverage (staged/untracked/base ranges), and an --instruction flag to steer review focus.
- Added a full docs and guide toolchain (flex-docs, init-docs, guide/agent creators) with controlled injection via markers/frontmatter and automatic project docs indexing for agents.
- Improved CLI experience with a rich UI, live multi-line status bar, and clearer visibility into running subagents.

### Features

- feat: add --instruction to steer the codex review lens (31549d8)
- feat: feed the root handoffs context into the codex review (0341f0d)
- feat: broaden codex diff to staged, untracked, and base ranges (f0aace4)
- feat: run the codex cross-model review by default (db631e7)
- feat: refresh installed packs too on init --update (b2bf7d5)
- feat: add init --update to refresh base items to new version (148089b)
- feat: carry the gen record across init --force (cfa2530)
- feat: clean orphaned pack output via the bundled catalog (00d632c)
- feat: make add and remove source-only by default (e2fe7e4)
- feat: make init scaffold source only, guard --force wipe (2c6fc5d)
- feat: add interactive multi-select pack picker (a1f4ac5)
- feat: add svelte pack with runes, components, and naming skills (dfcddd2)
- feat: add python pack with naming, idioms, and typing skills (9c27a61)
- feat: add typescript pack with naming, types, and idioms skills (6096221)
- feat: add rust pack with naming, idioms, and error-handling skills (5f9a7f6)
- feat: add frontend pack with component, state, a11y, perf, and styling skills (71d0583)
- feat: expand flex-skill-creator with naming axes and authoring best practices (b6899e7)
- feat: add engineering pack with architecture and craft skills (47b47a8)
- feat: define the group-prefix skill naming convention in flex-skill-creator (d2a58d5)
- feat: add chesterton's fence and over-simplification guards to simplifier (f1077dc)
- feat: add red flags to the verify-fix-loop skill (f988edd)
- feat: add tight rationalizations to the verify-fix-loop skill (0a773ed)
- feat: add red flags self-monitoring to the verify-fix agents (0f0952c)
- feat: require a continuous-improvement rule in the generated guide (1e8f5f9)
- feat: add flex-commit command for structured conventional commits (257f5f0)
- feat: inject the agent roster into commands at an AGENTS marker (f3a2c5a)
- feat: give tester a project-docs marker so testing specs can target it (923f254)
- feat: route doc injection by agent id or lane and fix inline marker replacement (10c4fa3)
- feat: add flex-guide-creator command for CLAUDE.md and AGENTS.md (14d5b93)
- feat: add positives, stats, and pre-existing-debt bands to flex-review (0f62753)
- feat: add verification gates and standardize status across planner, debugger, simplifier (26456d7)
- feat: refine flex-codex-review with action grammar and overrides (3c03b74)
- feat: add scope detection and report format to flex-review (5e96804)
- feat: add flex-agent-creator command to author and audit agents (e824c0c)
- feat: enforce model and lane in agent frontmatter via agent-contract check (b7a913f)
- feat: align verifier agents on the verification gate and handoff contract (1aa0140)
- feat: sharpen reviewer stub detection and check honesty (5eed4c8)
- feat: make reviewer enforce indexed project specs (e014824)
- feat: add flex-docs command for maintaining docs/ (102ebdf)
- feat: gate doc injection behind an inject:true frontmatter signal (9617911)
- feat: keep unmanaged host files on gen via a generated record (cc48c66)
- feat: harden reviewer/tester and add debugger and simplifier agents (1db8130)
- feat: add flex-kit init-docs to scaffold a docs skeleton (59740dd)
- feat: add optional codex cross-model review to the verify-fix loop (7ced591)
- feat: inject a project docs index into agents via <!-- DOCS --> (3c6a7af)
- feat: show running subagent names in the status bar (851938c)
- feat: add a live multi-line status bar for claude code (88d1822)
- feat: route CLI output through a rich-based ui module (e9efce9)
- feat: add --all flag to add every bundled pack (5082e74)
- feat: make flex-plan a front-door with approval checkpoints (347c41e)
- feat: add planning-methodology skill with on-demand references (738fb92)
- feat: add planner agent that drafts structured plans (273780a)
- feat: add navigator skill for intent and skill routing (4a10e33)
- feat: port prep-kit delivery-loop strengths into base kit (715c46f)
- feat: add remove command to un-add a pack (3788aba)
- feat: add cross-model codex review command (9aed69d)
- feat: add tester agent, spec flow, and standalone review (67e8a38)
- feat: prefix slash commands with flex- to avoid host collisions (ccedf73)
- feat: add plan status and close slash commands (2cca4fe)
- feat: add user-prompt reminder and compaction re-orient (0b7a5d7)
- feat: bundle autonomous implement command (e29a02d)
- feat: add session-start and pre-tool hooks (7fdf240)
- feat: add command capability type (088f6e3)
- feat: add delivery modes with escalation (ce1d863)
- feat: add plan lifecycle commands (6b43ef8)
- feat: add pack install command (ce42366)
- feat: add api-design pack (686029f)
- feat: bundle verify-fix-loop orchestration starter (717cc04)
- feat: add skill-contract validation check (aa47a8f)
- feat: add init command with bundled starter template (deaf761)
- feat: generate per-host agent surfaces (72d57ab)
- feat: single-source skill kit generating claude and codex surfaces (f20c67d)

### Bug Fixes

- fix: keep verify-fix-loop handoffs and reports under the plan dir (db0e94f)
- fix: point skill guidance at the injected catalog, not 'installed packs' (f359a6a)
- fix: target codex skills at .agents/skills (6c9b197)

### Documentation

- docs: relax the skill-creator size guidance to ~250 lines (1fa1a2d)
- docs: codify writing principles and progressive disclosure in skill-creator (8b9a9e6)
- docs: align flex-docs guidance with the injected agent roster (b3e0440)
- docs: define doc kinds and content-driven inject routing in flex-docs (26e9cde)
- docs: add good/bad doc examples to flex-docs (066aba9)
- docs: correct CLAUDE.md module map and the inject-signal guide (ee922ac)
- docs: document the project docs index feature (e002548)
- docs: refresh getting-started for --all, front-door plan, and re-init (ab48b96)
- docs: add runnable demo scenarios (2a82d7a)
- docs: reflect delivery upgrades and clarify plan-lifecycle roles (65a0b04)
- docs: translate workflow docs to vietnamese (49b7381)
- docs: document codex-review workflow (848b826)
- docs: document each workflow flow in detail (5e1246c)
- docs: make how-to-use guide slash-command-first (54cc4cb)
- docs: add step-by-step how-to-use guide (3a1870c)
- docs: update for full os clone scope (c4c47f1)
- docs: document concept in readme and claude.md (34cd44a)
- docs: add prepkit concept spec blueprint (409f2bc)

### Refactoring

- refactor: keep transient handoffs at the repo root (c7671da)
- refactor: omit empty skills/docs sections from agent prompts (03cf3b1)
- refactor: slim the agent skills catalog to domain names (c67758f)
- refactor: prefix base skills with process- (b09b154)
- refactor: keep discipline skills language-agnostic with sharper descriptions (17265c2)
- refactor: split the engineering pack into architecture and engineering (0a0ab56)
- refactor: rename the api-design pack to backend with a backend-restful-api skill (579e75b)
- refactor: convert skill-creator skill into the flex-skill-creator command (8abbcd0)
- refactor: shorten injected skill catalog to lead clause (6fbd931)
- refactor: generalize host adapters to capability emitters (e0db70c)

### Styles

- style: tighten the docs skeleton descriptions (2de6b35)
- style: tighten planner agent prose (cc45a11)

### Other

- first commit (bf3fd5a)

**Contributors:** @Nguyễn Văn Hảo

