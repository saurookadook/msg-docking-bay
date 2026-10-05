# Testing Standards

Applies to tests in the TypeScript workspaces, `frontend` and `shared`. Backend tests are
Python and follow [python/pytest.md](python/pytest.md); TEST-9 to TEST-13 say how the two
sides meet.

| Workspace  | Runner         | Environment | Libraries                                                          |
| ---------- | -------------- | ----------- | ------------------------------------------------------------------ |
| `frontend` | Vitest         | jsdom       | Testing Library (`react`, `user-event`, `jest-dom`), MSW           |
| `shared`   | Jest + ts-jest | node        | —                                                                  |
| `backend`  | pytest         | Python      | see [python/pytest.md](python/pytest.md) PYTEST-1; a real PostgreSQL test database |

**Run:** `pnpm frontend:test`, `pnpm shared:test`, `pnpm backend:test`. Backend tests run in a
dedicated `backend-test` Compose service against the test database
([docker-and-environment.md](docker-and-environment.md) ENV-4).

---

## Files and naming

**TEST-1 — Test files sit next to the code they test and are named `*.test.ts(x)`**
(`utils/safeFetch.test.ts`, `pages/ProjectDetails/index.test.tsx`). In `shared`, tests
MAY be grouped in a `__tests__/` folder inside the module they cover.

**TEST-2 — Fixtures live in `__mocks__/` as `<entity>Mocks.ts`** (`userMocks.ts`,
`projectMocks.ts`, `commonMocks.ts`).
- Fixture values are named `mock<Thing>` (`mockFirstUser`, `mockNow`).
- Factories are named `create<Thing>Mock` (`createTaskMock`).
- Lookups are named `find<Thing>Mock`.

Fixtures used by more than one workspace live in `shared` and are exported from its
testing entry point ([monorepo.md](monorepo.md) MONO-7).

**TEST-3 — Test helpers live in `utils/testing/`:**

- `dom-element-getters/` — `get<Thing>` and `get<Thing>Container` functions that find DOM
  nodes
- `expect-helpers/` — assertion bundles named `expect<Thing>ToBeVisibleAndCorrect`
- `matchers/` — custom matchers (see TEST-19)
- page-specific helpers MAY live in `pages/<Page>/testUtils.ts`

Production code MUST NOT import from these folders.

---

## Structure

**TEST-4 — Nest `describe` blocks by subject, then by unit:**

```ts
describe('TaskList', () => {
  describe("'addMany' method", () => {
    it('rejects a task for an archived project', () => { ... });
  });
});

describe('ProjectDetails', () => {
  describe('when the project is archived', () => { ... });
});
```

Name method blocks `"'methodName' method"` (or `"'name' static method"`), and name state
blocks `'when …'`.

**TEST-5 — Test names describe behaviour in the present tense:** `it('<verb>s …')` or
`it('renders correctly')`. Use one form per file.

**TEST-6 — Mark long setup with `/* START TEST SETUP */` … `/* END TEST SETUP */`** so the
act and assert steps are easy to find.

**TEST-7 — Mark unwritten tests with `it.todo('…')`.** Do not commit `it.skip` with a
placeholder assertion. A skipped test MUST have a `// TODO:` saying why it is skipped.

**TEST-8 — Tests MUST be independent of each other.** Reset state in `beforeEach` or
`afterEach` (`cleanup()`, `vi.clearAllMocks()`, `server.resetHandlers()`). Release
resources in `afterAll`: close the MSW server, restore spies, and switch back to real
timers.

---

## Backend and the API contract

**TEST-9 — Backend tests follow [python/pytest.md](python/pytest.md):** pytest against a
real PostgreSQL test database, with each test rolled back (PYTEST-10), routes tested
through `TestClient` (PYTEST-14, FAPI-20), and WebSocket routes as in
[websockets.md](websockets.md) WS-17. The rules in this document do not apply to them.

**TEST-10 — Frontend tests type every mocked API response with the generated contract**
([monorepo.md](monorepo.md) MONO-15). A mock built as
`const mockProjectResponse: ProjectResponse = { data: { ... } }` stops compiling when the
backend changes the response, so the frontend's tests cannot keep passing against a shape
the API no longer returns. Never type a mock as `any` or cast it with `as` to make it fit.

**TEST-11 — Fake timers MUST leave the event loop running.** In `shared` (Jest):
`jest.useFakeTimers({ doNotFake: ['nextTick', 'setImmediate'], now: mockNow })`. In
`frontend` (Vitest), fake only what the test needs, `vi.useFakeTimers({ toFake:
['setTimeout', 'clearTimeout', 'Date'], now: mockNow })`, so promises and MSW handlers
still resolve.

**TEST-12 — Compare objects that carry generated values with asymmetric matchers**
(`project_id: expect.toBeUUID()`, `created_at: expect.toBeISODateString()`; TEST-19),
rather than deleting the fields before comparing or copying a generated value into the
expectation.

**TEST-13 — Never point tests at a development service.** Frontend and `shared` tests
never call a running backend; they mock the network (TEST-18). Backend tests use
`.env.test` and the `test_app` database (ENV-4, PYTEST-10).

---

## Frontend (Vitest + Testing Library)

**TEST-14 — Import test APIs explicitly from `vitest`** (`describe`, `it`, `expect`, `vi`,
and hooks). Do not rely on globals.

**TEST-15 — Query the DOM the way a user would.** Use `findByRole('heading', { level: 2,
name })`, `getByLabelText('Username')`, and `getByRole('button', { name })`, scoped with
`within()`. Fall back to `container.querySelector('#id')` only for structural elements
with no accessible role. Interact through `userEvent.setup()` rather than `fireEvent`,
unless user-event cannot produce the event.

**TEST-16 — Wait for async UI with `findBy*` or `waitFor`.** Never use fixed sleeps.

**TEST-17 — Render with the real store and router.** Wrap the component in the app's
store provider with an `initialState`, and in a memory router built from the app's
`routerConfig` (`<WithMemoryRouter initialEntries={['/path']} />`). When a test needs to
dispatch store actions, render a small helper component in the test file that dispatches
them.

**TEST-18 — Mock the network at the boundary.** Mock HTTP with
`vi.spyOn(window, 'fetch').mockImplementation(createFetchMock())` or MSW `http` handlers,
and mock WebSockets with MSW `ws` handlers (`server.listen()`, `resetHandlers()`,
`close()`). Restore spies in `afterAll`.

---

## Shared conventions

**TEST-19 — Use the custom matchers from `shared`:** `toBeUUID`, `toBeISODateString`,
`toBeStringIncluding`, and `toBeNullish`. Use them both as matchers
(`expect(id).toBeUUID()`) and as asymmetric matchers (`userID: expect.toBeUUID()`).
Register them in each workspace's test setup file. New matchers go in `shared`, one per
file, each with its own `declare global` type augmentation.

**TEST-20 — Fixtures MUST be deterministic.** Use fixed UUIDs and one shared `mockNow`,
never `randomUUID()` or `new Date()` when the module loads.

**TEST-21 — Build complex domain-state fixtures by replaying a list of operations**
through the real domain logic, not by writing out the resulting state by hand. Give each
generator a JSDoc `@example` showing the state it produces.

**TEST-22 — `@ts-expect-error` in tests needs a reason**, as anywhere else
([typescript.md](typescript.md) TS-36). If the same suppression keeps repeating, fix the
type (for example, with a typed mock factory) instead.

**TEST-23 — New behaviour ships with tests.** A bug fix SHOULD start with a failing test
that reproduces the bug.
