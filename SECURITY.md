# Security Policy

Visual Search Ranking is proprietary software (see [LICENSE](LICENSE)) developed by Axonity Solutions Inc. This policy applies to this repository and its deployed demo/staging/production instances.

## Reporting a Vulnerability

If you discover a security vulnerability, report it privately — do not open a public GitHub issue.

Email: anuragparcha315@gmail.com

Please include:
- A description of the vulnerability and its potential impact
- Steps to reproduce (proof-of-concept code or requests if applicable)
- The component affected

You should receive an acknowledgment within a reasonable timeframe. Please allow time to investigate and remediate before any public disclosure.

## Supported Versions

This project does not yet maintain multiple released versions. Security fixes are applied to `main` and the active development branch only.

## Security Posture

- Secrets (API keys, DB credentials, signing keys) are environment-variable/`.env`-based, gitignored, and never committed — see `CONTRIBUTING.md` and `docs/postmortems/0001-secret-leak-2026-08-06.md` for why this is non-negotiable.
- Pre-commit secret scanning (`.pre-commit-config.yaml`) and GitHub push protection (where the plan tier supports it — see `ENGINEERING_STANDARDS.md` §11) both run before code reaches the remote.
- Parameterized queries / ORM only — no raw string-interpolated SQL.
- Input validation on all external-facing inputs (API request bodies, form input) before it reaches business logic.
- Dependency vulnerabilities tracked via GitHub Dependabot alerts (`.github/dependabot.yml`).

## Known Limitations

This is an actively developed project. Report anything that looks like a gap between this document and actual behavior.
