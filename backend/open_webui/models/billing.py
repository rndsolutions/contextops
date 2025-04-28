import time
import uuid
from typing import Optional

from sqlalchemy import Column, String, Integer, DateTime, JSON, ForeignKey, Text, BigInteger
from sqlalchemy.orm import relationship
from open_webui.internal.db import Base

class SubscriptionItem(Base):
    __tablename__ = "subscription_items"

    id = Column(Text, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    subscription_id = Column(Text, ForeignKey("subscriptions.id"), nullable=False)
    price_id = Column(Text, nullable=False)
    quantity = Column(Integer, nullable=False)
    product_id = Column(Text, nullable=True)

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Text, primary_key=True, index=True)  # subscription.id from Paddle
    status = Column(Text, nullable=True)
    collection_mode = Column(Text, nullable=True)
    scheduled_change = Column(JSON, nullable=True)
    next_billed_at = Column(DateTime, nullable=True)
    current_billing_period = Column(JSON, nullable=True)
    billing_details = Column(JSON, nullable=True)
    occurred_at = Column(DateTime, nullable=True)  # notification.occurred_at

    created_at = Column(BigInteger, default=lambda: int(time.time_ns()))
    updated_at = Column(BigInteger, default=lambda: int(time.time_ns()), onupdate=lambda: int(time.time_ns()))

    items = relationship("SubscriptionItem", backref="subscription", cascade="all, delete-orphan")

class TransactionPayment(Base):
    __tablename__ = "transaction_payments"

    id = Column(Text, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    transaction_id = Column(Text, ForeignKey("transactions.id"), nullable=False)
    method_details = Column(JSON, nullable=True)

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Text, primary_key=True, index=True)  # transaction id from Paddle
    details_totals = Column(JSON, nullable=True)
    occurred_at = Column(DateTime, nullable=True)  # notification.occurred_at

    created_at = Column(BigInteger, default=lambda: int(time.time_ns()))
    updated_at = Column(BigInteger, default=lambda: int(time.time_ns()), onupdate=lambda: int(time.time_ns()))

    payments = relationship("TransactionPayment", backref="transaction", cascade="all, delete-orphan")


class BillingTable:
    def insert_subscription(self, db, subscription_data: dict):
        subscription_id = subscription_data.get("id")
        if not subscription_id:
            return None
        subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
        if not subscription:
            subscription = Subscription(id=subscription_id)
        subscription.status = subscription_data.get("status")
        subscription.collection_mode = subscription_data.get("collection_mode")
        subscription.scheduled_change = subscription_data.get("scheduled_change")
        subscription.next_billed_at = subscription_data.get("next_billed_at")
        subscription.current_billing_period = subscription_data.get("current_billing_period")
        subscription.billing_details = subscription_data.get("billing_details")
        subscription.occurred_at = subscription_data.get("occurred_at")
        db.add(subscription)
        db.commit()

        # Clear existing items and add new ones
        db.query(SubscriptionItem).filter(SubscriptionItem.subscription_id == subscription.id).delete()
        items = subscription_data.get("items", [])
        for item in items:
            price = item.get("price", {})
            item_obj = SubscriptionItem(
                subscription_id=subscription.id,
                price_id=price.get("id"),
                quantity=item.get("quantity"),
                product_id=price.get("product_id"),
            )
            db.add(item_obj)
        db.commit()
        return subscription

    def get_subscription(self, db, subscription_id: str):
        return db.query(Subscription).filter(Subscription.id == subscription_id).first()

    def delete_subscription(self, db, subscription_id: str):
        db.query(SubscriptionItem).filter(SubscriptionItem.subscription_id == subscription_id).delete()
        db.query(Subscription).filter(Subscription.id == subscription_id).delete()
        db.commit()
        return True

    def insert_transaction(self, db, transaction_data: dict):
        transaction_id = transaction_data.get("id")
        if not transaction_id:
            return None
        transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
        if not transaction:
            transaction = Transaction(id=transaction_id)
        transaction.details_totals = transaction_data.get("details_totals")
        transaction.occurred_at = transaction_data.get("occurred_at")
        db.add(transaction)
        db.commit()

        # Clear existing payments and add new ones
        db.query(TransactionPayment).filter(TransactionPayment.transaction_id == transaction.id).delete()
        payments = transaction_data.get("payments", [])
        for payment in payments:
            payment_obj = TransactionPayment(
                transaction_id=transaction.id,
                method_details=payment.get("method_details"),
            )
            db.add(payment_obj)
        db.commit()
        return transaction

    def get_transaction(self, db, transaction_id: str):
        return db.query(Transaction).filter(Transaction.id == transaction_id).first()

    def delete_transaction(self, db, transaction_id: str):
        db.query(TransactionPayment).filter(TransactionPayment.transaction_id == transaction_id).delete()
        db.query(Transaction).filter(Transaction.id == transaction_id).delete()
        db.commit()
        return True


Billing = BillingTable()
