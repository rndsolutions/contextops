from fastapi import APIRouter, Request, Response, status
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from open_webui.internal.db import get_db
from open_webui.models.billing import Billing
import dateutil.parser

router = APIRouter(
    prefix="/webhooks/billing",
    tags=["billing_webhooks"],
    responses={404: {"description": "Not found"}},
)

def parse_datetime(dt_str: Optional[str]) -> Optional[datetime]:
    if dt_str:
        try:
            return dateutil.parser.isoparse(dt_str)
        except Exception:
            return None
    return None

@router.post("/")
async def handle_billing_webhook(request: Request):
    """
    Endpoint to receive billing webhook events from Paddle.
    Parses the incoming JSON payload and persists relevant data using BillingTable.
    """
    payload = await request.json()
    event_type = payload.get("alert_name")

    with get_db() as db:
        if event_type in ("transaction_created", "transaction_updated"):
            transaction_data = payload.get("transaction", {})
            if transaction_data:
                # Prepare data dict for BillingTable
                data = {
                    "id": transaction_data.get("id"),
                    "details_totals": transaction_data.get("details", {}).get("totals"),
                    "occurred_at": parse_datetime(payload.get("notification", {}).get("occurred_at")),
                    "payments": transaction_data.get("payments", []),
                }
                Billing.insert_transaction(db, data)

        elif event_type in ("subscription_created", "subscription_updated"):
            subscription_data = payload.get("subscription", {})
            if subscription_data:
                # Prepare data dict for BillingTable
                data = {
                    "id": subscription_data.get("id"),
                    "status": subscription_data.get("status"),
                    "collection_mode": subscription_data.get("collection_mode"),
                    "scheduled_change": subscription_data.get("scheduled_change"),
                    "next_billed_at": parse_datetime(subscription_data.get("next_billed_at")),
                    "current_billing_period": subscription_data.get("current_billing_period"),
                    "billing_details": subscription_data.get("billing_details"),
                    "occurred_at": parse_datetime(payload.get("notification", {}).get("occurred_at")),
                    "items": subscription_data.get("items", []),
                }
                Billing.insert_subscription(db, data)

        else:
            # Unknown or unhandled event type
            pass

    return Response(status_code=status.HTTP_200_OK)
