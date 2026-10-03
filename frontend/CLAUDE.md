# frontend

The React app (`@app/frontend`). Code here follows the coding standards imported below.
The standards use a placeholder users/projects/tasks domain; apply their patterns to this
app's real entities.

@../docs/standards/README.md
@../docs/standards/typescript.md
@../docs/standards/react.md
@../docs/standards/logging-and-errors.md

## Read first when the task touches

- **Styles**: any `.css` file, design tokens, or a component's class names. Read
  `docs/standards/css.md`.
- **Tests**: `*.test.tsx`, `src/__mocks__/`, or `src/utils/testing/`. Read
  `docs/standards/testing.md`.
- **Real-time messaging**: the WebSocket manager, socket message handlers, or event
  types. Read `docs/standards/websockets.md`.
- **Dependencies**: `package.json`, adding a package, or importing from `@app/shared`.
  Read `docs/standards/monorepo.md` and `docs/standards/nodejs.md`.
- **Container or env vars**: the Dockerfile, Compose service, or `import.meta.env` values.
  Read `docs/standards/docker-and-environment.md`.
- **Tool config or suppressions**: `vite.config.ts`, `tsconfig*.json`, or an
  `oxlint-disable` / `oxfmt-ignore` comment. Read
  `docs/standards/formatting-and-linting.md`.
