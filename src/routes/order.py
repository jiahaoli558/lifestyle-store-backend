from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from src.models.models_fixed import db, Order, OrderItem, User, Product
from datetime import datetime
import json

order_bp = Blueprint('order', __name__)

@order_bp.route('/orders', methods=['POST'])
@cross_origin()
def create_order():
    """创建新订单"""
    try:
        data = request.get_json()
        
        # 验证必需字段
        user_id = data.get('user_id')
        items = data.get('items', [])
        total_amount = data.get('total_amount')
        payment_method = data.get('payment_method')
        shipping_address = data.get('shipping_address')
        
        if not all([user_id, items, total_amount, payment_method, shipping_address]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # 验证用户存在
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # 创建订单
        order = Order(
            user_id=user_id,
            total_amount=total_amount,
            status='pending',
            payment_method=payment_method,
            shipping_address=json.dumps(shipping_address) if isinstance(shipping_address, dict) else shipping_address,
            created_at=datetime.utcnow()
        )
        
        db.session.add(order)
        db.session.flush()  # 获取订单ID
        
        # 创建订单项
        for item_data in items:
            product_id = item_data.get('product_id')
            quantity = item_data.get('quantity')
            price = item_data.get('price')
            
            # 验证商品存在
            product = Product.query.get(product_id)
            if not product:
                db.session.rollback()
                return jsonify({'error': f'Product {product_id} not found'}), 404
            
            # 检查库存
            if product.stock < quantity:
                db.session.rollback()
                return jsonify({'error': f'Insufficient stock for product {product.name}'}), 400
            
            # 创建订单项
            order_item = OrderItem(
                order_id=order.id,
                product_id=product_id,
                quantity=quantity,
                price=price
            )
            
            db.session.add(order_item)
            
            # 更新库存
            product.stock -= quantity
        
        db.session.commit()
        
        # 返回订单信息
        order_data = {
            'id': order.id,
            'user_id': order.user_id,
            'total_amount': float(order.total_amount),
            'status': order.status,
            'payment_method': order.payment_method,
            'shipping_address': json.loads(order.shipping_address) if order.shipping_address else None,
            'created_at': order.created_at.isoformat(),
            'items': []
        }
        
        # 添加订单项信息
        for item in order.items:
            item_data = {
                'product_id': item.product_id,
                'product_name': item.product.name if item.product else 'Unknown',
                'quantity': item.quantity,
                'price': float(item.price)
            }
            order_data['items'].append(item_data)
        
        return jsonify({
            'success': True,
            'message': 'Order created successfully',
            'order': order_data
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@order_bp.route('/orders/<int:user_id>', methods=['GET'])
@cross_origin()
def get_user_orders(user_id):
    """获取用户订单列表"""
    try:
        orders = Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc()).all()
        
        orders_data = []
        for order in orders:
            order_data = {
                'id': order.id,
                'total_amount': float(order.total_amount),
                'status': order.status,
                'payment_method': order.payment_method,
                'created_at': order.created_at.isoformat() if order.created_at else None,
                'items': []
            }
            
            # 添加订单项
            for item in order.items:
                item_data = {
                    'product_id': item.product_id,
                    'product_name': item.product.name if item.product else '商品已删除',
                    'quantity': item.quantity,
                    'price': float(item.price)
                }
                order_data['items'].append(item_data)
            
            orders_data.append(order_data)
        
        return jsonify({
            'success': True,
            'orders': orders_data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@order_bp.route('/orders/detail/<int:order_id>', methods=['GET'])
@cross_origin()
def get_order_detail(order_id):
    """获取订单详情"""
    try:
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        order_data = {
            'id': order.id,
            'user_id': order.user_id,
            'total_amount': float(order.total_amount),
            'status': order.status,
            'payment_method': order.payment_method,
            'shipping_address': json.loads(order.shipping_address) if order.shipping_address else None,
            'created_at': order.created_at.isoformat() if order.created_at else None,
            'updated_at': order.updated_at.isoformat() if order.updated_at else None,
            'items': []
        }
        
        # 添加订单项详情
        for item in order.items:
            item_data = {
                'product_id': item.product_id,
                'product': {
                    'name': item.product.name if item.product else '商品已删除',
                    'image': item.product.image if item.product else None,
                    'price': float(item.product.price) if item.product else 0
                },
                'quantity': item.quantity,
                'price': float(item.price)
            }
            order_data['items'].append(item_data)
        
        return jsonify({
            'success': True,
            'order': order_data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

