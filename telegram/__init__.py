"""
__init__.py - تهيئة Telegram package
"""
# استيراد الـ handlers الجديدة
from . import bot_handlers
from .bot_handlers import bot

__all__ = ['bot_handlers', 'bot']
