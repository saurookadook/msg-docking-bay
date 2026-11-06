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
