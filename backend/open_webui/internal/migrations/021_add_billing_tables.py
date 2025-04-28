
"""
Add tables for billing: subscriptions, subscription_items, transactions, transaction_payments.

"""

import peewee as pw
from peewee_migrate import Migrator

def migrate(migrator: Migrator, database: pw.Database, *, fake=False):
    @migrator.create_model
    class Subscription(pw.Model):
        id = pw.CharField(max_length=255, primary_key=True)
        status = pw.CharField(max_length=255, null=True)
        collection_mode = pw.CharField(max_length=255, null=True)
        scheduled_change = pw.CharField(max_length=255, null=True)
        next_billed_at = pw.DateTimeField(null=True)
        current_billing_period = pw.CharField(max_length=255, null=True)
        billing_details = pw.CharField(max_length=255, null=True)
        occurred_at = pw.DateTimeField(null=True)
        created_at = pw.BigIntegerField(null=False)
        updated_at = pw.BigIntegerField(null=False)

        class Meta:
            table_name = "subscriptions"

    @migrator.create_model
    class SubscriptionItem(pw.Model):
        id = pw.TextField(primary_key=True)
        price_id = pw.CharField(max_length=255, null=False)
        quantity = pw.IntegerField(null=False)
        product_id = pw.CharField(max_length=255, null=True)

        class Meta:
            table_name = "subscription_items"

    @migrator.create_model
    class Transaction(pw.Model):
        id = pw.CharField(max_length=255, primary_key=True)
        details_totals = pw.CharField(max_length=255, null=True)
        occurred_at = pw.DateTimeField(null=True)
        created_at = pw.BigIntegerField(null=False)
        updated_at = pw.BigIntegerField(null=False)

        class Meta:
            table_name = "transactions"

    @migrator.create_model
    class TransactionPayment(pw.Model):
        id = pw.TextField(primary_key=True)        
        method_details = pw.CharField(max_length=255, null=True)

        class Meta:
            table_name = "transaction_payments"

def rollback(migrator: Migrator, database: pw.Database, *, fake=False):
    migrator.remove_model("transaction_payments")
    migrator.remove_model("transactions")
    migrator.remove_model("subscription_items")
    migrator.remove_model("subscriptions")
