# CI Pipeline Standards

Applies to what CI checks in each area: the shared setup action, the steps each reusable
workflow runs, and how results are reported. How workflows are laid out, triggered, and
secured lives in [github-actions.md](github-actions.md). Image builds, scanning, and
publishing live in [docker-and-environment.md](docker-and-environment.md) (ENV-26 to
ENV-30).

**Source of truth:** `.github/workflows/*-test.yml`, `.github/workflows/repo-lint.yml`,
`.github/actions/node-setup/action.yml`, root `package.json` scripts.

**Origin.** Drawn from the `aoam-property-plan` frontend and backend test workflows and
their setup action, adapted to this pnpm workspace, the NestJS and MongoDB backend, and
the `shared` package.

---

## What runs

**CI-1 — CI runs these checks:**

| Area       | Reusable workflow   | Where           | Checks                                                     |
| ---------- | ------------------- | --------------- | ---------------------------------------------------------- |
| `repo`     | `repo-lint.yml`     | runner          | format check, lint, workflow lint                          |
| `shared`   | `shared-test.yml`   | runner          | build, typecheck, tests with coverage                      |
| `frontend` | `frontend-test.yml` | runner          | typecheck, tests with coverage, coverage report            |
| `backend`  | `backend-test.yml`  | runner, Compose | typecheck on the runner; tests in `backend-test`           |
| `docker`   | `docker-build.yml`  | runner, Buildx  | production image build, scan, and push (ENV-26 to ENV-30)  |

A change to `shared` runs `shared`, `frontend`, and `backend`, because their path filters
include `shared/**` (GHA-7).

**CI-2 — CI runs the scripts developers run** (ENV-29). Each check is one root script
call, so a red check reproduces locally with the same command. If CI needs a new command,
add it as a script first. That means every workspace defines a `typecheck` script that
type-checks without emitting, and every workspace whose tests run on the runner
(`frontend`, `shared`) defines `test:cov`. The one exception is the backend `test` job
(CI-7), which runs the steps of the root `backend:test` script one at a time so each
phase has its own log section.

**CI-3 — Within a job, checks run cheapest first and stop at the first failure:** setup,
then 🔎 typecheck, then 🖊️ tests, then 📊 reports. Do not reorder steps to collect more
failures from one run. Fix the first failure, then push.

---

## Setup

**CI-4 — Every job that needs Node uses the `node-setup` composite action**, and no job
installs Node or pnpm any other way. The action:

1. Installs pnpm with `pnpm/action-setup` and no `version` input, so it reads the
   `packageManager` field of the root `package.json` ([nodejs.md](nodejs.md) NODE-2).
   Corepack is not needed on the runner. `aoam-property-plan` hard-coded the pnpm
   version in its action, which was a second copy of `packageManager` that could drift.
2. Sets up Node with `actions/setup-node` from the root `.nvmrc` (NODE-1), with
   `cache: pnpm` keyed on the root `pnpm-lock.yaml`. pnpm has to be installed first,
   because the cache step calls it to find its store.
3. Installs every workspace once, from the root, with `pnpm install --frozen-lockfile`.
   A lockfile that is out of date with a `package.json` fails here instead of resolving
   new versions in CI. Install scripts are already limited to `onlyBuiltDependencies`
   (NODE-3), so there is no separate `--ignore-scripts` install followed by
   `pnpm rebuild`, as there was in `aoam-property-plan`. If installs prove flaky, wrap
   this step in the bounded, verified retry of GHA-23. Do not add the retry
   preemptively.
4. Builds `shared` (`pnpm shared:base build`) unless the caller passes
   `build-shared: "false"`, because the typecheck, tests, and type-aware lint all import
   its built output ([monorepo.md](monorepo.md) MONO-8).

```yaml
name: "Node.js setup"
description: "Install pnpm and Node.js, install workspace dependencies, and build shared"

inputs:
  build-shared:
    description: "Build @app/shared after installing dependencies (MONO-8)"
    required: false
    default: "true"

runs:
  using: "composite"
  steps:
    - name: "Install pnpm"
      uses: pnpm/action-setup@<sha> # <release> (version comes from packageManager)

    - name: "Set up Node.js"
      uses: actions/setup-node@<sha> # <release>
      with:
        node-version-file: ".nvmrc"
        cache: "pnpm"
        cache-dependency-path: "pnpm-lock.yaml"

    - name: "Install dependencies"
      shell: bash
      run: pnpm install --frozen-lockfile

    - name: "Build shared"
      if: inputs.build-shared == 'true'
      shell: bash
      run: pnpm shared:base build
```

---

## Frontend

**CI-5 — `frontend-test.yml` runs one `test` job:** checkout, `node-setup`,
🔎 `pnpm frontend:base typecheck`, 🖊️ `pnpm frontend:base test:cov`, then the coverage
report. If the frontend has more than one `tsconfig` (for example a stricter one, as
`aoam-property-plan` did), its `typecheck` script checks all of them, and CI still calls
it once.

