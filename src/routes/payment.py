from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import stripe
import os
from src.models.models_fixed import db, Order, OrderItem, Payment, PaymentMethod, User, Product
from datetime import datetime

payment_bp = Blueprint('payment', __name__)

# 设置Stripe API密钥
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY', 'sk_test_...')  # 需要设置环境变量

@payment_bp.route('/config', methods=['GET'])
@cross_origin()
def get_publishable_key():
    """获取Stripe公钥"""
    stripe_config = {
        'publicKey': os.environ.get('STRIPE_PUBLISHABLE_KEY', 'pk_test_...')
    }
    return jsonify(stripe_config)

@payment_bp.route('/create-checkout-session', methods=['POST'])
@cross_origin()
def create_checkout_session():
    """创建Stripe Checkout会话"""
    try:
        data = request.get_json()
        
        # 验证订单数据
        user_id = data.get('user_id')
        items = data.get('items', [])
        
        if not user_id or not items:
            return jsonify({'error': 'Missing required data'}), 400
        
        # 计算总金额并创建line_items
        line_items = []
        total_amount = 0
        
        for item in items:
            product = Product.query.get(item['product_id'])
            if not product:
                return jsonify({'error': f'Product {item["product_id"]} not found'}), 400
            
            quantity = item['quantity']
            unit_amount = int(product.price * 100)  # Stripe使用分为单位
            
            line_items.append({
                'price_data': {
                    'currency': 'cny',
                    'product_data': {
                        'name': product.name,
                        'images': [product.image] if product.image else [],
                    },
                    'unit_amount': unit_amount,
                },
                'quantity': quantity,
            })
            
            total_amount += product.price * quantity
        
        # 创建订单记录
        order = Order(
            user_id=user_id,
            total_amount=total_amount,
            status='pending',
            payment_status='pending',
            shipping_address=data.get('shipping_address')
        )
        db.session.add(order)
        db.session.flush()  # 获取订单ID
        
        # 创建订单项
        for item in items:
            product = Product.query.get(item['product_id'])
            order_item = OrderItem(
                order_id=order.id,
                product_id=item['product_id'],
                quantity=item['quantity'],
                unit_price=product.price,
                total_price=product.price * item['quantity']
            )
            db.session.add(order_item)
        
        # 创建Stripe Checkout会话
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=data.get('success_url', 'http://localhost:3000/payment/success?session_id={CHECKOUT_SESSION_ID}'),
            cancel_url=data.get('cancel_url', 'http://localhost:3000/payment/cancel'),
            metadata={
                'order_id': str(order.id),
                'user_id': str(user_id)
            }
        )
        
        # 创建支付记录
        payment = Payment(
            order_id=order.id,
            amount=total_amount,
            currency='CNY',
            status='pending',
            gateway='stripe',
            transaction_id=checkout_session.id
        )
        db.session.add(payment)
        db.session.commit()
        
        return jsonify({
            'checkout_session_id': checkout_session.id,
            'order_id': order.id
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@payment_bp.route('/webhook', methods=['POST'])
@cross_origin()
def stripe_webhook():
    """处理Stripe Webhook事件"""
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')
    endpoint_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError:
        return jsonify({'error': 'Invalid signature'}), 400
    
    # 处理事件
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        handle_checkout_session_completed(session)
    elif event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        handle_payment_succeeded(payment_intent)
    
    return jsonify({'status': 'success'})

def handle_checkout_session_completed(session):
    """处理支付完成事件"""
    try:
        order_id = session['metadata']['order_id']
        
        # 更新订单状态
        order = Order.query.get(order_id)
        if order:
            order.status = 'confirmed'
            order.payment_status = 'completed'
            
            # 更新支付记录
            payment = Payment.query.filter_by(
                order_id=order_id,
                transaction_id=session['id']
            ).first()
            if payment:
                payment.status = 'completed'
                payment.gateway_response = session
            
            db.session.commit()
            
            # 这里可以添加发送确认邮件、更新库存等逻辑
            
    except Exception as e:
        print(f"Error handling checkout session completed: {e}")
        db.session.rollback()

def handle_payment_succeeded(payment_intent):
    """处理支付成功事件"""
    try:
        # 根据payment_intent更新相关记录
        # 这里可以添加额外的业务逻辑
        pass
    except Exception as e:
        print(f"Error handling payment succeeded: {e}")

@payment_bp.route('/payment-status/<int:order_id>', methods=['GET'])
@cross_origin()
def get_payment_status(order_id):
    """获取支付状态"""
    try:
        order = Order.query.get_or_404(order_id)
        payment = Payment.query.filter_by(order_id=order_id).first()
        
        return jsonify({
            'order_id': order.id,
            'order_status': order.status,
            'payment_status': order.payment_status,
            'payment_details': payment.to_dict() if payment else None
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@payment_bp.route('/create-payment-intent', methods=['POST'])
@cross_origin()
def create_payment_intent():
    """创建Payment Intent（用于自定义支付表单）"""
    try:
        data = request.get_json()
        amount = data.get('amount')  # 金额（分）
        currency = data.get('currency', 'cny')
        
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency=currency,
            metadata=data.get('metadata', {})
        )
        
        return jsonify({
            'client_secret': intent.client_secret
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@payment_bp.route('/save-payment-method', methods=['POST'])
@cross_origin()
def save_payment_method():
    """保存用户支付方式"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        payment_method_id = data.get('payment_method_id')  # Stripe返回的payment method ID
        
        # 从Stripe获取支付方式详情
        payment_method = stripe.PaymentMethod.retrieve(payment_method_id)
        
        # 保存到数据库
        user_payment_method = PaymentMethod(
            user_id=user_id,
            type='credit_card',
            provider=payment_method.card.brand,
            last_four=payment_method.card.last4,
            expiry_month=payment_method.card.exp_month,
            expiry_year=payment_method.card.exp_year,
            token=payment_method_id,
            is_default=data.get('is_default', False)
        )
        
        # 如果设置为默认，取消其他默认支付方式
        if user_payment_method.is_default:
            PaymentMethod.query.filter_by(user_id=user_id, is_default=True).update({'is_default': False})
        
        db.session.add(user_payment_method)
        db.session.commit()
        
        return jsonify({
            'message': 'Payment method saved successfully',
            'payment_method': user_payment_method.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@payment_bp.route('/refund', methods=['POST'])
@cross_origin()
def create_refund():
    """创建退款"""
    try:
        data = request.get_json()
        payment_id = data.get('payment_id')
        amount = data.get('amount')  # 可选，不提供则全额退款
        reason = data.get('reason', '')
        
        payment = Payment.query.get_or_404(payment_id)
        
        # 创建Stripe退款
        refund_data = {
            'payment_intent': payment.transaction_id,
            'reason': 'requested_by_customer'
        }
        
        if amount:
            refund_data['amount'] = int(amount * 100)  # 转换为分
        
        stripe_refund = stripe.Refund.create(**refund_data)
        
        # 保存退款记录
        from src.models.models_fixed import Refund
        refund = Refund(
            payment_id=payment_id,
            amount=amount or payment.amount,
            reason=reason,
            status='pending',
            refund_id=stripe_refund.id
        )
        db.session.add(refund)
        
        # 更新支付状态
        payment.status = 'refunded' if not amount or amount >= payment.amount else 'partially_refunded'
        
        db.session.commit()
        
        return jsonify({
            'message': 'Refund created successfully',
            'refund': refund.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

