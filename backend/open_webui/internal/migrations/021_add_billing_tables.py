
"""
Add tables for billing: subscriptions, subscription_items, transactions, transaction_payments.

"""

import peewee as pw
from peewee_migrate import Migrator

def migrate(migrator: Migrator, database: pw.Database, *, fake=False):
    migrator.create_model(
        type(
            "Subscription",
            (pw.Model,),
            {
                "id": pw.TextField(primary_key=True),
                "status": pw.TextField(null=True),
                "collection_mode": pw.TextField(null=True),
                "scheduled_change": pw.JSONField(null=True),
                "next_billed_at": pw.DateTimeField(null=True),
                "current_billing_period": pw.JSONField(null=True),
                "billing_details": pw.JSONField(null=True),
                "occurred_at": pw.DateTimeField(null=True),
                "created_at": pw.BigIntegerField(null=False),
                "updated_at": pw.BigIntegerField(null=False),
                "Meta": type("Meta", (), {"table_name": "subscriptions"}),
            },
        )
    )

    migrator.create_model(
        type(
            "SubscriptionItem",
            (pw.Model,),
            {
                "id": pw.TextField(primary_key=True),
                "subscription_id": pw.ForeignKeyField(
                    "subscriptions", "id", on_delete="CASCADE"
                ),
                "price_id": pw.TextField(null=False),
                "quantity": pw.IntegerField(null=False),
                "product_id": pw.TextField(null=True),
                "Meta": type("Meta", (), {"table_name": "subscription_items"}),
            },
        )
    )

    migrator.create_model(
        type(
            "Transaction",
            (pw.Model,),
            {
                "id": pw.TextField(primary_key=True),
                "details_totals": pw.JSONField(null=True),
                "occurred_at": pw.DateTimeField(null=True),
                "created_at": pw.BigIntegerField(null=False),
                "updated_at": pw.BigIntegerField(null=False),
                "Meta": type("Meta", (), {"table_name": "transactions"}),
            },
        )
    )

    migrator.create_model(
        type(
            "TransactionPayment",
            (pw.Model,),
            {
                "id": pw.TextField(primary_key=True),
                "transaction_id": pw.ForeignKeyField(
                    "transactions", "id", on_delete="CASCADE"
                ),
                "method_details": pw.JSONField(null=True),
                "Meta": type("Meta", (), {"table_name": "transaction_payments"}),
            },
        )
    )

def rollback(migrator: Migrator, database: pw.Database, *, fake=False):
    migrator.remove_model("transaction_payments")
    migrator.remove_model("transactions")
    migrator.remove_model("subscription_items")
    migrator.remove_model("subscriptions")
