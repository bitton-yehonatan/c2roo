# c2roo CI/CD Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a complete GitHub Actions CI/CD pipeline to c2roo with lint, typecheck, test, build gates on PRs, and automated semantic-release → PyPI publishing with a manual approval gate.

**Architecture:** Two workflows (`ci.yml` for quality gates, `release.yml` for versioning and publishing) plus a shared composite action for setup. Configuration lives in `pyproject.toml`. Version management via python-semantic-release + Conventional Commits. PyPI publishing via OIDC Trusted Publishing (no tokens).

**Tech Stack:** GitHub Actions, UV, Ruff, Mypy (strict), python-semantic-release, PyPI Trusted Publishing (OIDC), pytest.

**Spec:** `docs/superpowers/specs/2026-04-12-cicd-pipeline-design.md`

**Important sequencing note:** Tasks must run in order. Mypy strict (Task 3) will likely surface many errors; do not skip the discovery step. Tasks 8–10 configure things on GitHub.com and pypi.org and cannot be done via code — they require manual action by the repo owner.

---

## Task 1: Add dev dependencies

Adds `ruff`, `mypy`, `python-semantic-release`, and `types-PyYAML` to the dev dependency group so downstream tasks can use them.

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: Add the dev dependencies via UV**

Run:
```bash
uv add --dev ruff mypy python-semantic-release types-PyYAML
```

Expected: `uv.lock` and `pyproject.toml` updated. The `[dependency-groups]` `dev` list now contains the four new packages in addition to the existing `pytest` and `pytest-cov`.

- [ ] **Step 2: Verify each tool is callable**

Run:
```bash
uv run ruff --version
uv run mypy --version
uv run semantic-release --version
```

Expected: All three commands print version strings, no errors.

- [ ] **Step 3: Commit**

```bash
git add pyproject.toml uv.lock
git commit -m "chore: add ruff, mypy, semantic-release, types-PyYAML as dev deps"
```

---

## Task 2: Configure and apply Ruff

Adds Ruff configuration to `pyproject.toml`, runs the checker + formatter, and fixes any issues so the codebase is clean before CI enforces it.

**Files:**
- Modify: `pyproject.toml`
- Modify: any files under `src/c2roo/` and `tests/` that ruff flags

- [ ] **Step 1: Add Ruff config to `pyproject.toml`**

Append this section to `pyproject.toml` (near the other `[tool.*]` sections):

```toml
[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM"]

[tool.ruff.lint.per-file-ignores]
"tests/**" = ["B"]  # allow bare asserts and common test patterns
```

- [ ] **Step 2: Run Ruff check to see current state**

Run:
```bash
uv run ruff check .
```

Expected: Either "All checks passed!" OR a list of violations. If violations exist, continue to step 3. If zero violations, skip to step 4.

- [ ] **Step 3: Auto-fix what can be fixed, manually fix the rest**

Run:
```bash
uv run ruff check --fix .
```

Then re-run `uv run ruff check .`. For any remaining violations, open each file and fix manually. Common leftovers are `B008` (mutable default args) and unused variables — fix them by changing the signature / removing the variable, not by adding `# noqa`.

Re-run until `uv run ruff check .` prints "All checks passed!".

- [ ] **Step 4: Run Ruff format**

Run:
```bash
uv run ruff format .
```

Expected: Either "N files reformatted, M files already formatted" or "M files already formatted". Either is fine.

- [ ] **Step 5: Verify format check passes**

Run:
```bash
uv run ruff format --check .
```

Expected: "M files already formatted" with exit code 0.

- [ ] **Step 6: Run the test suite to confirm nothing broke**

Run:
```bash
uv run pytest tests/ -v
```

Expected: All 70 tests pass.

- [ ] **Step 7: Commit**

```bash
git add -A
git commit -m "chore: configure ruff and apply lint/format fixes"
```

---

## Task 3: Configure Mypy strict and fix all errors

Adds strict mypy configuration and fixes every type error it surfaces. This is the biggest task in the plan — scope is unknown until you run mypy.

**Files:**
- Modify: `pyproject.toml`
- Modify: any files under `src/c2roo/` that mypy flags (likely many)

- [ ] **Step 1: Add Mypy config to `pyproject.toml`**

Append to `pyproject.toml`:

```toml
[tool.mypy]
python_version = "3.12"
strict = true
files = ["src/c2roo"]
ignore_missing_imports = true
```

