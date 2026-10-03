# backend

The NestJS API and WebSocket gateway (`@app/backend`). Code here follows the coding
standards imported below. The standards use a placeholder users/projects/tasks domain;
apply their patterns to this app's real entities.

@../docs/standards/README.md
@../docs/standards/typescript.md
@../docs/standards/nodejs.md
@../docs/standards/nestjs.md
@../docs/standards/logging-and-errors.md

## Read first when the task touches

- **Database**: a `*.schema.ts` file, an injected model, or any Mongoose query. Read
  `docs/standards/mongoose.md`.
- **Tests**: `*.test.ts`, `test/*.e2e-test.ts`, `src/__mocks__/`, or
  `src/utils/testing/`. Read `docs/standards/testing.md`.
- **Real-time messaging**: a gateway in `src/**/events/`, socket rooms, or event
  payloads. Read `docs/standards/websockets.md`.
- **Dependencies**: `package.json`, adding a package, or importing from `@app/shared`.
  Read `docs/standards/monorepo.md`.
- **Container or env vars**: the Dockerfile, Compose service, `.env*` files, or the
  config factory. Read `docs/standards/docker-and-environment.md`.
- **Tool config or suppressions**: `nest-cli.json`, `tsconfig*.json`, or an
  `oxlint-disable` / `oxfmt-ignore` comment. Read
  `docs/standards/formatting-and-linting.md`.
