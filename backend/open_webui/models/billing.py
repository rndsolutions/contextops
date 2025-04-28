import time
import uuid
from typing import Optional, List, Dict, Any

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, BigInteger
from sqlalchemy.orm import relationship, Session
from sqlalchemy.exc import SQLAlchemyError
from open_webui.internal.db import Base

# Used it for refrence implementation
# https://developer.paddle.com/build/subscriptions/provision-access-webhooks

class SubscriptionItem(Base):
    __tablename__ = "subscription_items"

    id = Column(String(255), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    subscription_id = Column(String(255), ForeignKey("subscriptions.id", ondelete="CASCADE"), nullable=False)
    price_id = Column(String(255), nullable=False)
    quantity = Column(Integer, nullable=False)
    product_id = Column(String(255), nullable=True)

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(String(255), primary_key=True, index=True)  # subscription.id from Paddle
    status = Column(String(255), nullable=True)
    collection_mode = Column(String(255), nullable=True)
    scheduled_change = Column(String(255), nullable=True)
    next_billed_at = Column(DateTime, nullable=True)
    current_billing_period = Column(String(255), nullable=True)
    billing_details = Column(String(255), nullable=True)
    occurred_at = Column(DateTime, nullable=True)  # notification.occurred_at

    created_at = Column(BigInteger, default=lambda: int(time.time_ns()))
    updated_at = Column(BigInteger, default=lambda: int(time.time_ns()), onupdate=lambda: int(time.time_ns()))

    items = relationship(
        "SubscriptionItem",
        backref="subscription",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )

class TransactionPayment(Base):
    __tablename__ = "transaction_payments"

    id = Column(String(255), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    transaction_id = Column(String(255), ForeignKey("transactions.id", ondelete="CASCADE"), nullable=False)
    method_details = Column(String(255), nullable=True)

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String(255), primary_key=True, index=True)  # transaction id from Paddle
    details_totals = Column(String(255), nullable=True)
    occurred_at = Column(DateTime, nullable=True)  # notification.occurred_at

    created_at = Column(BigInteger, default=lambda: int(time.time_ns()))
    updated_at = Column(BigInteger, default=lambda: int(time.time_ns()), onupdate=lambda: int(time.time_ns()))

    payments = relationship(
        "TransactionPayment",
        backref="transaction",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )


class BillingTable:
    def insert_subscription(self, db: Session, subscription_data: Dict[str, Any]) -> Optional[Subscription]:
        subscription_id = subscription_data.get("id")
        if not subscription_id:
            return None
        try:
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
            db.flush()

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
        except SQLAlchemyError:
            db.rollback()
            raise

    def get_subscription(self, db: Session, subscription_id: str) -> Optional[Subscription]:
        try:
            return db.query(Subscription).filter(Subscription.id == subscription_id).first()
        except SQLAlchemyError:
            db.rollback()
            raise

    def delete_subscription(self, db: Session, subscription_id: str) -> bool:
        try:
            db.query(SubscriptionItem).filter(SubscriptionItem.subscription_id == subscription_id).delete()
            db.query(Subscription).filter(Subscription.id == subscription_id).delete()
            db.commit()
            return True
        except SQLAlchemyError:
            db.rollback()
            raise

    def insert_transaction(self, db: Session, transaction_data: Dict[str, Any]) -> Optional[Transaction]:
        transaction_id = transaction_data.get("id")
        if not transaction_id:
            return None
        try:
            transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
            if not transaction:
                transaction = Transaction(id=transaction_id)
            transaction.details_totals = transaction_data.get("details_totals")
            transaction.occurred_at = transaction_data.get("occurred_at")
            db.add(transaction)
            db.flush()

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
        except SQLAlchemyError:
            db.rollback()
            raise

    def get_transaction(self, db: Session, transaction_id: str) -> Optional[Transaction]:
        try:
            return db.query(Transaction).filter(Transaction.id == transaction_id).first()
        except SQLAlchemyError:
            db.rollback()
            raise

    def delete_transaction(self, db: Session, transaction_id: str) -> bool:
        try:
            db.query(TransactionPayment).filter(TransactionPayment.transaction_id == transaction_id).delete()
            db.query(Transaction).filter(Transaction.id == transaction_id).delete()
            db.commit()
            return True
        except SQLAlchemyError:
            db.rollback()
            raise


Billing = BillingTable()