- [ ] **Step 2: Run mypy to discover scope of work**

Run:
```bash
uv run mypy src/c2roo 2>&1 | tee /tmp/mypy-initial.txt
```

Count the errors:
```bash
grep -c "error:" /tmp/mypy-initial.txt || echo "0"
```

Expected: Some number N of errors. Note N — this is your work list.

- [ ] **Step 3: Decide on scope**

If N ≤ 50: proceed to fix them all in this task.

If N > 50: stop and report back. The plan may need adjustment (e.g., split into per-module fix tasks, or temporarily relax to non-strict and file a follow-up). Do not silently dump `# type: ignore` comments everywhere — that defeats the purpose of adding mypy.

- [ ] **Step 4: Fix errors one module at a time**

For each module flagged by mypy, open it and add type annotations. Prefer:
- Explicit function signatures: `def foo(x: str) -> int:`
- `list[T]`, `dict[K, V]`, `T | None` (PEP 604) — target is 3.12
- `from collections.abc import Iterable, Mapping` for abstract containers
- Dataclasses: annotate fields directly
- `TypedDict` for dict-shaped data with known keys (e.g., parsed YAML frontmatter)

Avoid:
- Bare `Any` — use `object` or a proper type
- Blanket `# type: ignore` — always use `# type: ignore[specific-code]` with a comment explaining why
- Changing runtime behavior to satisfy mypy — if the code is correct and mypy is wrong, use a narrow ignore

After each module is clean, run `uv run mypy src/c2roo` and verify the error count drops.

- [ ] **Step 5: Verify mypy passes with zero errors**

Run:
```bash
uv run mypy src/c2roo
```

Expected: `Success: no issues found in N source files`

- [ ] **Step 6: Re-run tests to confirm no behavior change**

Run:
```bash
uv run pytest tests/ -v
```

Expected: All 70 tests pass.

- [ ] **Step 7: Re-run ruff to catch any drift from type-annotation edits**

Run:
```bash
uv run ruff check .
uv run ruff format --check .
```

Expected: Both pass.

- [ ] **Step 8: Commit**

```bash
git add -A
git commit -m "chore: add mypy strict config and fix all type errors"
```

---

## Task 4: Add semantic-release config to `pyproject.toml`

Configures python-semantic-release to track versions in `pyproject.toml` and `src/c2roo/__init__.py`, emit a changelog, and create GitHub Releases.

**Files:**
- Modify: `pyproject.toml`

Note: `src/c2roo/__init__.py` already contains `__version__ = "0.1.0"` (verified during planning). No change needed there.

- [ ] **Step 1: Add semantic-release config**

Append to `pyproject.toml`:

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

[tool.semantic_release.changelog]
template_dir = "templates"
changelog_sections = [
    { type = "feat", section = "Features" },
    { type = "fix", section = "Bug Fixes" },
    { type = "perf", section = "Performance" },
    { type = "refactor", section = "Refactoring" },
    { type = "docs", section = "Documentation" },
]
```

- [ ] **Step 2: Validate the config with a dry run**

Run:
```bash
uv run semantic-release version --print --no-commit --no-tag --no-push
```

Expected: Prints the next version it would compute (likely `0.1.0` if no `feat:`/`fix:` commits have happened since the version was set, or a bumped version if they have). No errors. No files modified.

Verify no files were changed:
```bash
git status
```

Expected: Only `pyproject.toml` shown as modified (from step 1), nothing else.

- [ ] **Step 3: Run the full quality gate locally to confirm nothing regressed**

Run:
```bash
uv run ruff check . && uv run ruff format --check . && uv run mypy src/c2roo && uv run pytest tests/ -v
```

Expected: All four pass.

- [ ] **Step 4: Commit**

```bash
git add pyproject.toml
git commit -m "chore: configure python-semantic-release"
```

---

## Task 5: Create the shared setup composite action

Extracts checkout + UV install + sync into a reusable composite action so `ci.yml` and `release.yml` don't duplicate it.

**Files:**
- Create: `.github/actions/setup/action.yml`

- [ ] **Step 1: Create the directory and file**

Create `.github/actions/setup/action.yml` with:

```yaml
name: Setup c2roo
description: Checkout, install UV, and sync dependencies

