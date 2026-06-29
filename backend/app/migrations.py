"""
Lightweight, dependency-free auto-migration.

This project intentionally does not use Alembic. Instead, on every startup we:
  1. Run Base.metadata.create_all() — this creates any tables that don't exist
     yet (new features each release tend to add whole new tables), but it
     NEVER alters an existing table.
  2. Run run_auto_migration() below — this diffs each model's columns against
     what actually exists in the database and adds any that are missing,
     using safe ADD COLUMN ... IF NOT EXISTS statements.

This is what makes "docker compose pull && docker compose up -d" safe to run
against a database that already has data in it: every release after 1.1.0
that adds a column to an existing table (users, prescriptions, medicines,
etc.) will self-heal on startup instead of crashing the app in a boot loop.

Columns added this way come back NULL for existing rows — every new column
introduced in this codebase is nullable (or has sensible application-level
defaults applied in Python), specifically so that this is always safe.
"""

import logging
from sqlalchemy import inspect, text

logger = logging.getLogger("medical.migrations")


def _column_ddl(column, dialect):
    """Render 'ADD COLUMN "name" TYPE [DEFAULT x]' for one SQLAlchemy Column."""
    coltype = column.type.compile(dialect=dialect)
    parts = [f'ADD COLUMN IF NOT EXISTS "{column.name}" {coltype}']

    # Only apply a DDL-level default for simple scalar defaults (bool/str/int).
    # Server-side defaults keep future inserts from other tools consistent;
    # the ORM-level default still applies for inserts made through the app.
    if column.default is not None and getattr(column.default, "is_scalar", False):
        value = column.default.arg
        if isinstance(value, bool):
            parts.append(f"DEFAULT {'true' if value else 'false'}")
        elif isinstance(value, (int, float)):
            parts.append(f"DEFAULT {value}")
        elif isinstance(value, str):
            escaped = value.replace("'", "''")
            parts.append(f"DEFAULT '{escaped}'")

    return " ".join(parts)


def run_auto_migration(engine, base):
    """Add any columns (and their indexes) that exist on the SQLAlchemy models but not in the DB yet."""
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())
    added = []

    with engine.begin() as conn:
        for table in base.metadata.sorted_tables:
            if table.name not in existing_tables:
                continue  # brand new table — create_all() already built it fully

            existing_cols = {c["name"] for c in inspector.get_columns(table.name)}
            for column in table.columns:
                if column.name in existing_cols:
                    continue
                ddl = f'ALTER TABLE "{table.name}" {_column_ddl(column, engine.dialect)}'
                try:
                    conn.execute(text(ddl))
                    added.append(f"{table.name}.{column.name}")
                except Exception as e:  # noqa: BLE001
                    logger.error(f"[migration] Failed to add {table.name}.{column.name}: {e}")
                    raise

                if column.index:
                    idx_name = f"ix_{table.name}_{column.name}"
                    try:
                        conn.execute(text(
                            f'CREATE INDEX IF NOT EXISTS "{idx_name}" ON "{table.name}" ("{column.name}")'
                        ))
                    except Exception as e:  # noqa: BLE001
                        # An index is a performance nice-to-have, not worth crashing startup over.
                        logger.warning(f"[migration] Could not create index {idx_name}: {e}")

    if added:
        logger.info(f"[migration] Added {len(added)} missing column(s): {', '.join(added)}")
    return added
