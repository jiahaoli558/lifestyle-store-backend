from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from src.models.models import db, Order, Shipment, ShipmentTracking, Notification, User
from datetime import datetime, timedelta
import random
import string

shipping_bp = Blueprint('shipping', __name__)

@shipping_bp.route('/create-shipment', methods=['POST'])
@cross_origin()
def create_shipment():
    """创建物流信息"""
    try:
        data = request.get_json()
        order_id = data.get('order_id')
        carrier = data.get('carrier', '顺丰速运')
        carrier_service = data.get('carrier_service', '标准快递')
        
        order = Order.query.get_or_404(order_id)
        
        # 生成跟踪号
        tracking_number = generate_tracking_number()
        
        # 创建物流记录
        shipment = Shipment(
            order_id=order_id,
            tracking_number=tracking_number,
            carrier=carrier,
            carrier_service=carrier_service,
            status='pending',
            shipped_at=datetime.utcnow(),
            estimated_delivery=datetime.utcnow() + timedelta(days=3)
        )
        
        db.session.add(shipment)
        db.session.flush()
        
        # 创建初始跟踪记录
        initial_tracking = ShipmentTracking(
            shipment_id=shipment.id,
            status='pending',
            location='仓库',
            description='订单已确认，正在准备发货',
            timestamp=datetime.utcnow()
        )
        
        db.session.add(initial_tracking)
        
        # 更新订单状态
        order.status = 'processing'
        
        # 发送通知
        notification = Notification(
            user_id=order.user_id,
            type='shipment_created',
            title='订单已发货',
            content=f'您的订单 #{order.id} 已发货，快递单号：{tracking_number}',
            data={'order_id': order_id, 'tracking_number': tracking_number}
        )
        db.session.add(notification)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Shipment created successfully',
            'shipment': shipment.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@shipping_bp.route('/track/<tracking_number>', methods=['GET'])
