# shared

The framework-free package (`@app/shared`) that both `frontend` and `backend` import.
Code here follows the coding standards imported below; the monorepo standard's rules for
the `shared` package decide what belongs here and how it is exported. The standards use a
placeholder users/projects/tasks domain; apply their patterns to this app's real
entities.

@../docs/standards/README.md
@../docs/standards/typescript.md
@../docs/standards/monorepo.md
@../docs/standards/logging-and-errors.md

## Read first when the task touches

- **Runtime APIs**: `process`, globals, timers, or anything that must behave the same in
  the browser and in Node. Read `docs/standards/nodejs.md` (NODE-5 to NODE-7).
- **Tests and test exports**: `*.test.ts`, `__tests__/`, custom matchers, fixtures, or the
  `@app/shared/testing` entry point. Read `docs/standards/testing.md`.
- **Real-time contract**: WebSocket event constants or message types. Read
  `docs/standards/websockets.md`.
- **Validation patterns used by forms and DTOs**: read `docs/standards/react.md`
  (REACT-11) and `docs/standards/nestjs.md` (NEST-24) so both consumers stay compatible.
- **Build or tool config**: `tsup.config.ts`, `package.json` `exports`,
  `tsconfig*.json`, or an `oxlint-disable` / `oxfmt-ignore` comment. Read
  `docs/standards/formatting-and-linting.md`.