runs:
  using: composite
  steps:
    - name: Install UV
      uses: astral-sh/setup-uv@v3
      with:
        enable-cache: true

    - name: Set up Python
      run: uv python install 3.12
      shell: bash

    - name: Sync dependencies
      run: uv sync --all-extras --dev
      shell: bash
```

Note: Checkout is NOT in the composite action. Checkout must happen in the calling workflow *before* invoking the composite (composite actions cannot use `actions/checkout` cleanly because they run against the already-checked-out workspace).

- [ ] **Step 2: Verify YAML syntax is valid**

Run:
```bash
uv run python -c "import yaml; yaml.safe_load(open('.github/actions/setup/action.yml'))"
```

Expected: No output, exit code 0.

- [ ] **Step 3: Commit**

```bash
git add .github/actions/setup/action.yml
git commit -m "ci: add shared setup composite action"
```

---

## Task 6: Create the CI workflow

Creates `ci.yml` with four parallel jobs: lint, typecheck, test, build. This is the quality gate that runs on every PR and push to main.

**Files:**
- Create: `.github/workflows/ci.yml`

- [ ] **Step 1: Create the workflow file**

Create `.github/workflows/ci.yml` with:

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: ./.github/actions/setup
      - name: Ruff check
        run: uv run ruff check .
      - name: Ruff format check
        run: uv run ruff format --check .

  typecheck:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: ./.github/actions/setup
      - name: Mypy
        run: uv run mypy src/c2roo

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: ./.github/actions/setup
      - name: Pytest
        run: uv run pytest tests/ -v

  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: ./.github/actions/setup
      - name: Build sdist and wheel
        run: uv build
      - name: Smoke test installed CLI
        run: |
          uv tool install --from "$(ls dist/*.whl)" c2roo
          c2roo --help
      - name: Upload build artifacts
        uses: actions/upload-artifact@v4
        with:
          name: dist
          path: dist/
          retention-days: 7
```

- [ ] **Step 2: Verify YAML syntax**

Run:
```bash
uv run python -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml'))"
```

Expected: No output, exit code 0.

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/ci.yml
git commit -m "ci: add CI workflow with lint, typecheck, test, build jobs"
```

---

## Task 7: Create the release workflow

Creates `release.yml` which runs after CI succeeds on `main`, invokes semantic-release, and publishes to PyPI via OIDC (gated by a GitHub Environment).

**Files:**
- Create: `.github/workflows/release.yml`

- [ ] **Step 1: Create the workflow file**

Create `.github/workflows/release.yml` with:

```yaml
name: Release

on:
  workflow_run:
    workflows: ["CI"]
    types: [completed]
    branches: [main]

jobs:
  release:
    # Only run if the triggering CI workflow succeeded
    if: ${{ github.event.workflow_run.conclusion == 'success' }}
    runs-on: ubuntu-latest
    permissions:
      contents: write
    outputs:
      released: ${{ steps.semrel.outputs.released }}
      version: ${{ steps.semrel.outputs.version }}
      tag: ${{ steps.semrel.outputs.tag }}
    steps:
      - uses: actions/checkout@v4
        with:
          ref: main
          fetch-depth: 0
          token: ${{ secrets.GITHUB_TOKEN }}

      - uses: ./.github/actions/setup

      - name: Run semantic-release
        id: semrel
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          set -e
          # Determine next version without committing
          CURRENT=$(uv run semantic-release version --print 2>/dev/null || true)
          PREV=$(grep -E '^version = ' pyproject.toml | head -1 | cut -d'"' -f2)
          echo "Current version in repo: $PREV"
          echo "Next version from semantic-release: $CURRENT"
          if [ -z "$CURRENT" ] || [ "$CURRENT" = "$PREV" ]; then
            echo "No release needed."
            echo "released=false" >> "$GITHUB_OUTPUT"
            exit 0
          fi
          # Perform the release
          uv run semantic-release version
          uv run semantic-release publish
          echo "released=true" >> "$GITHUB_OUTPUT"
          echo "version=$CURRENT" >> "$GITHUB_OUTPUT"
          echo "tag=v$CURRENT" >> "$GITHUB_OUTPUT"

  publish:
    needs: release
    if: ${{ needs.release.outputs.released == 'true' }}
    runs-on: ubuntu-latest
    environment:
      name: pypi
      url: https://pypi.org/project/c2roo/${{ needs.release.outputs.version }}
    permissions:
      id-token: write
      contents: read
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ needs.release.outputs.tag }}

      - uses: ./.github/actions/setup

      - name: Build distribution
        run: uv build

      - name: Publish to PyPI via Trusted Publishing
        run: uv publish
