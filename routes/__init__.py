# -*- coding: utf-8 -*-
"""
حزمة المسارات - Routes Package
تحتوي على مسارات الدفع والـ API
"""

from routes.api_routes import api_bp
from routes.payment_routes import payment_bp

__all__ = [
    'api_bp',
    'payment_bp'
]
