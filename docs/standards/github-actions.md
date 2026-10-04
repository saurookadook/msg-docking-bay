# GitHub Actions Standards

Applies to everything under `.github/workflows/` and `.github/actions/`: how workflows are
laid out, named, triggered, and secured. What each workflow checks lives in
[ci-pipeline.md](ci-pipeline.md); image builds and publishing live in
[docker-and-environment.md](docker-and-environment.md) (ENV-26 to ENV-30).

**Source of truth:** `.github/workflows/`, `.github/actions/`.

**Origin.** These rules come from the workflows in the `aoam-property-plan` repository,
adapted to this monorepo. Where a rule departs from that repository, it says why. Rules
with no counterpart there fill gaps it left open.

---

## Layout and naming

**GHA-1 — Split each CI area into thin trigger workflows and one reusable workflow that
does the work:**

```txt
.github/
  actions/
    node-setup/action.yml          composite: pnpm, Node, install, build shared
  workflows/
    frontend-ci-trigger-pr.yml     on: pull_request   → uses frontend-test.yml
    frontend-ci-trigger-main.yml   on: push to main   → uses frontend-test.yml
    frontend-test.yml              on: workflow_call  → the jobs and steps
    backend-ci-trigger-pr.yml
    backend-ci-trigger-main.yml
    backend-test.yml
    shared-ci-trigger-pr.yml
    shared-ci-trigger-main.yml
    shared-test.yml
    repo-ci-trigger-pr.yml
    repo-ci-trigger-main.yml
    repo-lint.yml
```

A trigger workflow decides _when_ CI runs and _with what permissions_. It holds one job
that `uses:` the reusable workflow, and nothing else. The reusable workflow decides _what_
runs, and it is the only place steps live. A new trigger (a schedule, a manual run) is a
new trigger file that calls the same reusable workflow, never a copy of its steps.

**GHA-2 — An area is a commit scope that has something to check**
([COMMIT_CONVENTIONS.md](../../COMMIT_CONVENTIONS.md)): `frontend`, `backend`, `shared`,
`repo` (repo-wide checks such as formatting and lint), and `docker` (image builds,
ENV-28).

**GHA-3 — File names are kebab-case and end in `.yml`:**

| File              | Pattern                                   | Example                                 |
| ----------------- | ----------------------------------------- | --------------------------------------- |
| trigger workflow  | `<area>-ci-trigger-<when>.yml`            | `backend-ci-trigger-pr.yml`             |
| reusable workflow | `<area>-<task>.yml`                       | `frontend-test.yml`, `repo-lint.yml`    |
| composite action  | `.github/actions/<kebab-name>/action.yml` | `.github/actions/node-setup/action.yml` |

`<when>` is `pr`, `main`, `schedule`, or `manual`. Use `.yml`, never `.yaml`, for every
file under `.github/`.

**GHA-4 — Workflow `name:` values follow one pattern**, because they are what the Actions
tab and the PR checks list show:

| File                             | `name:`                              |
| -------------------------------- | ------------------------------------ |
| `<area>-ci-trigger-pr.yml`       | `"<Area> CI Trigger: PR"`            |
| `<area>-ci-trigger-main.yml`     | `"<Area> CI Trigger: 'main' branch"` |
| `<area>-ci-trigger-schedule.yml` | `"<Area> CI Trigger: schedule"`      |
| `<area>-ci-trigger-manual.yml`   | `"<Area> CI Trigger: manual"`        |
| `<area>-<task>.yml`              | `"<Area> <Task>"` (`"Frontend Test"`) |

`<Area>` is the area in title case. Quote every `name:` value in workflows and actions.

---

## Triggers and path filters

**GHA-5 — PR triggers use `pull_request` with no branch filter; main triggers use `push`
with `branches: ["main"]`.** Schedules use `schedule` with a comment giving the cron
expression in words, and manual runs use `workflow_dispatch`.

**GHA-6 — The trigger files of one area use the same `paths` list, copied exactly.** Sort
the entries alphabetically so the two files are easy to compare, and put a comment above
`paths` naming the twin file. In `aoam-property-plan` the frontend PR trigger watched
`frontend/**` while the main trigger watched a narrower list, so a change to
`frontend/index.html` was tested on the PR and never on `main`.

**GHA-7 — A `paths` list names everything the area's result depends on, and only
positively:**

- the area's own workspace: `<area>/**`
- every workspace it depends on ([monorepo.md](monorepo.md) MONO-3): `shared/**` for
  `frontend` and `backend`
- root files that change installs or tooling: `package.json`, `pnpm-lock.yaml`,
  `pnpm-workspace.yaml`, `.nvmrc`, and root `tsconfig*.json`
