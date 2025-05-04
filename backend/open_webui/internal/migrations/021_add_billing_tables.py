"""Peewee migrations -- 002_add_local_sharing.py.

Some examples (model - class or model name)::

    > Model = migrator.orm['table_name']            # Return model in current state by name
    > Model = migrator.ModelClass                   # Return model in current state by name

    > migrator.sql(sql)                             # Run custom SQL
    > migrator.run(func, *args, **kwargs)           # Run python function with the given args
    > migrator.create_model(Model)                  # Create a model (could be used as decorator)
    > migrator.remove_model(model, cascade=True)    # Remove a model
    > migrator.add_fields(model, **fields)          # Add fields to a model
    > migrator.change_fields(model, **fields)       # Change fields
    > migrator.remove_fields(model, *field_names, cascade=True)
    > migrator.rename_field(model, old_field_name, new_field_name)
    > migrator.rename_table(model, new_table_name)
    > migrator.add_index(model, *col_names, unique=False)
    > migrator.add_not_null(model, *field_names)
    > migrator.add_default(model, field_name, default)
    > migrator.add_constraint(model, name, sql)
    > migrator.drop_index(model, *col_names)
    > migrator.drop_not_null(model, *field_names)
    > migrator.drop_constraints(model, *constraints)

"""

import peewee as pw
from peewee_migrate import Migrator

def migrate(migrator: Migrator, database: pw.Database, *, fake=False):
    @migrator.create_model
    class Subscription(pw.Model):
        id = pw.CharField(max_length=255, primary_key=True)
        items = pw.TextField(null=True)  # Store as JSON string
        status = pw.CharField(max_length=255, null=True)
        discount = pw.CharField(max_length=255, null=True)
        paused_at = pw.DateTimeField(null=True)
        address_id = pw.CharField(max_length=255, null=True)
        created_at = pw.DateTimeField(null=True)
        started_at = pw.DateTimeField(null=True)
        updated_at = pw.DateTimeField(null=True)
        business_id = pw.CharField(max_length=255, null=True)
        canceled_at = pw.DateTimeField(null=True)
        custom_data = pw.TextField(null=True)  # Store as JSON string
        customer_id = pw.CharField(max_length=255, null=True)
        import_meta = pw.TextField(null=True)  # Store as JSON string
        billing_cycle = pw.TextField(null=True)  # Store as JSON string
        currency_code = pw.CharField(max_length=16, null=True)
        next_billed_at = pw.DateTimeField(null=True)
        transaction_id = pw.CharField(max_length=255, null=True)
        billing_details = pw.TextField(null=True)  # Store as JSON string
        collection_mode = pw.CharField(max_length=255, null=True)
        first_billed_at = pw.DateTimeField(null=True)
        scheduled_change = pw.TextField(null=True)  # Store as JSON string
        current_billing_period = pw.TextField(null=True)  # Store as JSON string

        class Meta:
            table_name = "subscriptions"


def rollback(migrator: Migrator, database: pw.Database, *, fake=False):    
    migrator.remove_model("subscriptions")
