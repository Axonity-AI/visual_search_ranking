# Contributing to Visual Search Ranking

This is a proprietary Axonity project (see [LICENSE](LICENSE)). This guide documents the conventions the codebase follows, so they stay consistent as the team grows.

## Before you start

- Read the project's `README.md` for an overview and quickstart.
- Read `docs/architecture.md` before making structural changes.
- Skim `ENGINEERING_STANDARDS.md` (in the org's `_project-template`) for the full rationale behind these conventions.

## Branching

- `main` — always releasable. Nothing broken merges here.
- Short-lived branches only: `feat/<short-description>`, `fix/<short-description>`, branched from `main`, merged back within days via PR. No long-lived parallel branches — they drift, and reconciling them later costs far more than the discipline of merging often.

## Commits

- [Conventional Commits](https://www.conventionalcommits.org/): `feat:`, `fix:`, `chore:`, `docs:`, `refactor:`, `test:`, `ci:`, with an optional scope, e.g. `feat(frontend): add login page`. Enforced via the pre-commit commit-msg hook.
- Write the description in imperative mood ("add X", not "added X" or "adds X").
- No AI attribution trailers (e.g. `Co-Authored-By: Claude ...`) in commit messages, code, or docs.
- No emojis or non-standard characters in commits, code, or documentation.
- **Never commit `.env` files or secrets.** If one is ever committed, rotate the credential immediately, even if removed in a later commit — git history retains it until deliberately scrubbed. See `docs/postmortems/0001-secret-leak-2026-08-06.md` for why this rule exists.

## Pull requests vs. direct pushes

- Nothing merges to `main` without a PR, even solo — self-review still means reading your own diff as a reviewer would, and it leaves a record of what shipped and why.
- Use the PR template checklist before merging.
- CI (`.github/workflows/ci.yml`) must pass — lint, type-check, tests, and build are all required checks, not optional ones.

## Code quality bar

- Type hints/type annotations required for all functions (Python: type hints; TypeScript: no implicit `any`).
- Docstrings/comments explain *why*, not *what* — the code already says what it does.
- All external-facing inputs validated before reaching business logic.
- No hardcoded configuration — settings belong in environment variables or a config store, not magic strings/numbers in code.
- No temporary fix scripts or workarounds — find the root cause and fix it architecturally.

## Testing

- New features need tests under `tests/`, organized by feature/module.
- Target meaningful coverage on critical paths (auth, payments, data mutation), not 100% coverage everywhere.
- Run the test suite locally before pushing; CI runs the same suite on every push/PR and the coverage floor is enforced, not just reported.

## Documentation

- Update the relevant doc in `docs/` when behavior changes — stale docs cost more than no docs.
- Significant, hard-to-reverse technical decisions get an ADR in `docs/adr/` (see `docs/adr/0000-template.md`).
- Don't create new top-level `.md` files without a reason — check whether an existing doc already covers the topic first.
