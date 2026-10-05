# WebSocket Standards

Applies to real-time messaging between the frontend and the backend: the message models
and WebSocket routes in `backend`, the generated message types and event constants in
`shared`, and the connection manager in `frontend`.

**Stack:** FastAPI's WebSocket routes (Starlette's `WebSocket`), served by the same Uvicorn
process as the HTTP API and reached through the proxy at `/ws/`
([docker-and-environment.md](docker-and-environment.md) ENV-36, ENV-37); Pydantic message
models; the browser `WebSocket` API in the frontend; Starlette's `TestClient` in backend
tests and MSW `ws` handlers in frontend tests.

---

## Contract

**WS-1 — Event names are defined once, in the backend, and mirrored as checked constants
in `shared`.** The backend declares them in a `StrEnum` in `constants/ws_events.py`; each
member is `SCREAMING_SNAKE_CASE`, and its value is the kebab-case equivalent:

```python
class WSEvent(StrEnum):
    """Name every WebSocket message; values are the wire format."""

    JOIN_PROJECT = "join-project"
    UPDATE_TASK = "update-task"
    SEND_PROJECT = "send-project"
    SEND_TASK = "send-task"
    SEND_ERROR = "send-error"
```

`shared/src/constants/ws-events.ts` declares the same constants, each checked against the
generated message types (WS-3), so a renamed or removed event fails the frontend's
typecheck:

```ts
import type { ClientMessage, ServerMessage } from '../api';

export const JOIN_PROJECT = 'join-project' satisfies ClientMessage['event'];
export const UPDATE_TASK = 'update-task' satisfies ClientMessage['event'];
export const SEND_PROJECT = 'send-project' satisfies ServerMessage['event'];
export const SEND_TASK = 'send-task' satisfies ServerMessage['event'];
```

Both sides MUST use these names. Never write an event name as a string literal anywhere
else.

**WS-2 — Name events by direction:**

| Direction       | Pattern            | Examples                      |
| --------------- | ------------------ | ----------------------------- |
| client → server | imperative request | `JOIN_PROJECT`, `UPDATE_TASK` |
| server → client | `SEND_<payload>`   | `SEND_PROJECT`, `SEND_TASK`   |

**WS-3 — Every message is a JSON object `{ "event": ..., "data": ... }`, defined as a
Pydantic model in `api/websockets/messages.py`,** with `event` narrowed to one member and
`data` typed with an entity or payload model
([python/pydantic.md](python/pydantic.md)). The messages in each direction form a
discriminated union on `event`:

```python
class SendTaskMessage(BaseModel):
    """Send a task's full current state to the room."""

    event: Literal[WSEvent.SEND_TASK] = WSEvent.SEND_TASK
    data: TaskEntity


type ClientMessage = Annotated[
    JoinProjectMessage | UpdateTaskMessage, Field(discriminator="event")
]
type ServerMessage = Annotated[
    SendProjectMessage | SendTaskMessage | SendErrorMessage, Field(discriminator="event")
]
```

The backend adds every message model and both unions to the OpenAPI schema
([monorepo.md](monorepo.md) MONO-17), so the frontend's types for them are generated like
any other (MONO-13) and exposed as named aliases (MONO-15). Add a new message to the
backend models, regenerate, then use it on either side.

**WS-4 — Server-to-client payloads carry the full current state of whatever changed**, so
the client can replace its slice of state instead of merging deltas. Switch to deltas only
when payload size is a measured problem.

**WS-5 — Identify users from the authenticated session, not from client-supplied
parameters.** The room is identified by the route's path (`/ws/projects/{project_id}`),
typed `UUID` like any path ID (FAPI-10).

---

## Backend routes

**WS-6 — WebSocket routes live in `api/websockets/<resource>.py`,** one router per
resource, created as `APIRouter(prefix="/ws")` and included in `main.py` with the HTTP
routers (FAPI-4). This package sits beside `api/routes/` in the layout of
[python/python.md](python/python.md) PY-5, and holds the routes, `messages.py` (WS-3),
and `connection_manager.py` (WS-8).

**WS-7 — A route accepts the connection, then reads, validates, and dispatches each
message in a loop:**

```python
_client_message_adapter: TypeAdapter[ClientMessage] = TypeAdapter(ClientMessage)

_HANDLERS: dict[WSEvent, ClientMessageHandler] = {
    WSEvent.JOIN_PROJECT: handle_join_project,
    WSEvent.UPDATE_TASK: handle_update_task,
}


@projects_ws_router.websocket("/projects/{project_id}")
async def project_events(
    websocket: WebSocket,
    project_id: UUID,
    user: WSUserDep,
    open_db_session: WSSessionFactoryDep,
) -> None:
    """Relay task updates for one project to everyone viewing it."""
    await websocket.accept()
    connection_manager.join(project_id, user.user_id, websocket)
    try:
        while True:
            try:
                message = _client_message_adapter.validate_json(await websocket.receive_text())
            except ValidationError as e:
                logger.info("Rejected message: %s", [(err["loc"], err["type"]) for err in e.errors()])
                await websocket.send_text(SendErrorMessage.invalid().model_dump_json())
                continue
            await _HANDLERS[message.event](
                message, project_id=project_id, user=user, open_db_session=open_db_session
            )
    except WebSocketDisconnect:
        pass
    finally:
        connection_manager.leave(project_id, user.user_id)
```

