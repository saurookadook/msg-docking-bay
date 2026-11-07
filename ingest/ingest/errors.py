"""The ingest service's exception hierarchy (PY-20)."""


class IngestError(Exception):
    """Base for a failure the CLI reports with its message alone.

    Anything else that escapes a command is unexpected and keeps its
    traceback.
    """


class SchemaNotAtHeadError(IngestError):
    """Raised when the database is not migrated to the backend's head.

    Ingest writes rows as the app role and never migrates, so it stops
    rather than write against a schema its models do not describe.
    """


class RunInProgressError(IngestError):
    """Raised when another run of the same source kind holds its lock.

    Two runs of one kind would race on the same rows and watermark.
    """


class RunLostError(IngestError):
    """Raised when a run has lost its lock and may write no more.

    Either its connection dropped, which released the lock, or a later
    run marked it abandoned. Another run may have taken over, so its
    record stands and this run's outcome is not written.
    """
