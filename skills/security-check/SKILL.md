---
name: security-check
description: >
  Pre-release security audit across five axes: leaked secrets, dependency
  vulnerabilities, input validation, auth/access control (Auth/RLS), and safe
  defaults — with a prioritized fix list. Use before every deploy/release,
  after adding auth or payments, when handling user data, or when the user
  says "security" / "audit" / "امنیت".
tools: Read, Grep, Glob, Bash
---

# Security Check

**Philosophy:** security is not "the last feature" — it is the release gate.
**Output is always:** a findings report with severity (CRITICAL/IMPORTANT/SUGGESTED) + a proposed fix per item.

## Execution Cycle (5 axes, ordered by risk severity)

### Axis 1 — Leaked secrets (worst kind of leak)
- Grep for patterns: API keys, tokens, passwords, private keys, connection strings.
  - Common signatures: `sk-`, `ghp_`, `AKIA`, `-----BEGIN`, `postgres://user:pass@`
- Dangerous files tracked in git: `.env`, `*.pem`, `credentials*`, configs with real values.
- Also check git HISTORY: e.g. `git log -p -S "SECRET"`.
- **Pass criterion:** no secret in the repo; everything comes from ENV / a secret manager.

### Axis 2 — Vulnerable dependencies
- Node: `npm audit --omit=dev` | Python: `pip-audit` or `pip list --outdated`.
- Flag unpinned or very old versions.
- **Pass criterion:** no open critical/high (or consciously recorded as accepted risk).

### Axis 3 — Input validation (injection)
| Vector | Check | Required fix |
|---|---|---|
| SQL | Queries built by string concatenation? | Parameterized queries / ORM only |
| Shell | `exec`/`system` with user input? | Allowlist or escape |
| Path | Opening files from user input? | Block `../` traversal |
| XSS | HTML output without escaping? (`dangerouslySetInnerHTML`, `|safe`, `v-html`) | Escape / sanitize |
- **Pass criterion:** no user input reaches SQL/shell/path/HTML directly.

### Axis 4 — Authentication & access control
- Does every sensitive endpoint have auth? (list all routes and tick them off)
- IDOR: can user A see user B's data by changing an id?
- Database RLS (if Supabase/Postgres): enabled on all user tables?
- Passwords: hashed with bcrypt/argon2 (never md5/sha1/plaintext).
- **Pass criterion:** access to every resource = its owner or an authorized role.

### Axis 5 — Safe defaults
- CORS: `*` on an authenticated endpoint? → restrict to explicit origins.
- Debug mode / stack traces OFF in production?
- HTTPS enforced? Cookies `Secure` + `HttpOnly` + `SameSite`?
- Rate limiting on login / public APIs? (if not → record as debt)
- Headers: `X-Content-Type-Options`, `X-Frame-Options` / CSP (web).

## Report Template (mandatory)

```
Security Check — Report [date]

CRITICAL (release BLOCKED until fixed):
  [S1] OpenAI key in src/config.py:12 -> move to ENV + ROTATE the key

IMPORTANT (fix before user growth):
  [S2] no rate limit on /login -> slowapi / express-rate-limit

SUGGESTED:
  [S3] add CSP header

PASSED: dependencies (0 high), parameterized SQL, bcrypt passwords
VERDICT: RELEASE BLOCKED (1 CRITICAL)   |   or: OK TO RELEASE
```

- Record every CRITICAL/IMPORTANT finding in STATE.md too (bug table or tech debt).
- Fixing a leaked secret = **move it + ROTATE the key** (removing it from code is not enough — it stays in git history).

## Anti-Patterns

1. **Report without a proposed fix** — every finding needs a one-line solution.
2. **Silently fixing CRITICALs without telling the user** — report first, fix after approval (key rotation is the user's call).
3. **Security theater** — adding 10 headers while skipping the IDOR check.
4. **"Once and done"** — this check repeats before EVERY release (SMART invokes it in Phase 4).
