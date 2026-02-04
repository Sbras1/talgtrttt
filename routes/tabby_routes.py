#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مسارات تابي (Tabby Routes)
==========================
معالجة طلبات الدفع بالتقسيط عبر تابي
"""

from flask import Blueprint, request, jsonify, render_template, redirect
import time

from firebase_utils import db
from config import SITE_URL
from services.tabby_service import (
    create_tabby_session,
    verify_tabby_webhook,
    get_payment_status,
    capture_payment,
    is_tabby_configured,
    is_amount_eligible,
    TABBY_MIN_AMOUNT,
    TABBY_MAX_AMOUNT
)

# استيراد البوت للإشعارات
try:
    from telegram.bot_handlers import bot, ADMIN_ID, BOT_ACTIVE, pending_payments
    from notifications import notify_payment_success
except:
    bot = None
    ADMIN_ID = None
    BOT_ACTIVE = False
    pending_payments = {}

tabby_bp = Blueprint('tabby', __name__)


@tabby_bp.route('/tabby/check', methods=['GET'])
def check_tabby():
    """التحقق من إعداد تابي"""
    return jsonify({
        'configured': is_tabby_configured(),
        'min_amount': TABBY_MIN_AMOUNT,
        'max_amount': TABBY_MAX_AMOUNT
    })


@tabby_bp.route('/tabby/create', methods=['POST'])
def create_tabby_payment():
    """إنشاء طلب دفع تابي"""
    
    data = request.json or {}
    
    order_id = data.get('order_id')
    amount = data.get('amount')
    phone = data.get('phone')
    name = data.get('name', 'عميل')
    email = data.get('email')
    user_id = data.get('user_id')
    
    if not all([order_id, amount, phone]):
        return jsonify({
            'success': False,
            'error': 'البيانات غير مكتملة'
        }), 400
    
    try:
        amount = float(amount)
    except:
        return jsonify({
            'success': False,
            'error': 'المبلغ غير صحيح'
        }), 400
    
    if not is_amount_eligible(amount):
        return jsonify({
            'success': False,
            'error': f'تابي متاح للمبالغ بين {TABBY_MIN_AMOUNT} و {TABBY_MAX_AMOUNT} ريال'
        }), 400
    
    # إنشاء الجلسة
    result = create_tabby_session(
        order_id=order_id,
        amount=amount,
        customer_phone=phone,
        customer_name=name,
        customer_email=email
    )
    
    if result.get('success'):
        # حفظ الطلب المعلق
        expires_at = result.get('expires_at', time.time() + 1800)
        
        pending_data = {
            'user_id': str(user_id) if user_id else '',
            'amount': amount,
            'order_id': order_id,
            'phone': phone,
            'payment_method': 'tabby',
            'status': 'pending',
            'created_at': time.time(),
            'expires_at': expires_at,
            'tabby_session_id': result.get('session_id'),
            'tabby_payment_id': result.get('payment_id')
        }
        
        pending_payments[order_id] = pending_data
        
        try:
            from google.cloud.firestore import SERVER_TIMESTAMP
            pending_data['created_at'] = SERVER_TIMESTAMP
            db.collection('pending_payments').document(order_id).set(pending_data)
        except Exception as e:
            print(f"⚠️ خطأ في حفظ طلب تابي: {e}")
        
        return jsonify({
            'success': True,
            'checkout_url': result['checkout_url']
        })
    else:
        return jsonify({
            'success': False,
            'error': result.get('error', 'فشل إنشاء جلسة تابي'),
            'rejected': result.get('rejected', False)
        }), 400


@tabby_bp.route('/tabby/webhook', methods=['POST'])
def tabby_webhook():
    """استقبال إشعارات تابي (Webhook)"""
    
    data = request.json or {}
    print(f"📩 Tabby Webhook: {data}")
    
    if not verify_tabby_webhook(data):
        print("🚫 Tabby Webhook: بيانات غير صالحة")
        return jsonify({'status': 'error'}), 400
    
    payment_id = data.get('id')
    status = data.get('status', '').upper()
    order_ref = data.get('order', {}).get('reference_id', '')
    amount = float(data.get('amount', 0))
    
    print(f"📋 Tabby: payment_id={payment_id}, status={status}, order={order_ref}")
    
    # حالات الدفع
    if status == 'AUTHORIZED':
        # الدفع تم بنجاح - نؤكده ثم نضيف الرصيد
        print(f"✅ Tabby Payment Authorized: {order_ref}")
        
        # تأكيد الدفع (Capture)
        capture_result = capture_payment(payment_id, amount)
        if not capture_result.get('success'):
            print(f"⚠️ Tabby Capture Failed: {capture_result.get('error')}")
        
        # البحث عن الطلب
        order_data = pending_payments.get(order_ref)
        if not order_data:
            try:
                doc = db.collection('pending_payments').document(order_ref).get()
                if doc.exists:
                    order_data = doc.to_dict()
            except:
                pass
        
        if order_data:
            user_id = order_data.get('user_id')
            original_amount = order_data.get('amount', amount)
            
            # إضافة الرصيد
            try:
                from firebase_utils import update_user_balance
                new_balance = update_user_balance(user_id, original_amount)
                
                # تحديث حالة الطلب
                if order_ref in pending_payments:
                    pending_payments[order_ref]['status'] = 'completed'
                
                db.collection('pending_payments').document(order_ref).update({
                    'status': 'completed',
                    'completed_at': time.time(),
                    'tabby_payment_id': payment_id
                })
                
                # إشعار المستخدم
                if BOT_ACTIVE and bot and user_id:
                    try:
                        bot.send_message(
                            int(user_id),
                            f"✅ *تم شحن رصيدك بنجاح!*\n\n"
                            f"💰 المبلغ: {original_amount} ريال\n"
                            f"💳 طريقة الدفع: تابي (تقسيط)\n"
                            f"💵 رصيدك الجديد: {new_balance} ريال",
                            parse_mode='Markdown'
                        )
                    except:
                        pass
                
                # إشعار المالك
                if BOT_ACTIVE and bot and ADMIN_ID:
                    try:
                        bot.send_message(
                            ADMIN_ID,
                            f"💳 *دفعة تابي ناجحة!*\n\n"
                            f"👤 User ID: `{user_id}`\n"
                            f"💰 المبلغ: {original_amount} ريال\n"
                            f"📋 Order: `{order_ref}`",
                            parse_mode='Markdown'
                        )
                    except:
                        pass
                
                print(f"✅ تم إضافة {original_amount} ريال للمستخدم {user_id}")
                
            except Exception as e:
                print(f"❌ خطأ في إضافة الرصيد: {e}")
        
        return jsonify({'status': 'success'})
    
    elif status == 'CLOSED':
        # الدفعة مغلقة (ملغاة أو منتهية)
        print(f"🔴 Tabby Payment Closed: {order_ref}")
        
        if order_ref in pending_payments:
            pending_payments[order_ref]['status'] = 'failed'
        
        try:
            db.collection('pending_payments').document(order_ref).update({
                'status': 'failed',
                'failure_reason': 'CLOSED'
            })
        except:
            pass
        
        return jsonify({'status': 'noted'})
    
    elif status == 'REJECTED':
        print(f"🚫 Tabby Payment Rejected: {order_ref}")
        return jsonify({'status': 'noted'})
    
    return jsonify({'status': 'ok'})


@tabby_bp.route('/tabby/success')
def tabby_success():
    """صفحة نجاح الدفع عبر تابي"""
    order_id = request.args.get('order_id', '')
    
    # التحقق من الحالة في Firebase
    is_success = False
    try:
        doc = db.collection('pending_payments').document(order_id).get()
        if doc.exists:
            data = doc.to_dict()
            is_success = data.get('status') == 'completed'
    except:
        pass
    
    if is_success:
        return render_template('payment/success.html')
    else:
        # الدفع قيد المعالجة
        return render_template('payment/pending.html', order_id=order_id)


@tabby_bp.route('/tabby/cancel')
def tabby_cancel():
    """صفحة إلغاء الدفع"""
    return render_template('payment/cancel.html')


@tabby_bp.route('/tabby/failure')
def tabby_failure():
    """صفحة فشل الدفع"""
    return render_template('payment/failed.html', 
                          error_msg='فشل الدفع عبر تابي. يرجى المحاولة مرة أخرى.')
