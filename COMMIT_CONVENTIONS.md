# Commit Conventions

Commit messages in this repository follow
[Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/), always with
a scope. The structure makes history scannable, lets tools derive changelogs and version
bumps, and makes each commit's intent clear before anyone opens the diff.

## Format

```txt
<type>(<scope>)[!]: <description>

[optional body]

[optional footer(s)]
```

```txt
feat(server): add project invite endpoint
fix(client): keep task order stable after drag and drop
docs(standards): add testing standards
refactor(shared)!: rename TaskUpdate to TaskChange
```

## Type

The type says what kind of change the commit is. `feat` and `fix` come from the spec; the
others follow the widely used Angular convention.

| Type       | Use for                                                           | Version impact |
| ---------- | ----------------------------------------------------------------- | -------------- |
| `feat`     | a new user-facing capability                                      | minor          |
| `fix`      | a bug fix                                                         | patch          |
| `docs`     | documentation only                                                | none           |
| `refactor` | restructuring code without changing its behaviour                 | none           |
| `perf`     | a change made to improve performance                              | patch          |
| `test`     | adding or fixing tests only                                       | none           |
| `style`    | formatting only (whitespace, semicolons); no logic change         | none           |
| `build`    | build system, packaging, or dependencies (pnpm, tsup, Dockerfiles) | none           |
| `ci`       | CI configuration and scripts                                      | none           |
| `chore`    | maintenance that fits nowhere else (renames, cleanup, config)     | none           |
| `revert`   | reverting an earlier commit                                       | depends        |

If a change seems to need two types, it is probably two commits.

## Scope

The scope is required and names the part of the repository the commit touches:

| Scope       | Area                                                     |
| ----------- | -------------------------------------------------------- |
| `client`    | the React app (`client/`)                                |
| `server`    | the NestJS app (`server/`)                               |
| `shared`    | the shared package (`shared/`)                           |
| `standards` | coding standards (`docs/standards/`)                     |
| `docs`      | other documentation (`docs/`, READMEs)                   |
| `docker`    | Compose files, Dockerfiles, reverse proxy                |
| `deps`      | dependency additions, upgrades, and removals             |
| `repo`      | root-level configuration and repository meta files       |

Use one scope per commit. A change that genuinely spans several workspaces uses the scope
of the area that drives it (for example, a new shared event used by client and server is
`shared`). If no single area drives it, split the commit.

## Description

- Use the imperative mood: "add", "fix", "rename" (not "added" or "adds").
- Start with a lowercase letter, and do not end with a period.
- Keep the whole subject line (type, scope, and description) to 72 characters or fewer.
- Say what the commit does, not how; the diff shows how.

## Body

Add a body when the reason for the change isn't obvious from the subject. Separate it from
the subject with a blank line, wrap it at 72 characters, and explain **why** the change
was made and what it affects.

## Footers

Footers go after the body, one per line, in `Token: value` form:

- `Refs: #123` or `Closes: #123` to link issues.
- `BREAKING CHANGE: <description>` for any change that breaks a public contract (API
  shape, event payload, config format). Also mark the subject with `!` after the scope.
- `Co-Authored-By: Name <email>` for shared authorship.

## Atomic commits

Each commit contains one logical change and leaves the repository in a working state.

- A refactor and the feature built on it are two commits.
- File moves and renames go in their own commit, separate from content changes.
- Formatting-only changes (`style`) never ride along with logic changes.

## Pull requests

PRs are squash-merged. The PR title becomes the commit on `main`, so it follows this same
format. The standards in [docs/standards/git-workflow.md](docs/standards/git-workflow.md)
cover branches and PRs.
