from fastapi import APIRouter, Request, Response, status
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from open_webui.internal.db import get_db
from open_webui.models.billing import Billing
import dateutil.parser
import json

router = APIRouter(        
    responses={404: {"description": "Not found"}},
)

def parse_datetime(dt_str: Optional[str]) -> Optional[datetime]:
    if dt_str and isinstance(dt_str, str) and dt_str.strip():
        try:
            dt = dateutil.parser.isoparse(dt_str)
            # Additional sanity check: datetime should not be in the future by more than 1 day
            from datetime import datetime, timedelta
            if dt > datetime.utcnow() + timedelta(days=1):
                return None
            return dt
        except Exception:
            return None
    return None

@router.post("/")
async def handle_billing_webhook(request: Request):
    """
    Endpoint to receive billing webhook events from Paddle.
    Parses the incoming JSON payload and persists relevant data using BillingTable.
    """
    from starlette.requests import ClientDisconnect

    try:
        payload = await request.json()
    except ClientDisconnect:
        # Client disconnected before sending full request body
        return Response(status_code=status.HTTP_400_BAD_REQUEST, content="Client disconnected")

    event_type = payload.get("event_type")

    with get_db() as db:
        # Handle transaction events
        if event_type in ("transaction.paid4", "transaction.completed3"):
            transaction_data = payload.get("data", {})
            if transaction_data:
                # Compose a subscription_id if available
                subscription_id = transaction_data.get("subscription_id") or transaction_data.get("subscription", {}).get("id")
                # Compose transaction dict for upsert
                transaction_dict = {
                    "id": transaction_data.get("id"),
                    "items": transaction_data.get("items"),
                    "status": transaction_data.get("status"),
                    "discount": transaction_data.get("discount"),
                    "paused_at": parse_datetime(transaction_data.get("paused_at")),
                    "address_id": transaction_data.get("address_id"),
                    "created_at": parse_datetime(transaction_data.get("created_at")),
                    "started_at": parse_datetime(transaction_data.get("started_at")),
                    "updated_at": parse_datetime(transaction_data.get("updated_at")),
                    "business_id": transaction_data.get("business_id"),
                    "canceled_at": parse_datetime(transaction_data.get("canceled_at")),
                    "custom_data": transaction_data.get("custom_data"),
                    "customer_id": transaction_data.get("customer_id"),
                    "import_meta": transaction_data.get("import_meta"),
                    "billing_cycle": transaction_data.get("billing_cycle"),
                    "currency_code": transaction_data.get("currency_code"),
                    "next_billed_at": parse_datetime(transaction_data.get("next_billed_at")),
                    "transaction_id": transaction_data.get("id"),
                    "billing_details": transaction_data.get("billing_details"),
                    "collection_mode": transaction_data.get("collection_mode"),
                    "first_billed_at": parse_datetime(transaction_data.get("first_billed_at")),
                    "scheduled_change": transaction_data.get("scheduled_change"),
                    "current_billing_period": transaction_data.get("current_billing_period"),
                }
                # Remove keys with None values to avoid overwriting with nulls
                transaction_dict = {k: v for k, v in transaction_dict.items() if v is not None}
                Billing.insert_subscription(db, transaction_dict)

        # Handle subscription events
        elif event_type in ("subscription.created", "subscription.updated"):
            subscription_data = payload.get("data", {})
            if subscription_data:
                # Prepare data dict for BillingTable
                data = {
                    "id": subscription_data.get("id"),
                    "items": subscription_data.get("items"),
                    "status": subscription_data.get("status"),
                    "discount": subscription_data.get("discount"),
                    "paused_at": parse_datetime(subscription_data.get("paused_at")),
                    "address_id": subscription_data.get("address_id"),
                    "created_at": parse_datetime(subscription_data.get("created_at")),
                    "started_at": parse_datetime(subscription_data.get("started_at")),
                    "updated_at": parse_datetime(subscription_data.get("updated_at")),
                    "business_id": subscription_data.get("business_id"),
                    "canceled_at": parse_datetime(subscription_data.get("canceled_at")),
                    "custom_data": subscription_data.get("custom_data"),
                    "customer_id": subscription_data.get("customer_id"),
                    "import_meta": subscription_data.get("import_meta"),
                    "billing_cycle": subscription_data.get("billing_cycle"),
                    "currency_code": subscription_data.get("currency_code"),
                    "next_billed_at": parse_datetime(subscription_data.get("next_billed_at")),
                    "transaction_id": subscription_data.get("transaction_id"),
                    "billing_details": subscription_data.get("billing_details"),
                    "collection_mode": subscription_data.get("collection_mode"),
                    "first_billed_at": parse_datetime(subscription_data.get("first_billed_at")),
                    "scheduled_change": subscription_data.get("scheduled_change"),
                    "current_billing_period": subscription_data.get("current_billing_period"),
                }
                # Remove keys with None values to avoid overwriting with nulls
                data = {k: v for k, v in data.items() if v is not None}
                Billing.insert_subscription(db, data)

        else:
            # Unknown or unhandled event type
            pass

    return Response(status_code=status.HTTP_200_OK)
