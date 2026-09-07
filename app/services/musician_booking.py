"""Creación de reservas iniciadas por el músico (contratas offline / regularizadas)."""

from datetime import date, datetime
from decimal import Decimal
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.booking import Booking, BookingStatus
from app.models.contract import Contract
from app.models.contractor_profile import ContractorProfile
from app.models.musician_profile import MusicianProfile
from app.models.payment import Payment, PaymentStatus
from app.models.profile_status import ProfileStatus
from app.models.user import User, UserRole
from app.schemas.booking import MusicianAttachContractorSignature, MusicianBookingCreate
from app.services.booking_contract import create_booking_contract
from app.services.contract_pdf import contract_html_text_length
from app.services.payment_evidence import (
    apply_evidence_urls,
    assert_evidence_uploads,
    normalize_evidence_urls,
)
from app.services.uploads import UPLOAD_DIR
from app.services.uniqueness import (
    assert_document_number_unique,
    assert_phone_unique,
    normalize_email,
)


def assert_upload_exists(upload_url: str, label: str) -> None:
    filename = upload_url.rsplit("/", 1)[-1]
    if not filename or not (UPLOAD_DIR / filename).is_file():
        raise HTTPException(
            status_code=400,
            detail=f"No se encontró el archivo de {label}. Vuelve a subirlo.",
        )


def resolve_or_create_contractor_client(
    db: Session,
    *,
    fullname: str,
    email: str | None,
    phone: str | None,
    document_type: str | None,
    document_number: str | None,
    address: str | None,
    city: str | None,
) -> tuple[ContractorProfile, User]:
    email_raw = normalize_email(email)
    has_real_email = bool(email_raw)
    email_norm = email_raw if has_real_email else f"cliente-{uuid4().hex[:12]}@guest.local"

    user = None
    if has_real_email:
        user = (
            db.query(User)
            .filter(func.lower(User.email) == email_norm)
            .first()
        )

    if user:
        if user.role != UserRole.contractor:
            raise HTTPException(
                status_code=400,
                detail="Ese correo ya pertenece a una cuenta que no es de contratista",
            )
        profile = (
            db.query(ContractorProfile)
            .filter(ContractorProfile.user_id == user.id)
            .first()
        )
        if not profile:
            profile = ContractorProfile(
                user_id=user.id,
                status=ProfileStatus.draft,
            )
            db.add(profile)
            db.flush()

        # Completa datos faltantes del cliente para el contrato PDF
        if fullname and fullname.strip():
            user.fullname = fullname.strip()
        if phone and not user.phone:
            user.phone = assert_phone_unique(db, phone, exclude_user_id=user.id)
        if document_type and not profile.document_type:
            profile.document_type = document_type
        if document_number and not profile.document_number:
            profile.document_number = assert_document_number_unique(
                db,
                document_number,
                exclude_profile_id=profile.id,
            )
        if address and not profile.address:
            profile.address = address
        if city and not profile.city:
            profile.city = city
        db.flush()
        return profile, user

    phone_norm = assert_phone_unique(db, phone)
    user = User(
        email=email_norm,
        fullname=fullname.strip(),
        phone=phone_norm,
        role=UserRole.contractor,
        password_hash=None,
        is_verified=False,
        # Sin correo real: cuenta solo de soporte a la contrata (sin login útil)
        is_active=has_real_email,
    )
    db.add(user)
    db.flush()

    doc_norm = assert_document_number_unique(db, document_number)
    profile = ContractorProfile(
        user_id=user.id,
        document_type=document_type,
        document_number=doc_norm,
        address=address,
        city=city,
        status=ProfileStatus.draft,
    )
    db.add(profile)
    db.flush()
    return profile, user


def _apply_signature_and_optional_payment(
    db: Session,
    *,
    booking: Booking,
    signature_image_url: str,
    payment_evidence_url: str | None,
    payment_evidence_urls: list[str] | None,
    payment_amount: Decimal | None,
    payment_type: str | None,
    mark_payment_validated: bool,
    sign_ip: str,
) -> None:
    assert_upload_exists(signature_image_url, "firma")
    evidence_urls = normalize_evidence_urls(
        payment_evidence_url=payment_evidence_url,
        payment_evidence_urls=payment_evidence_urls,
    )
    if evidence_urls:
        assert_evidence_uploads(evidence_urls, require_at_least_one=False)

    contract = db.query(Contract).filter(Contract.booking_id == booking.id).first()
    if not contract:
        raise HTTPException(404, "Contrato no encontrado para esta reserva")

    has_snapshot = bool(contract.title and contract.body)
    has_legacy_pdf = bool(contract.contract_pdf_url or contract.contract_signed_pdf_url)
    if not has_snapshot and not has_legacy_pdf:
        raise HTTPException(
            status_code=400,
            detail=(
                "El contrato de esta reserva no tiene contenido. "
                "Vuelve a crear la solicitud o regenera el acuerdo."
            ),
        )

    now = datetime.utcnow()
    contract.terms_accepted = True
    contract.terms_accepted_at = now
    contract.terms_accepted_ip = sign_ip
    contract.contractor_signed = True
    contract.contractor_sign_timestamp = now
    contract.contractor_sign_ip = sign_ip
    contract.contractor_signature_url = signature_image_url
    if has_snapshot:
        contract.contract_signed_pdf_url = None

    amount = payment_amount
    if amount is None:
        if booking.advance_amount is not None:
            amount = Decimal(str(booking.advance_amount))
        elif booking.price_agreed is not None:
            amount = Decimal(str(booking.price_agreed))

    pay_type = payment_type
    if pay_type is None:
        pay_type = "advance" if booking.advance_amount is not None else "full"

    if amount is None or amount <= 0:
        # Firma sin montos: contrato firmado, pago pendiente de registrar
        booking.status = BookingStatus.contract_signed
        return

    payment = Payment(
        booking_id=booking.id,
        amount=amount,
        payment_type=pay_type,
        status=(
            PaymentStatus.retained
            if mark_payment_validated
            else PaymentStatus.initiated
        ),
        retained_at=now if mark_payment_validated else None,
    )
    apply_evidence_urls(payment, evidence_urls)
    db.add(payment)
    booking.status = (
        BookingStatus.payment_retained
        if mark_payment_validated
        else BookingStatus.payment_pending
    )