@cross_origin()
def track_shipment(tracking_number):
    """根据快递单号查询物流信息"""
    try:
        shipment = Shipment.query.filter_by(tracking_number=tracking_number).first_or_404()
        return jsonify(shipment.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@shipping_bp.route('/order/<int:order_id>/tracking', methods=['GET'])
@cross_origin()
def get_order_tracking(order_id):
    """获取订单的物流信息"""
    try:
        shipment = Shipment.query.filter_by(order_id=order_id).first()
        if not shipment:
            return jsonify({'error': 'Shipment not found'}), 404
        
        return jsonify(shipment.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@shipping_bp.route('/update-tracking', methods=['POST'])
@cross_origin()
def update_tracking():
    """更新物流跟踪信息"""
    try:
        data = request.get_json()
        shipment_id = data.get('shipment_id')
        status = data.get('status')
        location = data.get('location')
        description = data.get('description')
        
        shipment = Shipment.query.get_or_404(shipment_id)
        
        # 创建新的跟踪记录
        tracking = ShipmentTracking(
            shipment_id=shipment_id,
            status=status,
            location=location,
            description=description,
            timestamp=datetime.utcnow()
        )
        
        db.session.add(tracking)
        
        # 更新物流状态
        shipment.status = status
        if status == 'delivered':
            shipment.delivered_at = datetime.utcnow()
            # 更新订单状态
            order = Order.query.get(shipment.order_id)
            order.status = 'delivered'
            
            # 发送送达通知
            notification = Notification(
                user_id=order.user_id,
                type='order_delivered',
                title='订单已送达',
                content=f'您的订单 #{order.id} 已成功送达，感谢您的购买！',
                data={'order_id': order.id, 'tracking_number': shipment.tracking_number}
            )
            db.session.add(notification)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Tracking updated successfully',
            'tracking': tracking.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@shipping_bp.route('/simulate-tracking/<int:shipment_id>', methods=['POST'])
@cross_origin()
def simulate_tracking_updates(shipment_id):
    """模拟物流跟踪更新（用于演示）"""
    try:
        shipment = Shipment.query.get_or_404(shipment_id)
        
        # 模拟的物流状态更新
        tracking_updates = [
            {
                'status': 'picked_up',
                'location': '深圳仓库',
                'description': '快件已从仓库发出'
            },
            {
                'status': 'in_transit',
                'location': '深圳转运中心',
                'description': '快件已到达转运中心'
            },
            {
                'status': 'in_transit',
                'location': '广州转运中心',
                'description': '快件正在运输途中'
            },
            {
                'status': 'out_for_delivery',
                'location': '广州配送站',
                'description': '快件已出库，正在派送中'
            },
            {
                'status': 'delivered',
                'location': '收货地址',
                'description': '快件已签收，签收人：本人'
            }
        ]
        
        # 添加跟踪记录
        for i, update in enumerate(tracking_updates):
            tracking = ShipmentTracking(
                shipment_id=shipment_id,
                status=update['status'],
                location=update['location'],
                description=update['description'],
                timestamp=datetime.utcnow() + timedelta(hours=i*6)  # 每6小时一个更新
            )
            db.session.add(tracking)
        
        # 更新物流状态为已送达
        shipment.status = 'delivered'
        shipment.delivered_at = datetime.utcnow() + timedelta(days=2)
        
        # 更新订单状态
        order = Order.query.get(shipment.order_id)
        order.status = 'delivered'
        
        db.session.commit()
        
        return jsonify({
            'message': 'Tracking simulation completed',
            'shipment': shipment.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@shipping_bp.route('/carriers', methods=['GET'])
@cross_origin()
def get_carriers():
    """获取支持的快递公司列表"""
    carriers = [
        {'code': 'sf', 'name': '顺丰速运', 'services': ['标准快递', '次日达', '即日达']},
        {'code': 'ems', 'name': '中国邮政EMS', 'services': ['标准快递', '次日达']},
        {'code': 'sto', 'name': '申通快递', 'services': ['标准快递']},
        {'code': 'yt', 'name': '圆通速递', 'services': ['标准快递']},
        {'code': 'zto', 'name': '中通快递', 'services': ['标准快递']},
        {'code': 'yunda', 'name': '韵达速递', 'services': ['标准快递']},
        {'code': 'jd', 'name': '京东物流', 'services': ['标准快递', '次日达', '当日达']},
    ]
    
    return jsonify(carriers)

@shipping_bp.route('/estimate-delivery', methods=['POST'])
@cross_origin()
def estimate_delivery():
    """估算配送时间"""
    try:
        data = request.get_json()
        carrier = data.get('carrier', 'sf')
        service = data.get('service', '标准快递')
        destination = data.get('destination', '')
        
        # 简单的配送时间估算逻辑
        base_days = 3
        if service == '次日达':
            base_days = 1
        elif service == '当日达':
            base_days = 0
        elif service == '即日达':
            base_days = 0
        
        # 根据目的地调整时间（简化逻辑）
        if '北京' in destination or '上海' in destination or '广州' in destination or '深圳' in destination:
            base_days = max(1, base_days)
        elif '西藏' in destination or '新疆' in destination:
            base_days += 2
        
        estimated_delivery = datetime.utcnow() + timedelta(days=base_days)
        
        return jsonify({
            'estimated_delivery': estimated_delivery.isoformat(),
            'estimated_days': base_days,
            'carrier': carrier,
            'service': service
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@shipping_bp.route('/batch-update-status', methods=['POST'])
@cross_origin()
def batch_update_status():
    """批量更新订单状态（管理员功能）"""
    try:
        data = request.get_json()
        order_ids = data.get('order_ids', [])
        new_status = data.get('status')
        
        updated_orders = []
        for order_id in order_ids:
            order = Order.query.get(order_id)
            if order:
                order.status = new_status
                updated_orders.append(order.id)
                
                # 如果有物流信息，也更新物流状态
                shipment = Shipment.query.filter_by(order_id=order_id).first()
                if shipment:
                    shipment.status = new_status
        
        db.session.commit()
        
        return jsonify({
            'message': f'Updated {len(updated_orders)} orders',
            'updated_orders': updated_orders
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

def generate_tracking_number():
    """生成快递单号"""
    # 生成一个简单的跟踪号：SF + 12位数字
    prefix = 'SF'
    numbers = ''.join(random.choices(string.digits, k=12))
    return f"{prefix}{numbers}"

@shipping_bp.route('/shipping-cost', methods=['POST'])
@cross_origin()
def calculate_shipping_cost():
    """计算运费"""
    try:
        data = request.get_json()
        weight = data.get('weight', 1.0)  # 重量（kg）
        destination = data.get('destination', '')
        carrier = data.get('carrier', 'sf')
        service = data.get('service', '标准快递')
        
        # 简化的运费计算逻辑
        base_cost = 10.0  # 基础运费
        
        # 根据重量计算
        if weight > 1:
            base_cost += (weight - 1) * 5
        
        # 根据服务类型调整
        if service == '次日达':
            base_cost *= 1.5
        elif service == '当日达' or service == '即日达':
            base_cost *= 2.0
        
        # 根据目的地调整
        if '西藏' in destination or '新疆' in destination:
            base_cost *= 1.8
        elif '内蒙古' in destination or '青海' in destination:
            base_cost *= 1.3
        
        return jsonify({
            'shipping_cost': round(base_cost, 2),
            'carrier': carrier,
            'service': service,
            'weight': weight,
            'destination': destination
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

