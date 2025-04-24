"""Peewee migrations -- 019_add_trial_column.py."""

import peewee as pw
from peewee_migrate import Migrator

def migrate(migrator: Migrator, database: pw.Database, *, fake=False):
    """Write your migrations here."""
    migrator.add_fields(
        "user",
        trial=pw.BooleanField(default=True),
    )

def rollback(migrator: Migrator, database: pw.Database, *, fake=False):
    """Write your rollback migrations here."""
    migrator.remove_fields("user", "trial")