def create_musician_booking(
    db: Session,
    *,
    musician: MusicianProfile,
    musician_user: User,
    payload: MusicianBookingCreate,
    sign_ip: str = "unknown",
) -> Booking:
    if musician.status != ProfileStatus.published or not musician_user.is_verified:
        raise HTTPException(
            status_code=403,
            detail="Tu perfil de músico debe estar verificado para crear contratas",
        )

    if contract_html_text_length(musician.contract_template_body) < 50:
        raise HTTPException(
            status_code=400,
            detail="Configura tu plantilla de contrato antes de crear contratas",
        )

    if payload.event_date < date.today():
        raise HTTPException(400, "La fecha del evento no puede ser anterior a hoy")

    contractor, contractor_user = resolve_or_create_contractor_client(
        db,
        fullname=payload.contractor_fullname,
        email=str(payload.contractor_email) if payload.contractor_email else None,
        phone=payload.contractor_phone,
        document_type=payload.document_type,
        document_number=payload.document_number,
        address=payload.contractor_address,
        city=payload.contractor_city,
    )

    booking = Booking(
        contractor_id=contractor.id,
        musician_id=musician.id,
        event_date=payload.event_date,
        start_time=payload.start_time,
        end_time=payload.end_time,
        location_address=payload.location_address.strip(),
        location_city=payload.location_city,
        location_reference=payload.location_reference,
        event_type=payload.event_type.strip(),
        event_description=payload.event_description,
        price_agreed=payload.price_agreed,
        advance_amount=payload.advance_amount,
        musician_quote_notes=payload.musician_quote_notes,
        quoted_at=datetime.utcnow(),
        status=BookingStatus.accepted,
    )
    db.add(booking)
    db.flush()

    from app.services.platform_payment import sync_booking_platform_fee

    sync_booking_platform_fee(db, booking, use_current_settings=True)

    try:
        create_booking_contract(
            db,
            booking,
            musician,
            musician_user,
            contractor,
            contractor_user,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if payload.contractor_signature_url:
        _apply_signature_and_optional_payment(
            db,
            booking=booking,
            signature_image_url=payload.contractor_signature_url,
            payment_evidence_url=payload.payment_evidence_url,
            payment_evidence_urls=payload.payment_evidence_urls,
            payment_amount=payload.payment_amount,
            payment_type=payload.payment_type,
            mark_payment_validated=payload.mark_payment_validated,
            sign_ip=sign_ip,
        )

    db.commit()
    db.refresh(booking)
    return booking


def attach_contractor_signature_as_musician(
    db: Session,
    *,
    booking: Booking,
    musician: MusicianProfile,
    musician_user: User,
    payload: MusicianAttachContractorSignature,
    sign_ip: str = "unknown",
) -> Booking:
    if booking.status != BookingStatus.contract_pending:
        raise HTTPException(
            status_code=400,
            detail="Solo puedes adjuntar la firma cuando el contrato está pendiente",
        )

    if not payload.terms_accepted:
        raise HTTPException(
            status_code=400,
            detail="Debes confirmar que el contratista aceptó los términos",
        )

    contractor = (
        db.query(ContractorProfile)
        .filter(ContractorProfile.id == booking.contractor_id)
        .first()
    )
    if not contractor:
        raise HTTPException(404, "Contratista no encontrado")

    contractor_user = db.query(User).filter(User.id == contractor.user_id).first()
    if not contractor_user:
        raise HTTPException(404, "Usuario contratista no encontrado")

    _apply_signature_and_optional_payment(
        db,
        booking=booking,
        signature_image_url=payload.signature_image_url,
        payment_evidence_url=payload.payment_evidence_url,
        payment_evidence_urls=payload.payment_evidence_urls,
        payment_amount=payload.payment_amount,
        payment_type=payload.payment_type,
        mark_payment_validated=payload.mark_payment_validated,
        sign_ip=sign_ip or "unknown",
    )

    db.commit()
    db.refresh(booking)
    return booking
