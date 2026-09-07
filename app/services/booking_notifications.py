from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.notification import Notification
from app.models.user import User, UserRole


def notify_user(
    db: Session,
    *,
    user: User,
    type: str,
    title: str,
    message: str,
    booking_id: str | None = None,
    meta: dict | None = None,
) -> None:
    payload: dict = dict(meta or {})
    if booking_id:
        payload["booking_id"] = booking_id

    db.add(
        Notification(
            user_id=user.id,
            type=type,
            title=title,
            message=message,
            meta=payload or None,
        )
    )


def notify_admins(
    db: Session,
    *,
    type: str,
    title: str,
    message: str,
    meta: dict | None = None,
) -> None:
    admins = db.query(User).filter(User.role == UserRole.admin).all()
    for admin in admins:
        notify_user(
            db,
            user=admin,
            type=type,
            title=title,
            message=message,
            meta=meta,
        )


def notify_booking_created(db: Session, musician_user: User, booking_id: str) -> None:
    notify_user(
        db,
        user=musician_user,
        type="booking_requested",
        title="Nueva solicitud de reserva",
        message="Un contratista te envió una solicitud de reserva. Revísala y responde con tu cotización.",
        booking_id=booking_id,
    )


def notify_booking_updated(db: Session, musician_user: User, booking_id: str) -> None:
    notify_user(
        db,
        user=musician_user,
        type="booking_updated",
        title="Solicitud actualizada",
        message="El contratista actualizó los detalles de la solicitud. Revísala antes de cotizar.",
        booking_id=booking_id,
    )


def notify_booking_quoted(db: Session, contractor_user: User, booking_id: str) -> None:
    notify_user(
        db,
        user=contractor_user,
        type="booking_quoted",
        title="Cotización recibida",
        message="El músico respondió tu solicitud con un precio. Revisa la cotización y confirma o rechaza.",
        booking_id=booking_id,
    )


def notify_booking_quote_updated(db: Session, contractor_user: User, booking_id: str) -> None:
    notify_user(
        db,
        user=contractor_user,
        type="booking_quote_updated",
        title="Cotización actualizada",
        message="El músico modificó su cotización. Revisa los cambios y confirma o rechaza.",
        booking_id=booking_id,
    )


def notify_booking_quote_accepted(db: Session, musician_user: User, booking_id: str) -> None:
    notify_user(
        db,
        user=musician_user,
        type="booking_quote_accepted",
        title="Cotización aceptada",
        message="El contratista aceptó tu cotización. El contrato está listo para su revisión.",
        booking_id=booking_id,
    )


def notify_booking_confirmed(db: Session, musician_user: User, booking_id: str) -> None:
    notify_user(
        db,
        user=musician_user,
        type="booking_confirmed",
        title="Comprobante enviado",
        message="El contratista aceptó el contrato y subió la evidencia de pago. Un administrador la revisará.",
        booking_id=booking_id,
    )


def notify_admins_payment_submitted(
    db: Session, booking_id: str, *, kind: str
) -> None:
    label = "el anticipo" if kind == "advance" else "el abono final"
    notify_admins(
        db,
        type="admin_payment_review_requested",
        title="Comprobante por validar",
        message=f"Un contratista subió el comprobante de {label}. Revísalo en Tesorería.",
        meta={"booking_id": booking_id, "kind": kind},
    )


def notify_payment_validated(
    db: Session, contractor_user: User, musician_user: User, booking_id: str
) -> None:
    notify_user(
        db,
        user=contractor_user,
        type="payment_validated",
        title="Reserva confirmada",
        message="El administrador validó tu anticipo. Ya puedes coordinar detalles del evento.",
        booking_id=booking_id,
    )
    notify_user(
        db,
        user=musician_user,
        type="payment_validated",
        title="Reserva confirmada",
        message="El administrador validó el anticipo del contratista. La reserva quedó confirmada.",
        booking_id=booking_id,
    )


def notify_payment_rejected(
    db: Session,
    contractor_user: User,
    musician_user: User,
    booking_id: str,
    *,
    reason: str,
) -> None:
    notify_user(
        db,
        user=contractor_user,
        type="payment_rejected",
        title="Comprobante rechazado",
        message=f"El administrador rechazó tu comprobante: {reason}. Vuelve a firmar y subir la evidencia.",
        booking_id=booking_id,
    )
    notify_user(
        db,
        user=musician_user,
        type="payment_rejected",
        title="Comprobante rechazado",
        message="El administrador rechazó el comprobante del anticipo de tu contratista.",
        booking_id=booking_id,
    )


