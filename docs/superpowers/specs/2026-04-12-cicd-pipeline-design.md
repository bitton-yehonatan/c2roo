# c2roo CI/CD Pipeline — Design Spec

**Date:** 2026-04-12
**Status:** Approved (design phase)
**Scope:** Add full CI/CD pipeline to c2roo using GitHub Actions

## Goals

1. Catch quality issues (lint, types, test failures) on every PR before merge
2. Verify the package builds and installs cleanly on every change
3. Automate version management and changelog generation from Conventional Commits
4. Publish releases to PyPI automatically, with a human approval gate as a safety net
5. Use modern best practices: Trusted Publishing (OIDC), no long-lived secrets

## Non-Goals

- Multi-Python-version testing (3.12 only for now)
- Multi-OS testing (Ubuntu only for now)
- TestPyPI staging (direct to PyPI with manual gate)
- Docker images, container publishing, or other distribution formats
- Documentation site deployment

## Architecture

Two GitHub Actions workflows, separated by concern:

- **`ci.yml`** — quality gates on every push/PR. Required checks for merge.
- **`release.yml`** — runs after CI passes on `main`. Automates versioning, changelog, and PyPI publish (with manual approval gate).

A shared composite action handles the repeated setup steps (checkout, install UV, sync deps).

```
.github/
├── workflows/
│   ├── ci.yml
│   └── release.yml
└── actions/
    └── setup/
        └── action.yml
```

## Workflow 1: CI (`ci.yml`)

**Triggers:**
- `push` to `main`
- `pull_request` targeting `main`

**Runner:** `ubuntu-latest`
**Python:** 3.12 (single version)

**Jobs** (all run in parallel, all required for merge):

### `lint`
- `uv run ruff check .`
- `uv run ruff format --check .`
- Blocks merge on failure.

### `typecheck`
- `uv run mypy src/c2roo`
- Strict mode enabled (`strict = true` in `pyproject.toml`).
- Blocks merge on failure.
- **Implementation note:** the codebase has never been type-checked under mypy strict. The implementation plan must sequence this carefully: add mypy config → fix all existing errors → land the `typecheck` job → *then* enable it as a required check in branch protection. The steady state is "all four jobs required"; the transition order matters so we don't block ourselves from merging the very PR that introduces the check.

### `test`
- `uv run pytest tests/ -v`
- Runs the existing 70-test suite.
- Blocks merge on failure.

### `build`
- `uv build` — produces sdist and wheel in `dist/`
- Smoke test: install the built wheel into a temp env and run `c2roo --help`
- Uploads `dist/` as a workflow artifact (for debugging; release workflow rebuilds its own)
- Blocks merge on failure.

**Shared setup** (composite action at `.github/actions/setup/action.yml`):
1. `actions/checkout@v4`
2. `astral-sh/setup-uv@v3` with caching enabled
3. `uv sync --all-extras --dev`

## Workflow 2: Release (`release.yml`)

**Trigger:** `workflow_run` — runs after `ci.yml` completes successfully on `main`.

This guarantees we never release code that failed CI.

**Permissions:**
- `contents: write` — semantic-release needs to commit version bumps, create tags, create GitHub Releases
- `id-token: write` — required for PyPI OIDC Trusted Publishing

### Job 1: `release`

Runs on `ubuntu-latest`.

Steps:
1. Checkout with `fetch-depth: 0` (semantic-release needs full history)
2. Run shared setup composite action
3. Run `uv run semantic-release version`:
   - Analyzes commits since last tag using Conventional Commits parser
   - `feat:` → minor bump; `fix:` → patch bump; `feat!:` / `BREAKING CHANGE:` → major bump
   - Updates `pyproject.toml` version field
   - Updates `src/c2roo/__init__.py` `__version__`
   - Generates/updates `CHANGELOG.md`
   - Commits changes to `main` with `[skip ci]` in the message
   - Creates git tag (e.g., `v0.2.0`)
   - Creates GitHub Release with changelog excerpt
4. If no release-worthy commits exist (only `docs:`, `chore:`, etc.), the job exits cleanly with `released=false` and `publish` is skipped

**Outputs:**
- `released` (bool)
- `version` (string, e.g., `0.2.0`)

### Job 2: `publish`

**Condition:** `needs: release` and `if: needs.release.outputs.released == 'true'`

**Environment:** `pypi` — this GitHub Environment has a required reviewer configured. The job pauses in the Actions UI until a maintainer clicks "Approve and deploy". This is the manual gate.

