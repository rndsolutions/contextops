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
    from starlette.requests import ClientDisconnect

    try:
        payload = await request.json()
    except ClientDisconnect:
        # Client disconnected before sending full request body
        # Log or handle as needed, here we return 400 Bad Request
        return Response(status_code=status.HTTP_400_BAD_REQUEST, content="Client disconnected")

    event_type = payload.get("event_type")

    with get_db() as db:
        if event_type in ("transaction.created", "transaction.updated"):
            transaction_data = payload.get("data", {})
            if transaction_data:
                # Prepare data dict for BillingTable
                data = {
                    "id": transaction_data.get("id"),
                    "details_totals": json.dumps(transaction_data.get("details", {}).get("totals")),
                    "occurred_at": parse_datetime(payload.get("notification", {}).get("occurred_at")),
                    "payments": json.dumps(transaction_data.get("payments", [])),
                }
                Billing.insert_transaction(db, data)

        elif event_type in ("subscription.created", "subscription.updated"):
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
