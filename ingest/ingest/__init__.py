"""The batch ingest service: loads upstream data into PostgreSQL.

It imports the backend's models, constants, configuration, database
session and logging, and adds only what ingestion needs. The backend
owns the schema; this package only writes rows.
"""