- Handlers are named `handle_<event>` and dispatched through a registry dict (PY-35).
  They delegate all domain logic to services, like an HTTP route (FAPI-14).
- The route is `async def`, so it MUST NOT block (FAPI-8). Each message's database work
  runs in `await asyncio.to_thread(...)` (PY-51), in a function that opens a session with
  `with open_db_session() as db_session:`, commits its unit of work, and lets the context
  manager close it (SQLA-15). A connection never holds one session open for its lifetime.
- `WSSessionFactoryDep` is declared next to `DBSessionDep` in
  `api/dependencies/db_session.py` (FAPI-21). Its provider returns a context-manager
  factory built on `db_session_generator`, so it rolls back on error and closes like the
  HTTP dependency (FAPI-9), and tests override it to hand out the rolled-back test
  session (WS-17).
- An invalid message gets a `SEND_ERROR` reply with a fixed sentence and the connection
  stays open. The reply never echoes the input or Pydantic's error text, and the log names
  only each error's `loc` and `type` (FAPI-23).

**WS-8 — Check the connection before accepting it, and track clients per room in one
`ConnectionManager`.**

- The `WSUserDep` dependency reads the user from the session cookie, and checks the
  `Origin` header against the same allowed origins as `CORSMiddleware` (FAPI-17). CORS
  does not apply to WebSockets, so without that check any site could open a connection
  with the user's cookie. On failure it closes the socket with
  `status.WS_1008_POLICY_VIOLATION` before `accept()`.
- `api/websockets/connection_manager.py` holds one manager per process, with a private
  map `_rooms: dict[UUID, dict[UUID, WebSocket]]` (project ID → user ID → socket).
- The map lives in one process. Uvicorn workers do not share memory, so a broadcast
  reaches only clients connected to the same worker. Run the backend with one worker
  (`UVICORN_WORKERS=1`) and one replica until broadcasts go through a shared channel
  (PostgreSQL `LISTEN`/`NOTIFY` on the direct connection, PG-15, or a message broker);
  adding a worker or replica before that is a bug, not a scaling step.

**WS-9 — Broadcast only to clients in the affected room**, serializing the message once
with `model_dump_json()` and sending it to each socket. A send that fails removes that
client from the room instead of failing the broadcast.

**WS-10 — Remove a client from the room in `finally`** (WS-7), so a disconnect, an error,
or a server shutdown never leaves a dead socket in the map.

**WS-11 — WebSocket URLs come from configuration**, never from literals: the frontend
builds them from `APP_DOMAIN` (ENV-40), and the backend's route paths come from the
router prefix. Keep-alive pings are Uvicorn's (`UVICORN_WS_PING_INTERVAL`, 20 s by
default); do not add an application-level ping.

---

## Frontend connection manager

**WS-12 — One `WebSocketManager` singleton (`wsManager`) owns the connection.** Components
call its methods to open, get, and close the connection. They never call `new WebSocket`
directly.

**WS-13 — Components subscribe in an effect and unsubscribe in that effect's cleanup.**
Add the `message` listener, then remove it and close the connection on unmount. Wrap the
handler in `useCallback`.

**WS-14 — Message handlers parse with `safeParseJSON` and return early on `null`**, then
`switch` on `messageData.event`, typed with the generated `ServerMessage` union so each
case narrows `data`. The `default` branch logs the unhandled event. Each case dispatches a
store action rather than setting component state directly.

**WS-15 — Send only after the socket is `OPEN`.** Wait for the `open` event (or a promise
the manager exposes); do not poll `readyState` on an interval. Build outgoing messages
with the generated `ClientMessage` types.

**WS-16 — Reconnect with backoff.** The manager reconnects with exponential backoff and a
cap, then re-sends any join or subscribe messages for the current room. A close with
code 1008 (WS-8) is not retried.

---

## Testing

**WS-17 — Test each side at its boundary.** Backend tests open a connection with
`test_app_client.websocket_connect("/ws/projects/<id>")` as a context manager, then
`send_json` and `receive_json`, against the rolled-back test database, with `WSSessionFactoryDep`'s provider overridden
next to `api_db_session` ([python/pytest.md](python/pytest.md) PYTEST-10, PYTEST-14);
test each `handle_<event>`
function and the `ConnectionManager` directly as well. Frontend tests use MSW
`ws.link(url)` handlers in `__mocks__/`, with messages typed by the generated types
([testing.md](testing.md)).
