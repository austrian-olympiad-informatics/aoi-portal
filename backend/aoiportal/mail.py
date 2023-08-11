import logging
import re
import smtplib
from dataclasses import dataclass
from email.headerregistry import Address as EmailAddress
from email.message import EmailMessage
from email.utils import formatdate, make_msgid
from typing import List, Optional, Union, cast

from flask import current_app, render_template

_LOGGER = logging.getLogger(__name__)


@dataclass
class Address:
    address: str
    name: Optional[str] = None


def _address_to_email_address(
    address: Union[List[Address], Address, str, None]
) -> Union[None, EmailAddress, List[EmailAddress]]:
    if address is None:
        return None
    if isinstance(address, str):
        m = re.match(r"(.*)\s*<(.*)@(.*)>", address)
        if m is not None:
            return EmailAddress(m.group(1), m.group(2), m.group(3))
        m = re.match(r"(.*)@(.*)", address)
        if m is not None:
            return EmailAddress("", m.group(1), m.group(2))
        raise ValueError(f"Not a valid email address: {address}")
    if isinstance(address, list):
        return [cast(EmailAddress, _address_to_email_address(x)) for x in address]
    m = re.match(r"(.*)@(.*)", address.address)
    if m is None:
        raise ValueError(f"Not a valid email address: {address}")
    return EmailAddress(address.name or "", m.group(1), m.group(2))


def encode_email(
    *,
    to: Address,
    subject: str,
    content_html: str,
    reply_to: Union[None, Address, List[Address]] = None,
    unsubscribe_link: Optional[str] = None,
) -> EmailMessage:
    full_html = render_template(
        "mail_template.html", content=content_html, unsubscribe_link=unsubscribe_link
    )

    msg = EmailMessage()
    sender = cast(
        EmailAddress,
        _address_to_email_address(current_app.config["MAIL_DEFAULT_SENDER"]),
    )
    msg["Subject"] = subject
    msg["From"] = sender
    msg.set_content(full_html, subtype="html")
    msg["To"] = _address_to_email_address(to)
    msg["Date"] = formatdate(localtime=True)
    # see RFC 5322 section 3.6.4.
    msg["Message-ID"] = make_msgid(domain=sender.domain)
    if reply_to:
        msg["Reply-To"] = _address_to_email_address(reply_to)
    return msg


def send_email(
    *,
    to: Address,
    subject: str,
    content_html: str,
    reply_to: Union[None, Address, List[Address]] = None,
    unsubscribe_link: Optional[str] = None,
) -> None:
    msg = encode_email(
        to=to,
        subject=subject,
        content_html=content_html,
        reply_to=reply_to,
        unsubscribe_link=unsubscribe_link,
    )
    with smtplib.SMTP(
        current_app.config["MAIL_SERVER"],
        current_app.config["MAIL_PORT"],
    ) as smtp:
        if current_app.config["MAIL_USE_TLS"]:
            smtp.starttls()
        smtp.login(
            current_app.config["MAIL_USERNAME"],
            current_app.config["MAIL_PASSWORD"],
        )
        smtp.send_message(msg)


def send_mass(mails: List[EmailMessage]) -> List[EmailMessage]:
    failed = []
    with smtplib.SMTP(
        current_app.config["MAIL_SERVER"],
        current_app.config["MAIL_PORT"],
    ) as smtp:
        if current_app.config["MAIL_USE_TLS"]:
            smtp.starttls()
        smtp.login(
            current_app.config["MAIL_USERNAME"],
            current_app.config["MAIL_PASSWORD"],
        )
        for msg in mails:
            try:
                smtp.send_message(msg)
            except Exception:
                _LOGGER.error("Sending mail %s failed", msg, exc_info=True)
                failed.append(msg)

    return failed