def notify_payment_released(db: Session, musician_user: User, booking_id: str) -> None:
    notify_user(
        db,
        user=musician_user,
        type="payment_released",
        title="Pago liberado",
        message="Los pagos de esta reserva fueron liberados. Ya puedes verlos en tus ingresos.",
        booking_id=booking_id,
    )


def notify_booking_commitment_updated(
    db: Session,
    contractor_user: User,
    booking_id: str,
    *,
    notes: str | None = None,
) -> None:
    """Músico actualiza el compromiso: solo notifica al contratista (sin validación)."""
    base = (
        "El músico actualizó detalles del compromiso (ubicación, precio u otros). "
        "Revisa la reserva."
    )
    if notes and notes.strip():
        base = f"{base} Nota: {notes.strip()[:120]}"
    notify_user(
        db,
        user=contractor_user,
        type="booking_commitment_updated",
        title="Compromiso actualizado",
        message=base,
        booking_id=booking_id,
    )


def notify_booking_change_requested(
    db: Session, musician_user: User, booking_id: str
) -> None:
    notify_user(
        db,
        user=musician_user,
        type="booking_change_requested",
        title="Cambio solicitado en la reserva",
        message="El contratista propuso cambios (ubicación u otros detalles). Revísalos y acepta o rechaza.",
        booking_id=booking_id,
    )


def notify_booking_change_accepted(
    db: Session, contractor_user: User, booking_id: str
) -> None:
    notify_user(
        db,
        user=contractor_user,
        type="booking_change_accepted",
        title="Cambio aceptado",
        message="El músico aceptó los cambios que propusiste. La reserva se actualizó sin volver a firmar.",
        booking_id=booking_id,
    )


def notify_booking_change_rejected(
    db: Session, contractor_user: User, booking_id: str
) -> None:
    notify_user(
        db,
        user=contractor_user,
        type="booking_change_rejected",
        title="Cambio rechazado",
        message="El músico rechazó los cambios propuestos. La reserva continúa con los datos anteriores.",
        booking_id=booking_id,
    )


def notify_booking_requoted(
    db: Session, contractor_user: User, booking_id: str
) -> None:
    notify_user(
        db,
        user=contractor_user,
        type="booking_quoted",
        title="Nueva cotización por cambios",
        message="El músico actualizó el precio tras tus cambios. Revisa la nueva cotización.",
        booking_id=booking_id,
    )


def notify_booking_message(
    db: Session, target_user: User, booking_id: str, preview: str
) -> None:
    notify_user(
        db,
        user=target_user,
        type="booking_message",
        title="Nuevo mensaje en tu reserva",
        message=preview[:140],
        booking_id=booking_id,
    )


def notify_balance_submitted(
    db: Session, musician_user: User, booking_id: str
) -> None:
    notify_user(
        db,
        user=musician_user,
        type="balance_submitted",
        title="Abono final en revisión",
        message="El contratista subió el comprobante del saldo. Un administrador lo revisará.",
        booking_id=booking_id,
    )


def notify_balance_validated(
    db: Session, contractor_user: User, musician_user: User, booking_id: str
) -> None:
    notify_user(
        db,
        user=contractor_user,
        type="balance_validated",
        title="Abono final validado",
        message="El administrador validó el pago total. Ya puedes compartir fotos y reseña del evento.",
        booking_id=booking_id,
    )
    notify_user(
        db,
        user=musician_user,
        type="balance_validated",
        title="Abono final validado",
        message="El administrador validó el pago total del contratista. Ya se habilitó la fase de evento.",
        booking_id=booking_id,
    )


def notify_balance_rejected(
    db: Session,
    contractor_user: User,
    musician_user: User,
    booking_id: str,
    *,
    reason: str,
) -> None:
    notify_user(
        db,
        user=contractor_user,
        type="balance_rejected",
        title="Abono final rechazado",
        message=f"El administrador rechazó el comprobante del saldo: {reason}. Vuelve a subirlo.",
        booking_id=booking_id,
    )
    notify_user(
        db,
        user=musician_user,
        type="balance_rejected",
        title="Abono final rechazado",
        message="El administrador rechazó el comprobante del saldo de tu contratista.",
        booking_id=booking_id,
    )