- for areas tested in Docker: `compose.yaml`, `.dockerignore`, and the `.env*.example`
  templates
- its own CI files: `.github/workflows/<area>-*.yml`, and `.github/actions/<name>/**`
  for every composite action it uses

Watch directories (`backend/**`), not file extensions. An extension list misses new file
types: the `aoam-property-plan` backend list named `*.py`, `*.toml`, and similar, so a
change to `backend/Dockerfile`, which the backend tests build, ran no tests. Do not use
negated patterns (`"!.github/workflows/frontend-*.yml"`) to exclude other areas'
workflows. Every new area would need another exclusion in every other trigger, and a
missed one runs the wrong suite.

```yaml
name: "Frontend CI Trigger: PR"

on:
  pull_request:
    # Keep identical to frontend-ci-trigger-main.yml (GHA-6).
    paths:
      - ".github/actions/node-setup/**"
      - ".github/workflows/frontend-*.yml"
      - ".nvmrc"
      - "frontend/**"
      - "package.json"
      - "pnpm-lock.yaml"
      - "pnpm-workspace.yaml"
      - "shared/**"
      - "tsconfig.json"

permissions: {}

concurrency:
  group: ${{ github.workflow }}-${{ github.event.pull_request.number }}
  cancel-in-progress: true

jobs:
  test:
    permissions:
      contents: read
      pull-requests: write # coverage report comment (CI-6)
    uses: ./.github/workflows/frontend-test.yml
```

**GHA-8 — A path-filtered workflow MUST NOT be a required status check.** A workflow that
`paths` skips never reports, so a required check stays pending and blocks the merge. The
`repo` area has no path filter (CI-10), so it can be required. Making another area required
is a deliberate change to this standard: move that area's change detection into its jobs,
inside a workflow with no path filter.

---

## Reusable workflows and permissions

**GHA-9 — A reusable workflow is triggered by `on: workflow_call` only.** If it needs
values from the caller, it declares them as `inputs` and `secrets`. Callers pass secrets
by name and never use `secrets: inherit`.

**GHA-10 — Trigger workflows own permissions.** Every trigger file sets top-level
`permissions: {}`. Its calling job then grants exactly what the reusable workflow needs
for that event, with a comment on any grant beyond `contents: read`:

| Event         | Typical grant                                                 |
| ------------- | ------------------------------------------------------------- |
| PR            | `contents: read`; `pull-requests: write` for a report comment |
| `main`        | `contents: read`; `packages: write` only for an image push    |
| schedule/scan | `contents: read`; `security-events: write` only for uploads   |

Reusable workflows do not declare `permissions`. A called workflow can only narrow what
its caller granted, and a job that asks for more than that fails before it starts, so
declaring them in both places adds nothing but a second list to keep in sync.

---

## Jobs

**GHA-11 — Every job sets `runs-on: ubuntu-latest` and `timeout-minutes`.** Test and lint
jobs use `timeout-minutes: 15`. A job that needs longer gets a higher value with a comment
saying why. Without a timeout, a hung job holds a runner for GitHub's default of six hours.

**GHA-12 — Job IDs are kebab-case and name what the job does** (`test`, `typecheck`,
`lint`, `build`). In a trigger file, the calling job's ID matches the reusable workflow's
task (`test` calls `frontend-test.yml`). `aoam-property-plan`'s `backend-test.yml` named
its test job `build`, which made a test failure read as a build failure.

**GHA-13 — PR triggers cancel superseded runs; main triggers do not.** PR triggers set
`concurrency` grouped by workflow and PR number with `cancel-in-progress: true`
(GHA-7 example). Main triggers set no concurrency, so every commit on `main` gets a
result.

---

## Steps

**GHA-14 — Check out with `actions/checkout` and its default `ref`, and set
`persist-credentials: false`.** On `pull_request`, the default is the merge of the PR into
its base, so CI tests what would land. Do not override it with
`ref: ${{ github.head_ref || github.ref_name }}` as `aoam-property-plan` did: that tests
the branch tip without newer commits on `main`, and it cannot find a branch that lives in
a fork. Keep the token out of `.git/config` unless a later step pushes.

**GHA-15 — Every step has a `name:`.** Names are sentence case. A step that runs a check
starts with its phase emoji, so a failure is easy to find in the log:

