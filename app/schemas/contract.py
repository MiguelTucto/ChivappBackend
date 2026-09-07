from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel


class ContractOut(BaseModel):
    id: UUID
    booking_id: UUID
    title: str | None = None
    body: str | None = None
    context: dict[str, Any] | None = None
    # Legacy PDF paths (contratos antiguos). Nuevos contratos generan PDF on-demand.
    contract_pdf_url: str | None = None
    contract_signed_pdf_url: str | None = None
    contractor_signature_url: str | None = None
    musician_signature_url: str | None = None
    contractor_signed: bool
    musician_signed: bool
    terms_accepted: bool
    terms_accepted_at: datetime | None
    contractor_sign_timestamp: datetime | None
    musician_sign_timestamp: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