```

**Notes for the implementer:**
- `workflow_run` workflows run against the default branch's copy of the workflow file, not the commit that triggered them. This means changes to `release.yml` only take effect after they're merged to `main`.
- The `release` job checks out `main` at the tip (where the `workflow_run` fired) and needs full history for semantic-release.
- The `publish` job checks out the newly-created tag so `uv build` produces an artifact with the bumped version.
- `uv publish` uses OIDC automatically when `id-token: write` is granted and a Trusted Publisher is configured on PyPI.

- [ ] **Step 2: Verify YAML syntax**

Run:
```bash
uv run python -c "import yaml; yaml.safe_load(open('.github/workflows/release.yml'))"
```

Expected: No output, exit code 0.

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/release.yml
git commit -m "ci: add release workflow with semantic-release and PyPI OIDC publish"
```

---

## Task 8: Configure GitHub Environment `pypi` (manual, on github.com)

GitHub Environments cannot be configured via code in the repo — they must be set up in the repo settings UI.

**This task is a checklist for the repo owner, not code.**

- [ ] **Step 1: Navigate to environment settings**

Go to `https://github.com/<owner>/c2roo/settings/environments` and click "New environment".

- [ ] **Step 2: Create the environment**

- Name: `pypi`
- Click "Configure environment"

- [ ] **Step 3: Add required reviewer**

- Check "Required reviewers"
- Add yourself (repo owner) as a reviewer
- Save protection rules

- [ ] **Step 4: Confirm no deployment branch restriction is set**

