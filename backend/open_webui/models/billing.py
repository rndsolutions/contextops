import time
import uuid
from typing import Optional, List, Dict, Any

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, BigInteger
from sqlalchemy.orm import relationship, Session
from sqlalchemy.exc import SQLAlchemyError
from open_webui.internal.db import Base

# Used it for refrence implementation
# https://developer.paddle.com/build/subscriptions/provision-access-webhooks

from sqlalchemy import JSON

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(String(255), primary_key=True, index=True)
    items = Column(JSON, nullable=True)
    status = Column(String(255), nullable=True)
    discount = Column(String(255), nullable=True)
    paused_at = Column(DateTime, nullable=True)
    address_id = Column(String(255), nullable=True)
    created_at = Column(DateTime, nullable=True)
    started_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    business_id = Column(String(255), nullable=True)
    canceled_at = Column(DateTime, nullable=True)
    custom_data = Column(JSON, nullable=True)
    customer_id = Column(String(255), nullable=True)
    import_meta = Column(JSON, nullable=True)
    billing_cycle = Column(JSON, nullable=True)
    currency_code = Column(String(16), nullable=True)
    next_billed_at = Column(DateTime, nullable=True)
    transaction_id = Column(String(255), nullable=True)
    billing_details = Column(JSON, nullable=True)
    collection_mode = Column(String(255), nullable=True)
    first_billed_at = Column(DateTime, nullable=True)
    scheduled_change = Column(JSON, nullable=True)
    current_billing_period = Column(JSON, nullable=True)


class BillingTable:
    def insert_subscription(self, db: Session, subscription_data: Dict[str, Any]) -> Optional[Subscription]:
        subscription_id = subscription_data.get("id")
        if not subscription_id:
            return None
        try:
            subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
            if not subscription:
                subscription = Subscription(id=subscription_id)
            subscription.items = subscription_data.get("items")
            subscription.status = subscription_data.get("status")
            subscription.discount = subscription_data.get("discount")
            subscription.paused_at = subscription_data.get("paused_at")
            subscription.address_id = subscription_data.get("address_id")
            subscription.created_at = subscription_data.get("created_at")
            subscription.started_at = subscription_data.get("started_at")
            subscription.updated_at = subscription_data.get("updated_at")
            subscription.business_id = subscription_data.get("business_id")
            subscription.canceled_at = subscription_data.get("canceled_at")
            subscription.custom_data = subscription_data.get("custom_data")
            subscription.customer_id = subscription_data.get("customer_id")
            subscription.import_meta = subscription_data.get("import_meta")
            subscription.billing_cycle = subscription_data.get("billing_cycle")
            subscription.currency_code = subscription_data.get("currency_code")
            subscription.next_billed_at = subscription_data.get("next_billed_at")
            subscription.transaction_id = subscription_data.get("transaction_id")
            subscription.billing_details = subscription_data.get("billing_details")
            subscription.collection_mode = subscription_data.get("collection_mode")
            subscription.first_billed_at = subscription_data.get("first_billed_at")
            subscription.scheduled_change = subscription_data.get("scheduled_change")
            subscription.current_billing_period = subscription_data.get("current_billing_period")
            db.add(subscription)
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
            db.query(Subscription).filter(Subscription.id == subscription_id).delete()
            db.commit()
            return True
        except SQLAlchemyError:
            db.rollback()
            raise


from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class BillingResponse(BaseModel):
    subscription: Optional[Dict[str, Any]] = None
    transaction: Optional[Dict[str, Any]] = None
    message: Optional[str] = None

Billing = BillingTable()
