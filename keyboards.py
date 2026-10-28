"""Inline keyboard layouts and builders for Remedial Hub Telegram Bot.

Constructs inline keyboards matching exact layout requirements for the main menu,
multi-step student registration, admin decision actions, and broadcast controls.
"""

from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import config


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Build the Main Menu inline keyboard with exact rows."""
    builder = InlineKeyboardBuilder()

    # Row 1: Register Now
    builder.row(
        InlineKeyboardButton(text="📝 Register Now", callback_data="register_now")
    )
    # Row 2: My Status | FAQ
    builder.row(
        InlineKeyboardButton(text="📊 My Status", callback_data="my_status"),
        InlineKeyboardButton(text="❓ FAQ", callback_data="faq"),
    )
    # Row 3: How To Register? | About Us
    builder.row(
        InlineKeyboardButton(text="🎥 How To Register?", callback_data="how_to_register"),
        InlineKeyboardButton(text="ℹ️ About Us", callback_data="about_us"),
    )
    # Row 4: Testimonial
    builder.row(
        InlineKeyboardButton(text="🌟 Testimonial", callback_data="testimonial")
    )
    # Row 5: Contact Us (URL)
    builder.row(
        InlineKeyboardButton(text="📞 Contact Us", url=config.SUPPORT_URL)
    )

    return builder.as_markup()


def get_stream_keyboard() -> InlineKeyboardMarkup:
    """Build the Stream Selection keyboard."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="🔬 Natural Science", callback_data="stream_Natural Science"
        ),
        InlineKeyboardButton(
            text="📚 Social Science", callback_data="stream_Social Science"
        ),
    )
    builder.row(
        InlineKeyboardButton(text="✏️ Edit Name", callback_data="edit_name"),
        InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_reg"),
    )
    return builder.as_markup()


def get_bank_keyboard() -> InlineKeyboardMarkup:
    """Build the Bank Selection keyboard."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="🏦 Bank of Abyssinia", callback_data="bank_BOA"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="📱 Telebirr (ቴሌብር)", callback_data="bank_Telebirr"
        )
    )
    builder.row(
        InlineKeyboardButton(text="🔄 Edit Stream", callback_data="edit_stream"),
        InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_reg"),
    )
    return builder.as_markup()


def get_payment_keyboard() -> InlineKeyboardMarkup:
    """Build the payment instruction action keyboard."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="📩 Send Payment Screenshot", callback_data="send_screenshot"
        )
    )
    builder.row(
        InlineKeyboardButton(text="🔄 Change Bank", callback_data="change_bank"),
        InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_reg"),
    )
    return builder.as_markup()


def get_receipt_cancel_keyboard() -> InlineKeyboardMarkup:
    """Build single cancel button during screenshot/document upload step."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_reg")
    )
    return builder.as_markup()


def get_back_keyboard(include_register: bool = False) -> InlineKeyboardMarkup:
    """Build navigation keyboard with Back to Menu and optional Register button."""
    builder = InlineKeyboardBuilder()
    if include_register:
        builder.row(
            InlineKeyboardButton(text="📝 Register Now", callback_data="register_now")
        )
    builder.row(
        InlineKeyboardButton(text="🔙 Back to Menu", callback_data="back_to_menu")
    )
    return builder.as_markup()


def get_admin_decision_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Build admin receipt approval / rejection buttons for a specific student."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="✅ Approve", callback_data=f"admin_approve:{user_id}"
        ),
        InlineKeyboardButton(
            text="❌ Reject", callback_data=f"admin_reject:{user_id}"
        ),
    )
    return builder.as_markup()


def get_admin_dashboard_keyboard() -> InlineKeyboardMarkup:
    """Build administrator management dashboard keyboard."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="📢 Broadcast Message", callback_data="admin_broadcast"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="🔄 Refresh Stats", callback_data="admin_refresh_stats"
        ),
        InlineKeyboardButton(
            text="📥 Export Students (CSV)", callback_data="admin_export_csv"
        ),
    )
    return builder.as_markup()


def get_broadcast_confirm_keyboard() -> InlineKeyboardMarkup:
    """Build confirmation keyboard before dispatching broadcast."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="🚀 Send Now", callback_data="broadcast_send"
        ),
        InlineKeyboardButton(
            text="❌ Cancel", callback_data="broadcast_cancel"
        ),
    )
    return builder.as_markup()