def notify_booking_event_started(
    db: Session, target_user: User, booking_id: str
) -> None:
    notify_user(
        db,
        user=target_user,
        type="booking_event_started",
        title="Evento habilitado",
        message="La fase de evento quedó activa. Ya pueden compartir fotos y reacciones.",
        booking_id=booking_id,
    )


def notify_live_location_requested(
    db: Session,
    target_user: User,
    booking_id: str,
    from_party: str,
) -> None:
    who = {
        "leader": "El músico líder",
        "member": "Un integrante",
        "musician": "El músico",
        "contractor": "El contratista",
    }.get(from_party, "Un participante")
    notify_user(
        db,
        user=target_user,
        type="live_location_requested",
        title="Solicitud de ubicación",
        message=f"{who} te pide compartir tu ubicación en vivo durante el evento.",
        booking_id=booking_id,
    )


def notify_live_location_sharing(
    db: Session,
    target_user: User,
    booking_id: str,
    from_party: str,
) -> None:
    who = {
        "leader": "El músico líder",
        "member": "Un integrante",
        "musician": "El músico",
        "contractor": "El contratista",
    }.get(from_party, "Un participante")
    notify_user(
        db,
        user=target_user,
        type="live_location_sharing",
        title="Ubicación compartida",
        message=f"{who} empezó a compartir su ubicación. Ya puedes verla en el mapa.",
        booking_id=booking_id,
    )


def notify_booking_completed(
    db: Session, target_user: User, booking_id: str
) -> None:
    notify_user(
        db,
        user=target_user,
        type="booking_completed",
        title="Reserva finalizada",
        message="La contratación quedó cerrada. Gracias por usar la plataforma.",
        booking_id=booking_id,
    )


def notify_booking_review(
    db: Session, target_user: User, booking_id: str, preview: str
) -> None:
    notify_user(
        db,
        user=target_user,
        type="booking_review",
        title="Nueva reacción del evento",
        message=preview[:140],
        booking_id=booking_id,
    )


def notify_booking_rejected(
    db: Session,
    target_user: User,
    booking_id: str,
    *,
    by_role: str,
) -> None:
    role_label = "músico" if by_role == "musician" else "contratista"
    notify_user(
        db,
        user=target_user,
        type="booking_rejected",
        title="Solicitud rechazada",
        message=f"La solicitud de reserva fue rechazada por el {role_label}.",
        booking_id=booking_id,
    )


def notify_booking_cancelled(
    db: Session,
    target_user: User,
    booking_id: str,
    *,
    by_role: str,
) -> None:
    role_label = "músico" if by_role == "musician" else "contratista"
    notify_user(
        db,
        user=target_user,
        type="booking_cancelled",
        title="Reserva cancelada",
        message=f"La reserva fue cancelada por el {role_label}.",
        booking_id=booking_id,
    )


def notify_profile_submitted(
    db: Session,
    *,
    user: User,
    profile_role: str,
    profile_id: str,
    display_name: str,
) -> None:
    role_label = "músico" if profile_role == "musician" else "contratista"
    notify_user(
        db,
        user=user,
        type="profile_submitted",
        title="Perfil enviado a revisión",
        message="Recibimos tu solicitud de verificación. Te avisaremos cuando un administrador la revise.",
        meta={"profile_id": profile_id, "profile_role": profile_role},
    )
    notify_admins(
        db,
        type="profile_review_requested",
        title=f"Nueva verificación de {role_label}",
        message=f"{display_name} envió su perfil de {role_label} para revisión.",
        meta={"profile_id": profile_id, "profile_role": profile_role},
    )


def notify_profile_approved(
    db: Session,
    *,
    user: User,
    profile_role: str,
    profile_id: str,
) -> None:
    role_label = "músico" if profile_role == "musician" else "contratista"
    notify_user(
        db,
        user=user,
        type="profile_approved",
        title="Perfil verificado",
        message=f"Tu perfil de {role_label} fue aprobado. Ya puedes usar todas las funciones de la plataforma.",
        meta={"profile_id": profile_id, "profile_role": profile_role},
    )


