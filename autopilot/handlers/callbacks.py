"""Callback handler registrations for application buttons.

This module centralizes callback handlers that are invoked from the main menu
and elsewhere. It registers handlers on import via the callback_router.
"""
from __future__ import annotations

import logging
from ..callbacks import callback_router
from ..keyboards.factory import KeyboardFactory

logger = logging.getLogger("autopilot.handlers.callbacks")


async def dev_callback(update, client):
    try:
        await update.callback_query.answer("معلومات المطور: @YourDev", show_alert=False)
    except Exception:
        logger.exception("Failed to answer dev callback")


async def support_callback(update, client):
    try:
        await update.callback_query.answer("قناة الدعم: https://t.me/your_support_channel", show_alert=False)
    except Exception:
        logger.exception("Failed to answer support callback")


async def updates_callback(update, client):
    try:
        await update.callback_query.answer("قناة التحديثات: https://t.me/your_updates_channel", show_alert=False)
    except Exception:
        logger.exception("Failed to answer updates callback")


async def gift_callback(update, client):
    try:
        await update.callback_query.answer("تم إرسال هديتك اليومية! 🎁", show_alert=False)
    except Exception:
        logger.exception("Failed to answer gift callback")


# register callbacks
callback_router.register("developer", dev_callback)
callback_router.register("support", support_callback)
callback_router.register("updates", updates_callback)
callback_router.register("gift", gift_callback)
