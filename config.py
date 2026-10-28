"""Configuration module for Remedial Hub Telegram Bot.

Loads settings from environment variables with safe defaults and provides
centralized access to bank details, group links, and admin identifiers.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import List, Optional
from dotenv import load_dotenv

# Load variables from .env file into environment
load_dotenv()


def _parse_admin_ids(raw_ids: str) -> List[int]:
    """Parse comma-separated admin IDs into a list of integers."""
    admin_ids: List[int] = []
    if not raw_ids:
        return admin_ids
    for item in raw_ids.split(","):
        cleaned = item.strip()
        if cleaned.isdigit() or (cleaned.startswith("-") and cleaned[1:].isdigit()):
            admin_ids.append(int(cleaned))
    return admin_ids


def _parse_optional_int(val: Optional[str]) -> Optional[int]:
    """Parse an integer or return None if empty/invalid."""
    if not val:
        return None
    val = val.strip()
    try:
        return int(val)
    except ValueError:
        return None


@dataclass(frozen=True)
class Config:
    """Application configuration container."""

    # Bot Credentials
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "").strip()

    # Administrators
    ADMIN_IDS: List[int] = field(
        default_factory=lambda: _parse_admin_ids(os.getenv("ADMIN_IDS", ""))
    )

    # Support & Official Channel Links
    SUPPORT_URL: str = os.getenv("SUPPORT_URL", "https://t.me/Remedial_Hub").strip()
    CHANNEL_USERNAME: str = os.getenv("CHANNEL_USERNAME", "@RemediallHub").strip()

    # Financial & Registration Settings
    FEE_AMOUNT: str = os.getenv("FEE_AMOUNT", "250").strip()

    # Payment Accounts
    TELEBIRR_NAME: str = os.getenv("TELEBIRR_NAME", "Ashenafi Asegid").strip()
    TELEBIRR_NUMBER: str = os.getenv("TELEBIRR_NUMBER", "0919417450").strip()

    BOA_ACCOUNT_NAME: str = os.getenv("BOA_ACCOUNT_NAME", "Ashenafi Asegid").strip()
    BOA_ACCOUNT_NUMBER: str = os.getenv("BOA_ACCOUNT_NUMBER", "221100751").strip()

    # Private Group IDs (Negative numbers for supergroups, e.g. -100...)
    NATURAL_GROUP_ID: Optional[int] = _parse_optional_int(os.getenv("NATURAL_GROUP_ID"))
    SOCIAL_GROUP_ID: Optional[int] = _parse_optional_int(os.getenv("SOCIAL_GROUP_ID"))

    # Fallback Links if group invite creation fails or groups not configured
    NATURAL_FALLBACK_LINK: str = os.getenv(
        "NATURAL_FALLBACK_LINK", "https://t.me/+RemedialHubNatural"
    ).strip()
    SOCIAL_FALLBACK_LINK: str = os.getenv(
        "SOCIAL_FALLBACK_LINK", "https://t.me/+RemedialHubSocial"
    ).strip()

    # Media File IDs
    HOW_TO_VIDEO_FILE_ID: Optional[str] = (
        os.getenv("HOW_TO_VIDEO_FILE_ID", "").strip() or None
    )

    # Database
    DB_NAME: str = os.getenv("DB_NAME", "remedial_hub.db").strip()

    # Optional Proxy URL (e.g. http://127.0.0.1:1080 or socks5://127.0.0.1:1080)
    PROXY_URL: Optional[str] = os.getenv("PROXY_URL", "").strip() or None

    def get_payment_details_text(self, bank_code: str) -> str:
        """Return formatted HTML payment instructions for the specified bank."""
        if bank_code in ("bank_Telebirr", "Telebirr"):
            return (
                "🏦 <b>ቴሌብር (Telebirr) የክፍያ መረጃ፦</b>\n\n"
                f"💰 <b>የሚከፈል መጠን፦</b> {self.FEE_AMOUNT} ብር\n"
                f"⚠️ <i>ከ {self.FEE_AMOUNT} ብር በታችም ሆነ በላይ መክፈል ተቀባይነት የለውም!</i>\n\n"
                f"👤 <b>የሂሳብ ስም፦</b> {self.TELEBIRR_NAME}\n"
                "💳 <b>ስልክ ቁጥር (ይጫኑት ኮፒ ይሆናል)፦</b>\n"
                f"<code>{self.TELEBIRR_NUMBER}</code>\n"
                "─────────────────────\n\n"
                "ክፍያ ከፈጸሙ በኋላ ከታች ያለውን <b>Send Payment Screenshot</b> "
                "የሚለውን በመጫን የከፈሉበትን ደረሰኝ (ፎቶ ወይም ዶክመንት) ይላኩ።"
            )
        elif bank_code in ("bank_BOA", "BOA", "Bank of Abyssinia"):
            return (
                "🏦 <b>አቢሲንያ ባንክ (Bank of Abyssinia) የክፍያ መረጃ፦</b>\n\n"
                f"💰 <b>የሚከፈል መጠን፦</b> {self.FEE_AMOUNT} ብር\n"
                f"⚠️ <i>ከ {self.FEE_AMOUNT} ብር በታችም ሆነ በላይ መክፈል ተቀባይነት የለውም!</i>\n\n"
                f"👤 <b>የሂሳብ ስም፦</b> {self.BOA_ACCOUNT_NAME}\n"
                "💳 <b>የሂሳብ ቁጥር (ይጫኑት ኮፒ ይሆናል)፦</b>\n"
                f"<code>{self.BOA_ACCOUNT_NUMBER}</code>\n"
                "─────────────────────\n\n"
                "ክፍያ ከፈጸሙ በኋላ ከታች ያለውን <b>Send Payment Screenshot</b> "
                "የሚለውን በመጫን የከፈሉበትን ደረሰኝ (ፎቶ ወይም ዶክመንት) ይላኩ።"
            )
        else:
            return (
                f"💰 <b>የሚከፈል መጠን፦</b> {self.FEE_AMOUNT} ብር\n"
                "እባክዎ ትክክለኛ የባንክ አማራጭ ይምረጡ።"
            )

    def is_admin(self, user_id: int) -> bool:
        """Check whether a given user ID is an authorized administrator."""
        return user_id in self.ADMIN_IDS


# Global configuration singleton instance
config = Config()