Steps:
1. Checkout at the tag semantic-release just created
2. Run shared setup composite action
3. `uv build` — rebuild fresh, since the version was bumped after CI ran (CI's artifact has the stale version)
4. `uv publish` — OIDC Trusted Publishing, no token needed

## Configuration Additions to `pyproject.toml`

### Ruff

```toml
[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM"]
```

### Mypy

```toml
[tool.mypy]
python_version = "3.12"
strict = true
files = ["src/c2roo"]
ignore_missing_imports = true
```

### Semantic Release

```toml
[tool.semantic_release]
version_toml = ["pyproject.toml:project.version"]
version_variables = ["src/c2roo/__init__.py:__version__"]
branch = "main"
changelog_file = "CHANGELOG.md"
upload_to_vcs_release = true
build_command = "uv build"
commit_parser = "conventional"
commit_message = "chore(release): {version} [skip ci]"
```

### Dev Dependencies

Add to the existing dev dependency group:
- `ruff`
- `mypy`
- `python-semantic-release`
- `types-PyYAML`

## Source Code Changes

**`src/c2roo/__init__.py`** — add `__version__ = "0.1.0"` so semantic-release can track it.

**Existing code** — fix all mypy strict errors that surface when `strict = true` is enabled. The count and nature of these errors is unknown until mypy is actually run; the implementation plan must include a discovery phase.

## Repository Configuration (Manual, Not in Code)

### Branch Protection Rules for `main`

Configured in GitHub repo Settings → Branches:
- Require pull request before merging
- Require status checks to pass: `lint`, `typecheck`, `test`, `build`
- Require branches to be up to date before merging
- Do not allow force pushes
- Do not allow deletions
- Require linear history (keeps commit log clean for Conventional Commits)

### GitHub Environment: `pypi`

Configured in GitHub repo Settings → Environments:
- Name: `pypi`
- Required reviewers: repo owner (Yehonatan Bitton)
- No deployment branch restrictions needed (release.yml only runs on main)

### PyPI Trusted Publisher (One-Time Setup)

**Chicken-and-egg problem:** PyPI's standard Trusted Publisher setup requires the project to already exist. Since `c2roo` is not yet on PyPI, we use the **pending publisher** flow:

1. Log in to PyPI
2. Account → Publishing → Add a new pending publisher
3. Fill in:
   - PyPI Project Name: `c2roo`
   - Owner: `<github-username>`
   - Repository name: `c2roo`
   - Workflow name: `release.yml`
   - Environment name: `pypi`
4. Save

The first successful `release.yml` run will register the project on PyPI under this publisher. Subsequent releases use the now-normal trusted publisher.

### Repository Secrets

**None required.** OIDC replaces API tokens entirely. This is the point of Trusted Publishing.

## Files Created

```
.github/workflows/ci.yml
.github/workflows/release.yml
.github/actions/setup/action.yml
CHANGELOG.md                    # created automatically by semantic-release on first release
```

## Files Modified

- `pyproject.toml` — add ruff, mypy, semantic-release config; add dev dependencies
- `src/c2roo/__init__.py` — add `__version__`
- Possibly many files under `src/c2roo/` — fix mypy strict errors

## Error Handling & Edge Cases

**No release-worthy commits on `main` push**
- semantic-release detects this, exits with `released=false`
- `publish` job is skipped via `if` condition
- No version bump, no tag, no release — normal behavior, not an error

**CI fails on `main` push**
- `workflow_run` trigger only fires on CI success
- Release workflow never starts
- Broken code cannot be released

**semantic-release commit push fails** (e.g., concurrent push to main)
- Job fails loudly
- No partial release state — tag is created only if push succeeds
- Manual recovery: re-run the release workflow

**Manual approval on `pypi` environment times out**
- GitHub Environments have a configurable wait timer (default: 30 days)
- Release tag already exists at this point (semantic-release ran in the previous job)
- Recovery: approve the job, or manually `uv publish` from the tag

**PyPI upload fails** (e.g., network, version already exists)
- Job fails
- Tag and GitHub Release already exist from the `release` job — out of sync with PyPI
- Recovery: fix the underlying issue, manually rerun the `publish` job (reruns from the existing tag)
- Prevention: the CI `build` job already verifies the package builds cleanly, so upload failures will almost always be environmental (network, PyPI outage) rather than a bad artifact

**mypy finds new errors after code change merges**
- This cannot happen: `typecheck` is a required check, PRs that introduce new errors cannot merge
- Pre-commit hook (future enhancement) would catch these even earlier

**Someone pushes directly to `main`** (bypassing PR)
- Branch protection prevents this for non-admins
- Admins can bypass, but this is a known trade-off
- If it happens and breaks CI, release.yml's `workflow_run` trigger prevents publishing

## Testing Strategy

Pipeline changes are hard to test locally — the feedback loop is "push and watch". To minimize that:

1. **Use a test branch first**: create `cicd-setup` branch, iterate on workflows there with `push` trigger temporarily pointing at that branch, verify each job works
2. **Use `act`** (optional) to run GitHub Actions locally where feasible; note `act` has limitations with OIDC and some marketplace actions
3. **Validate semantic-release dry-run**: `uv run semantic-release version --no-commit --no-tag --no-push` locally to preview what would happen
4. **Do the PyPI pending publisher setup before the first release attempt**, not after
5. **First real release** should be a deliberate test: merge one `feat:` commit, watch the whole pipeline run end-to-end, manually approve the PyPI publish

## Open Questions / Risks

- **mypy strict may surface many errors.** The implementation plan needs a discovery phase where mypy is run against the current codebase to assess scope before committing to strict-from-day-one. If the error count is unmanageable, we may need to fall back to non-strict initially (in which case this spec should be revised).
- **semantic-release behavior on first run** (no prior tags): it should treat `v0.1.0` in `pyproject.toml` as the baseline. Implementation should verify this with a dry run before the first real release.
- **`workflow_run` trigger quirks**: `workflow_run` workflows do not inherit the triggering workflow's permissions or secrets by default, and they run against the default branch's version of the workflow file, not the commit that triggered them. Implementation must account for this.

## Success Criteria

1. Every PR runs lint, typecheck, test, and build jobs; all four must pass before merge
2. Branch protection on `main` enforces the required checks
3. Pushing a `feat:` commit to `main` triggers an automated version bump, changelog update, tag, and GitHub Release
4. PyPI publish requires manual approval via the `pypi` environment
5. PyPI publish succeeds using OIDC Trusted Publishing (no tokens stored)
6. `CHANGELOG.md` accurately reflects release history in Keep-a-Changelog-ish format
7. Zero long-lived secrets in the repo
