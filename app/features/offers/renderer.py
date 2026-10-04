from dataclasses import dataclass
from html import escape

from sqlalchemy.orm import Session

from app.features.offers.enums import VariantContentType
from app.features.offers.model import OfferVariant


@dataclass
class RenderedEmail:
    subject: str
    from_name: str | None  # None -> the sender account's own name is used
    html: str  # handed to the existing SMTP path as the campaign "body"


def render_variant(variant: OfferVariant) -> tuple[str, str | None, str]:
    """Turn a Variant into (subject, from_name, html). Raises ValueError for content invalid for its type.

    Plain text is escaped and keeps its newlines: the SMTP layer already turns "\\n" into <br>
    for bodies that are not full HTML documents. No styling, personalization or link rewriting here.
    """
    kind = variant.content_type
    text, image, html = variant.body_text, variant.image_url, variant.body_html

    if kind == VariantContentType.HTML:
        if not html:
            raise ValueError("HTML variant has no body_html.")
        content = html
    else:
        if kind == VariantContentType.TEXT and not text:
            raise ValueError("TEXT variant has no body_text.")
        if kind == VariantContentType.IMAGE and not image:
            raise ValueError("IMAGE variant has no image_url.")
        if kind == VariantContentType.TEXT_IMAGE and not (text or image):
            raise ValueError("TEXT_IMAGE variant has neither body_text nor image_url.")
        parts = []
        if text and kind in (VariantContentType.TEXT, VariantContentType.TEXT_IMAGE):
            parts.append(escape(text))
        if image and kind in (VariantContentType.IMAGE, VariantContentType.TEXT_IMAGE):
            parts.append(f'<img src="{escape(image, quote=True)}" alt="">')
        content = "\n\n".join(parts)

    return variant.subject, variant.from_name or None, content


def render_campaign_email(db: Session, campaign) -> RenderedEmail:
    """Email content for a campaign.

    Prepared snapshot -> the stored subject/from_name/body (never re-rendered).
    No Variant        -> the campaign's own subject/body/from_name, exactly as before.
    Variant           -> Variant subject, body and from_name; from_name falls back to the campaign's.
                         Only reached by campaigns prepared before snapshots existed.
    """
    if campaign.prepared_body is not None:
        return RenderedEmail(campaign.prepared_subject, campaign.prepared_from_name, campaign.prepared_body)

    if not campaign.variant_id:
        return RenderedEmail(campaign.subject, campaign.from_name, campaign.body)

    variant = db.get(OfferVariant, campaign.variant_id)
    if not variant or variant.offer_id != campaign.offer_id:
        raise ValueError("Selected variant is missing or does not belong to the campaign's offer.")
    subject, from_name, html = render_variant(variant)
    return RenderedEmail(subject, from_name or campaign.from_name, html)


def snapshot_campaign_email(db: Session, campaign) -> None:
    """Freeze the effective Variant email onto the campaign (called when it is prepared).

    Why: a campaign must send exactly what the user prepared. Editing or deactivating the Variant
    afterwards must not change queued emails, and there is no placeholder fallback (13A.13A).

    No-op for legacy campaigns (no Variant) and for campaigns that already hold a snapshot.
    Raises ValueError, leaving the campaign untouched, if the Variant is missing or invalid.
    """
    if not campaign.variant_id or campaign.prepared_body is not None:
        return
    email = render_campaign_email(db, campaign)
    campaign.prepared_subject = email.subject
    campaign.prepared_from_name = email.from_name
    campaign.prepared_body = email.html