```yaml
name: "Frontend Test"

on:
  workflow_call:

defaults:
  run:
    shell: bash

jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - name: "Check out code"
        uses: actions/checkout@<sha> # <release>
        with:
          persist-credentials: false

      - name: "Set up Node.js and dependencies"
        uses: ./.github/actions/node-setup

      - name: "🔎 Typecheck"
        run: pnpm frontend:base typecheck

      - name: "🖊️ Run tests"
        id: tests
        run: pnpm frontend:base test:cov

      - name: "📊 Report coverage"
        # Report whether the tests passed or failed, but not if they never ran (GHA-19).
        if: ${{ !cancelled() && steps.tests.outcome != 'skipped' }}
        uses: davelosert/vitest-coverage-report-action@<sha> # <release>
        with:
          working-directory: ./frontend
          json-summary-path: ./coverage/coverage-summary.json
```

**CI-6 — Frontend coverage is reported with `davelosert/vitest-coverage-report-action`.**
The Vitest config MUST set `coverage.reporter` to include `json-summary` and `json`
(the action reads both), and `coverage.reportOnFailure: true`, so a report exists even
when tests fail. On a PR, the action comments on the PR, which is why the PR trigger
grants `pull-requests: write` (GHA-10). On `main`, it writes to the job summary.
Coverage thresholds, if any, live in the Vitest config, not in the workflow.

---

## Backend

**CI-7 — `backend-test.yml` runs two jobs in parallel:** `typecheck` on the runner and
`test` in Compose.

- `typecheck`: checkout, `node-setup`, then 🔎 `pnpm backend:base typecheck`.
- `test`: needs only Docker (GHA-20). It runs the root `backend:test` script's Compose
  commands one at a time, against the isolated `app-test` project
  ([docker-and-environment.md](docker-and-environment.md) ENV-4). These commands MUST
  match that script; change both in the same PR.

```yaml
jobs:
  # typecheck: checkout, node-setup, then 🔎 Typecheck (as in CI-5)

  test:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - name: "Check out code"
        uses: actions/checkout@<sha> # <release>
        with:
          persist-credentials: false

      - name: "Create env files from templates"
        run: |
          cp .env.example .env
          cp .env.test.example .env.test

      - name: "🐳 Build images"
        run: docker compose -p app-test --env-file .env.test build backend-test

      - name: "🍃 Start database"
        run: docker compose -p app-test --env-file .env.test up -d --wait mongo

      - name: "🖊️ Run tests"
        run: docker compose -p app-test --env-file .env.test run --rm backend-test

      - name: "Tear down"
        if: always()
        run: docker compose -p app-test --env-file .env.test down -v
```

**CI-8 — The backend job waits for the database with its Compose healthcheck**
(`up --wait`, ENV-11). Do not write a polling loop. `aoam-property-plan` looped on
`pg_isready` because its database service had no healthcheck. If the stack needs
generated local files (the MongoDB secrets of ENV-13, certificates), the job runs the same
setup script developers run, before it builds.

---

## Shared

**CI-9 — `shared-test.yml` runs one `test` job:** checkout, `node-setup` (whose
`shared` build is itself a check), 🔎 `pnpm shared:base typecheck`, and
🖊️ `pnpm shared:base test:cov`. Jest coverage stays in the log; the Vitest report action
(CI-6) does not apply to it.

---

## Repository-wide

**CI-10 — `repo-lint.yml` runs one `lint` job** with the repo-wide checks from
[formatting-and-linting.md](formatting-and-linting.md) FMT-11:

1. checkout and `node-setup` (the type-aware linter resolves `@app/shared` through its
   built types)
2. 🧹 `pnpm format:check`
3. 🧹 `pnpm lint --deny-warnings`
4. 🧹 workflow lint: `actionlint`, run from its `rhysd/actionlint` image pinned by
   version and digest (ENV-24), SHOULD check every file under `.github/`

The `repo` triggers have no `paths` filter. Formatting covers Markdown and config files
anywhere in the repository, and an unfiltered workflow is the only kind that can be a
required check (GHA-8).

---

## Failures and changes

**CI-11 — A red check blocks the merge.** Fix it or revert the change that broke it. A
flaky test is fixed, or skipped with a `// TODO:` that says why
([testing.md](testing.md) TEST-7), in its own PR. Never skip it by weakening the
workflow.

**CI-12 — Adding a workspace or an area** means: a trigger pair and a reusable workflow
for it (GHA-1); its path in the `paths` of every area that depends on it (GHA-7); a row
in the CI-1 table; and a `typecheck` script, plus `test:cov` if its tests run on the
runner (CI-2).