| Emoji | Phase                       | Example                 |
| ----- | --------------------------- | ----------------------- |
| 🐳    | build images                | `"🐳 Build images"`     |
| 🍃    | start or prepare MongoDB    | `"🍃 Start database"`   |
| 🔎    | typecheck                   | `"🔎 Typecheck"`        |
| 🧹    | format check or lint        | `"🧹 Lint"`             |
| 🖊️    | run tests                   | `"🖊️ Run tests"`        |
| 📊    | report results or coverage  | `"📊 Report coverage"`  |

Setup and teardown steps (checkout, Node setup, creating env files, tear down) have no
emoji. `aoam-property-plan` used 🐘 for its Postgres step; this repository uses MongoDB,
so its database steps use 🍃.

**GHA-16 — Run commands from the repository root through root scripts**
([monorepo.md](monorepo.md) MONO-11): `pnpm frontend:base typecheck`, not
`cd frontend && pnpm typecheck`. Use a step's `working-directory:` only for a tool that
has to run inside a workspace (CI-6), and never `cd` inside `run:`.

**GHA-17 — Shell steps run in bash with errors on.** Every reusable workflow sets:

```yaml
defaults:
  run:
    shell: bash
```

An explicit `shell: bash` runs with `-eo pipefail`, so a failing command, including one
in the middle of a pipe, fails the step. Use `run: |` for more than one command. Never
turn errors off (`set +e`) except around a bounded retry loop that checks exit codes
itself and turns them back on straight after (GHA-23).

**GHA-18 — Never put a `${{ }}` expression from the event payload directly into `run:`.**
PR titles, branch names, and commit messages are attacker-controlled, and interpolating
them into a script allows command injection. Pass the value through `env:` and read it as
`"$NAME"`. Declare an `env` value only where something reads it. `aoam-property-plan`
declared `PR_NUMBER` at workflow level in both test workflows, and nothing used it.

**GHA-19 — Use `if:` conditions precisely, and never `continue-on-error` on a check.**

- A step that reports on another step runs when that step ran, whether it passed or
  failed: give the reported step an `id` and use
  `if: ${{ !cancelled() && steps.<id>.outcome != 'skipped' }}`. Plain `always()`, which
  `aoam-property-plan` used, also runs after setup failed and adds a second, misleading
  failure.
- A teardown step uses `if: always()`.
- A check that may fail without failing the job is not a check. Do not use
  `continue-on-error: true` or `|| true` on one.

**GHA-20 — Do not set up toolchains a job does not use.** A job that tests in Docker needs
only Docker, which the runner already has. `aoam-property-plan`'s backend job installed
Python on the runner even though its tests ran in a container.

---

## Composite actions

**GHA-21 — Setup that two or more workflows repeat lives in a composite action** under
`.github/actions/<name>/`, used by path (`uses: ./.github/actions/node-setup`) after
checkout. Its `name:` and `description:` say exactly what it does.
`aoam-property-plan`'s action said it installed npm dependencies, but it used pnpm.

**GHA-22 — Inside a composite action:**

- every step has a `name:`
- every `run` step sets `shell: bash` (composite actions require it, and they do not read
  workflow `defaults`)
- a value that differs between callers is an input with a default, not a hard-coded path
- inputs reach scripts through `env:`, not `${{ inputs.* }}` inside `run:` (GHA-18)

**GHA-23 — Retries are a last resort, bounded, and verified.** Only a step known to fail
for transient reasons (a dependency install) may retry, and never a test or check.
Make at most three attempts, and clean up state between attempts. Check that the step
actually worked, not just its exit code: `aoam-property-plan` found that pnpm could exit
`0` after crashing, so its install loop also checked that a known package had landed in
`node_modules`. After the last failed attempt, print an error to stderr and `exit 1`.

---

## Third-party actions

**GHA-24 — Pin every third-party action to a full commit SHA, with its release in a
comment, and let Dependabot update the pins** (ENV-24, ENV-27). `aoam-property-plan`
pinned to major tags (`@v4`), which their owners can move. Local actions
(`./.github/actions/...`) are versioned with the repository and need no pin. Prefer
actions from the tool's owner (`actions/*`, `docker/*`, `pnpm/*`). Add a community action
only when it replaces a meaningful amount of script, as the coverage reporter does
(CI-6).

**GHA-25 — Never run PR code with elevated access.** Do not use `pull_request_target` or
`workflow_run` to build or test a PR's code: both run with the base repository's secrets
and a writable token.

---

## Changing CI

**GHA-26 — A workflow change is tested by the workflow it changes.** GHA-7 puts each
area's own workflow files in its `paths`, so editing `frontend-test.yml` runs it on the
PR. Commit CI changes with type `ci`, scoped to the area the workflow serves
(`ci(frontend): report coverage on main`). Changes to shared actions or to more than one
area use `repo`.
