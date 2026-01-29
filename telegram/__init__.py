"""
__init__.py - تهيئة Telegram package
"""
# استيراد الـ handlers الجديدة
from . import bot_handlers
from .bot_handlers import bot

def send_otp_message(user_id, otp):
    """إرسال كود OTP للمستخدم عبر البوت"""
    try:
        message = (
            "🔐 *كود التحقق*\n\n"
            f"الكود الخاص بك: `{otp}`\n\n"
            "⏱ صالح لمدة 5 دقائق\n\n"
            "⚠️ لا تشارك هذا الكود مع أي شخص"
        )
        bot.send_message(
            int(user_id),
            message,
            parse_mode="Markdown"
        )
        return True
    except Exception as e:
        print(f"❌ خطأ في إرسال OTP: {e}")
        return False

__all__ = ['bot_handlers', 'send_otp_message']