def notify_profile_rejected(
    db: Session,
    *,
    user: User,
    profile_role: str,
    profile_id: str,
    reason: str,
) -> None:
    notify_user(
        db,
        user=user,
        type="profile_rejected",
        title="Perfil rechazado",
        message=f"Tu perfil necesita correcciones: {reason}",
        meta={
            "profile_id": profile_id,
            "profile_role": profile_role,
            "rejection_reason": reason,
        },
    )


def notify_profile_needs_resubmit(
    db: Session,
    *,
    user: User,
    profile_role: str,
    profile_id: str,
) -> None:
    notify_user(
        db,
        user=user,
        type="profile_needs_resubmit",
        title="Verificación pendiente otra vez",
        message="Actualizaste tu perfil publicado. Vuelve a enviarlo para revisión para recuperar la verificación.",
        meta={"profile_id": profile_id, "profile_role": profile_role},
    )


def notify_complaint_opened(db: Session, musician_user: User, booking_id: str) -> None:
    notify_user(
        db,
        user=musician_user,
        type="booking_complaint_opened",
        title="Queja sobre un show finalizado",
        message="El contratista registró una queja. Revisa el detalle y acepta o presenta tu descargo.",
        booking_id=booking_id,
    )
    notify_admins(
        db,
        type="booking_complaint_opened",
        title="Nueva queja de reserva",
        message="Un contratista abrió una queja. Espera las respuestas antes de liquidar.",
        meta={"booking_id": booking_id},
    )


def notify_complaint_musician_update(
    db: Session,
    *,
    contractor_user: User,
    booking_id: str,
    accepted: bool,
) -> None:
    notify_user(
        db,
        user=contractor_user,
        type="booking_complaint_musician_update",
        title="El músico respondió la queja" if not accepted else "El músico aceptó la queja",
        message=(
            "El músico aceptó la queja. El admin definirá los montos al liquidar."
            if accepted
            else "El músico presentó su descargo. El admin revisará y liquidará."
        ),
        booking_id=booking_id,
    )
    notify_admins(
        db,
        type="booking_complaint_musician_update",
        title="Queja lista para liquidar",
        message="Ambas partes ya respondieron. Define montos y liquida desde Tesorería.",
        meta={"booking_id": booking_id, "accepted": accepted},
    )


def notify_settlement_completed(
    db: Session,
    *,
    musician_user: User,
    contractor_user: User,
    booking_id: str,
    musician_amount: float,
    contractor_refund: float,
) -> None:
    notify_user(
        db,
        user=musician_user,
        type="booking_settled",
        title="Desembolso autorizado",
        message=f"El admin liquidó la reserva. Monto a recibir: S/ {musician_amount:.2f}.",
        booking_id=booking_id,
    )
    if contractor_refund > 0:
        notify_user(
            db,
            user=contractor_user,
            type="booking_settled_refund",
            title="Devolución pendiente de transferencia",
            message=(
                f"El admin liquidó la disputa con una devolución de "
                f"S/ {contractor_refund:.2f}. Cuando envíen el comprobante "
                f"deberás validarlo."
            ),
            booking_id=booking_id,
        )


def notify_refund_transfer_sent(
    db: Session,
    *,
    contractor_user: User,
    booking_id: str,
    amount: float,
) -> None:
    notify_user(
        db,
        user=contractor_user,
        type="booking_refund_transfer",
        title="Comprobante de devolución",
        message=(
            f"El admin registró la devolución de S/ {amount:.2f}. "
            f"Revisa el comprobante y valida para completar."
        ),
        booking_id=booking_id,
    )


def notify_refund_validated(
    db: Session,
    *,
    booking_id: str,
    amount: float,
    accepted: bool,
    reason: str | None = None,
) -> None:
    if accepted:
        notify_admins(
            db,
            type="booking_refund_validated",
            title="Devolución confirmada",
            message=(
                f"El contratista validó la devolución de S/ {amount:.2f}."
            ),
            meta={"booking_id": booking_id, "amount": amount},
        )
    else:
        detail = f" Motivo: {reason}" if reason else ""
        notify_admins(
            db,
            type="booking_refund_rejected",
            title="Devolución rechazada",
            message=(
                f"El contratista rechazó el comprobante de S/ {amount:.2f}."
                f"{detail} Debes volver a transferir."
            ),
            meta={"booking_id": booking_id, "amount": amount, "reason": reason},
        )