Under "Deployment branches and tags", leave as "No restriction" (release.yml's `workflow_run` trigger already restricts to main).

- [ ] **Step 5: Verify**

Visit `https://github.com/<owner>/c2roo/settings/environments/pypi` and confirm the `pypi` environment exists with "Required reviewers: 1" shown.

---

## Task 9: Configure PyPI pending Trusted Publisher (manual, on pypi.org)

Since `c2roo` is not yet on PyPI, we use the pending publisher flow. This must be done before the first release.

**This task is a checklist for the repo owner, not code.**

- [ ] **Step 1: Log in to PyPI**

Go to `https://pypi.org` and log in (create an account if needed).

- [ ] **Step 2: Navigate to pending publishers**

Account menu → "Your account" → "Publishing" tab, or directly: `https://pypi.org/manage/account/publishing/`.

- [ ] **Step 3: Add a pending publisher**

Under "Add a new pending publisher", fill in:
- PyPI Project Name: `c2roo`
- Owner: your GitHub username (the one that owns the c2roo repo)
- Repository name: `c2roo`
- Workflow name: `release.yml`
- Environment name: `pypi`

Click "Add".

- [ ] **Step 4: Verify**

The pending publisher appears in the list. It will convert to a normal Trusted Publisher automatically when the first release succeeds.

---

## Task 10: Configure branch protection (manual, on github.com)

Enforce the CI required checks via branch protection. This must happen after `ci.yml` has run at least once on `main` (otherwise GitHub doesn't know the check names exist yet).

**This task is a checklist for the repo owner, not code.**

- [ ] **Step 1: Push all prior tasks to main**

At this point, Tasks 1–7 should be merged to main (via PR so CI actually runs). CI should have completed at least one successful run on main so the check names `lint`, `typecheck`, `test`, `build` are known to GitHub.

Verify by going to `https://github.com/<owner>/c2roo/actions` and confirming a green CI run on main.

- [ ] **Step 2: Navigate to branch protection**

Go to `https://github.com/<owner>/c2roo/settings/branches` and click "Add branch ruleset" (or "Add rule" depending on GitHub UI version).

- [ ] **Step 3: Configure the rule**

- Branch name pattern: `main`
- Enable: "Require a pull request before merging"
- Enable: "Require status checks to pass"
  - Enable: "Require branches to be up to date before merging"
  - Add required checks: `lint`, `typecheck`, `test`, `build`
- Enable: "Require linear history"
- Enable: "Do not allow bypassing the above settings" (optional; enable once you trust the pipeline)
- Disable: force pushes, deletions (these should be off by default)

- [ ] **Step 4: Save**

Click "Create" / "Save changes".

- [ ] **Step 5: Verify**

Try to push a trivial change directly to main from your local machine. Expected: push is rejected with a message about branch protection requiring a PR.

---

## Task 11: End-to-end smoke test

Validate the full pipeline with a deliberate test release.

- [ ] **Step 1: Create a test feature branch**

```bash
git checkout -b cicd-smoke-test
```

- [ ] **Step 2: Make a trivial `feat:` change**

Edit `README.md` to add a one-line note to the features section (e.g., "Automated releases via CI/CD").

- [ ] **Step 3: Commit with a feat prefix**

```bash
git add README.md
git commit -m "feat: note automated release pipeline in README"
```

- [ ] **Step 4: Push and open PR**

```bash
git push -u origin cicd-smoke-test
gh pr create --title "feat: note automated release pipeline in README" --body "Smoke test for CI/CD pipeline."
```

- [ ] **Step 5: Watch CI run on the PR**

Expected: All four jobs (`lint`, `typecheck`, `test`, `build`) run and pass. The PR shows green checks.

- [ ] **Step 6: Merge the PR**

Use a merge strategy compatible with linear history (squash or rebase). Do not use a merge commit.

```bash
gh pr merge --squash --delete-branch
```

- [ ] **Step 7: Watch the Release workflow trigger**

Go to `https://github.com/<owner>/c2roo/actions` and watch:
1. `CI` runs on main push → succeeds
2. `Release` workflow triggers via `workflow_run` → `release` job runs
3. semantic-release bumps version from `0.1.0` → `0.2.0` (since we have a `feat:` commit)
4. A tag `v0.2.0` is created
5. A GitHub Release is created with changelog excerpt
6. The `publish` job starts and pauses on the `pypi` environment approval gate

- [ ] **Step 8: Approve the PyPI publish**

In the Actions UI, click into the paused `publish` job and click "Review deployments" → check `pypi` → "Approve and deploy".

Expected: `publish` job resumes, builds the wheel at v0.2.0, and uploads to PyPI via OIDC.

- [ ] **Step 9: Verify on PyPI**

Visit `https://pypi.org/project/c2roo/` and confirm version 0.2.0 is listed.

- [ ] **Step 10: Verify pending publisher converted**

Visit `https://pypi.org/manage/project/c2roo/settings/publishing/` and confirm the pending publisher is now a regular Trusted Publisher attached to the project.

- [ ] **Step 11: Verify `CHANGELOG.md` was created**

Pull main and check:

```bash
git pull origin main
cat CHANGELOG.md
```

Expected: `CHANGELOG.md` exists with an entry for 0.2.0 listing the `feat:` commit.

---

## Self-review notes

**Spec coverage check:**
- Goals 1–5 from spec → covered by Tasks 2, 3, 6, 7 (CI gates) and Tasks 4, 7, 9 (automated release to PyPI with OIDC and approval gate). ✓
- Non-goals → respected; no multi-Python, multi-OS, TestPyPI, Docker, or docs deployment. ✓
- Architecture (two workflows + composite action) → Tasks 5, 6, 7. ✓
- `pyproject.toml` config additions (ruff, mypy, semantic-release, dev deps) → Tasks 1, 2, 3, 4. ✓
- `src/c2roo/__init__.py` `__version__` → already present (verified); spec's requirement is satisfied without code change. Task 4 step 1 still references it so semantic-release tracks it.
- Branch protection, GitHub Environment, PyPI pending publisher → Tasks 8, 9, 10. ✓
- Error handling / edge cases from spec → addressed by workflow structure (workflow_run gating, `if` conditions, environment approval). The smoke test (Task 11) validates the happy path end-to-end.
- Testing strategy from spec (test branch first, dry-run semrel, PyPI pending publisher before first release) → Tasks 4 (dry run), 9 (pending publisher), 11 (smoke test).
- Open risk: mypy strict error count unknown → Task 3 has an explicit discovery step and a stop-and-reconsider branch if N > 50.

**Placeholder scan:** No TBDs, no "handle edge cases", no "similar to Task N". Each task has exact commands and exact file contents.

**Type consistency:** Job names (`lint`, `typecheck`, `test`, `build`) are consistent across Tasks 6, 10, and 11. Environment name `pypi` is consistent across Tasks 7, 8, 11. Workflow file names (`ci.yml`, `release.yml`) are consistent.
