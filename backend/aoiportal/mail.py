import logging
from dataclasses import dataclass
from typing import List, Optional, Union

from flask import render_template
from flask_mail import Mail, Message  # type: ignore

_LOGGER = logging.getLogger(__name__)

mail = Mail()


@dataclass
class Address:
    address: str
    name: Optional[str] = None

    def encode(self) -> str:
        if self.name is not None:
            return f"{self.name} <{self.address}>"
        return self.address


def encode_email(
    *,
    to: Address,
    subject: str,
    content_html: str,
    reply_to: Union[None, Address, List[Address]] = None,
    unsubscribe_link: Optional[str] = None,
) -> Message:
    full_html = render_template(
        "mail_template.html", content=content_html, unsubscribe_link=unsubscribe_link
    )
    reply_to_str: Optional[str] = None
    if isinstance(reply_to, Address):
        reply_to_str = reply_to.encode()
    elif isinstance(reply_to, list):
        reply_to_str = ",".join(x.encode() for x in reply_to)

    return Message(
        subject=subject,
        recipients=[to.encode()],
        html=full_html,
        reply_to=reply_to_str,
    )


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
    mail.send(msg)


def send_mass(mails: List[Message]) -> List[Message]:
    failed = []
    with mail.connect() as conn:
        for msg in mails:
            try:
                conn.send(msg)
            except Exception:
                _LOGGER.error("Sending mail %s failed", msg, exc_info=True)
                failed.append(msg)

    return failed
