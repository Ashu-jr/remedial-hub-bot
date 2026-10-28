"""Finite State Machine (FSM) states for Remedial Hub Telegram Bot.

Defines the state transitions for the student registration workflow and
administrator broadcast operations.
"""

from aiogram.fsm.state import State, StatesGroup


class RegistrationFSM(StatesGroup):
    """States group representing the student registration journey."""

    waiting_for_name = State()            # Student enters full name
    waiting_for_stream = State()          # Student selects Natural or Social Science
    waiting_for_bank = State()            # Student chooses CBE, BOA, or Telebirr
    waiting_for_screenshot_btn = State()  # Student views bank details and clicks Send Screenshot
    waiting_for_receipt = State()         # Student uploads payment screenshot or PDF document


class AdminBroadcastFSM(StatesGroup):
    """States group representing administrator broadcast flow."""

    waiting_for_message = State()         # Admin writes or forwards the broadcast message
    confirm_broadcast = State()           # Admin previews and confirms sending
