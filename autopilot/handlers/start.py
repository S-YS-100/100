"""Start command handler and main menu implementation."""
from __future__ import annotations

import logging
from typing import Any

from ..router import router
from ..keyboards.factory import KeyboardFactory
from ..callbacks import callback_router
from ..config import get_settings
from ..context import app

logger = logging.getLogger("autopilot.handlers.start")


MAIN_BUTTONS = [
    ("𖠌", "home"),
    ("◈ المطور", "developer"),
    ("◈ قناة الدعم ⚙️", "support"),
    ("◈ ٱلتحديثات 24/7 📢", "updates"),
    ("◈ الهدية اليومية 🎁", "gift"),
    ("◈ إستراحة", "break"),
    ("☰ معاينة", "preview"),
    ("⧓ نبض النظام", "monitor"),
    ("محاكي التوقع", "predictor"),
    ("المراقبة", "monitor"),
]


async def start_handler(update: Any, client: Any) -> None:
    settings = get_settings()
    chat_id = update.chat_id
    try:
        # welcome image (public URL to avoid bundling binary assets)
        photo_url = "https://i.imgur.com/6M5130G.png"
        # build inline keyboard with 2 columns
        rows = []
        row = []
        for idx, (label, action) in enumerate(MAIN_BUTTONS):
            row.append(KeyboardFactory.button(label, callback_data=f"{action}"))
            if (idx + 1) % 2 == 0:
                rows.append(row)
                row = []
        if row:
            rows.append(row)
        markup = KeyboardFactory.inline(rows)

        caption = (
            "مرحبًا! أنا روبوت Autopilot — جاهز لمساعدتك.\n\n"
            "استخدم الأزرار أدناه للتنقل بين الميزات."
        )
        # send photo with caption and keyboard
        await client.send_photo(chat_id, photo_url, caption=caption, reply_markup=markup)
    except Exception:
        logger.exception("Failed to send start message")


def register() -> None:
    router.add_handler("start", start_handler)
    # register callbacks for main buttons
    from ..callbacks import callback_router as cr

    def _make_cb(action: str):
        async def _cb(update, client):
            # simple response for each action; more complex flows are handled elsewhere
            text_map = {
                "developer": "هذا هو المطور: @YourDev",
                "support": "قم بزيارة قناة الدعم: https://t.me/your_support_channel",
                "updates": "قناة التحديثات: https://t.me/your_updates_channel",
                "gift": "استلم هديتك اليومية!",
                "break": "استرح جيدًا 💤",
                "preview": "معاينة الميزات...",
                "monitor": "نمط المراقبة مُفعل",
                "predictor": "ابدأ المحاكاة",
                "home": "عودة إلى القائمة الرئيسية",
            }
            out = text_map.get(action, "تم الضغط على الزر: " + action)
            # edit the callback message to show the selected view and a back button
            try:
                await update.callback_query.message.edit_text(out, reply_markup=KeyboardFactory.inline([[KeyboardFactory.back_button("home")]]))
                await update.callback_query.answer()
            except Exception:
                # fallback: send a new message
                await client.send_message(update.chat_id, out)

        return _cb

    for _label, action in MAIN_BUTTONS:
        cr.register(action, _make_cb(action))
