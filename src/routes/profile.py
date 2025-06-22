from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from src.models.models import db, User, UserProfile, Address, Wishlist, PaymentMethod, Notification
from datetime import datetime

profile_bp = Blueprint('profile', __name__)

# 获取用户个人资料
@profile_bp.route('/profile/<int:user_id>', methods=['GET'])
@cross_origin()
def get_user_profile(user_id):
    try:
        user = User.query.get_or_404(user_id)
        profile = UserProfile.query.filter_by(user_id=user_id).first()
        
        if not profile:
            # 如果没有profile，创建一个空的
            profile = UserProfile(user_id=user_id)
            db.session.add(profile)
            db.session.commit()
        
        return jsonify({
            'user': user.to_dict(),
            'profile': profile.to_dict()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 更新用户个人资料
@profile_bp.route('/profile/<int:user_id>', methods=['PUT'])
@cross_origin()
def update_user_profile(user_id):
    try:
        data = request.get_json()
        
        # 更新用户基本信息
        user = User.query.get_or_404(user_id)
        if 'username' in data:
            user.username = data['username']
        if 'email' in data:
            user.email = data['email']
        
        # 更新或创建用户档案
        profile = UserProfile.query.filter_by(user_id=user_id).first()
        if not profile:
            profile = UserProfile(user_id=user_id)
            db.session.add(profile)
        
        if 'first_name' in data:
            profile.first_name = data['first_name']
        if 'last_name' in data:
            profile.last_name = data['last_name']
        if 'phone' in data:
            profile.phone = data['phone']
        if 'birth_date' in data and data['birth_date']:
            profile.birth_date = datetime.strptime(data['birth_date'], '%Y-%m-%d').date()
        if 'gender' in data:
            profile.gender = data['gender']
        if 'avatar' in data:
            profile.avatar = data['avatar']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': user.to_dict(),
            'profile': profile.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# 获取用户地址列表
@profile_bp.route('/addresses/<int:user_id>', methods=['GET'])
@cross_origin()
def get_user_addresses(user_id):
    try:
        addresses = Address.query.filter_by(user_id=user_id).order_by(Address.is_default.desc(), Address.created_at.desc()).all()
        return jsonify([address.to_dict() for address in addresses])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 添加新地址
@profile_bp.route('/addresses', methods=['POST'])
@cross_origin()
def add_address():
    try:
        data = request.get_json()
        
        # 如果设置为默认地址，先取消其他默认地址
        if data.get('is_default', False):
            Address.query.filter_by(user_id=data['user_id'], is_default=True).update({'is_default': False})
        
        address = Address(
            user_id=data['user_id'],
            name=data['name'],
            phone=data['phone'],
            country=data['country'],
            province=data['province'],
            city=data['city'],
            district=data.get('district'),
            address_line=data['address_line'],
            postal_code=data.get('postal_code'),
            is_default=data.get('is_default', False)
        )
        
        db.session.add(address)
        db.session.commit()
        
        return jsonify({
            'message': 'Address added successfully',
            'address': address.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# 更新地址
@profile_bp.route('/addresses/<int:address_id>', methods=['PUT'])
@cross_origin()
def update_address(address_id):
    try:
        data = request.get_json()
        address = Address.query.get_or_404(address_id)
        
        # 如果设置为默认地址，先取消其他默认地址
        if data.get('is_default', False) and not address.is_default:
            Address.query.filter_by(user_id=address.user_id, is_default=True).update({'is_default': False})
        
        # 更新地址信息
        for field in ['name', 'phone', 'country', 'province', 'city', 'district', 'address_line', 'postal_code', 'is_default']:
            if field in data:
                setattr(address, field, data[field])
        
        db.session.commit()
        
        return jsonify({
            'message': 'Address updated successfully',
            'address': address.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# 删除地址
@profile_bp.route('/addresses/<int:address_id>', methods=['DELETE'])
@cross_origin()
def delete_address(address_id):
    try:
        address = Address.query.get_or_404(address_id)
        db.session.delete(address)
        db.session.commit()
        
        return jsonify({'message': 'Address deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# 获取用户收藏夹
@profile_bp.route('/wishlist/<int:user_id>', methods=['GET'])
@cross_origin()
def get_user_wishlist(user_id):
    try:
        wishlists = Wishlist.query.filter_by(user_id=user_id).order_by(Wishlist.created_at.desc()).all()
        return jsonify([wishlist.to_dict() for wishlist in wishlists])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 添加到收藏夹
@profile_bp.route('/wishlist', methods=['POST'])
@cross_origin()
def add_to_wishlist():
    try:
        data = request.get_json()
        
        # 检查是否已经收藏
        existing = Wishlist.query.filter_by(user_id=data['user_id'], product_id=data['product_id']).first()
        if existing:
            return jsonify({'message': 'Product already in wishlist'}), 400
        
        wishlist = Wishlist(
            user_id=data['user_id'],
            product_id=data['product_id']
        )
        
        db.session.add(wishlist)
        db.session.commit()
        
        return jsonify({
            'message': 'Product added to wishlist',
            'wishlist': wishlist.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# 从收藏夹移除
@profile_bp.route('/wishlist/<int:wishlist_id>', methods=['DELETE'])
@cross_origin()
def remove_from_wishlist(wishlist_id):
    try:
        wishlist = Wishlist.query.get_or_404(wishlist_id)
        db.session.delete(wishlist)
        db.session.commit()
        
        return jsonify({'message': 'Product removed from wishlist'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# 获取用户通知
@profile_bp.route('/notifications/<int:user_id>', methods=['GET'])
@cross_origin()
def get_user_notifications(user_id):
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        notifications = Notification.query.filter_by(user_id=user_id)\
            .order_by(Notification.created_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'notifications': [notification.to_dict() for notification in notifications.items],
            'total': notifications.total,
            'pages': notifications.pages,
            'current_page': page,
            'unread_count': Notification.query.filter_by(user_id=user_id, is_read=False).count()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 标记通知为已读
@profile_bp.route('/notifications/<int:notification_id>/read', methods=['PUT'])
@cross_origin()
def mark_notification_read(notification_id):
    try:
        notification = Notification.query.get_or_404(notification_id)
        notification.is_read = True
        db.session.commit()
        
        return jsonify({'message': 'Notification marked as read'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# 标记所有通知为已读
@profile_bp.route('/notifications/<int:user_id>/read-all', methods=['PUT'])
@cross_origin()
def mark_all_notifications_read(user_id):
    try:
        Notification.query.filter_by(user_id=user_id, is_read=False).update({'is_read': True})
        db.session.commit()
        
        return jsonify({'message': 'All notifications marked as read'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# 获取用户支付方式
@profile_bp.route('/payment-methods/<int:user_id>', methods=['GET'])
@cross_origin()
def get_user_payment_methods(user_id):
    try:
        payment_methods = PaymentMethod.query.filter_by(user_id=user_id)\
            .order_by(PaymentMethod.is_default.desc(), PaymentMethod.created_at.desc()).all()
        return jsonify([method.to_dict() for method in payment_methods])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 添加支付方式
@profile_bp.route('/payment-methods', methods=['POST'])
@cross_origin()
def add_payment_method():
    try:
        data = request.get_json()
        
        # 如果设置为默认支付方式，先取消其他默认支付方式
        if data.get('is_default', False):
            PaymentMethod.query.filter_by(user_id=data['user_id'], is_default=True).update({'is_default': False})
        
        payment_method = PaymentMethod(
            user_id=data['user_id'],
            type=data['type'],
            provider=data.get('provider'),
            last_four=data.get('last_four'),
            expiry_month=data.get('expiry_month'),
            expiry_year=data.get('expiry_year'),
            is_default=data.get('is_default', False),
            token=data.get('token')
        )
        
        db.session.add(payment_method)
        db.session.commit()
        
        return jsonify({
            'message': 'Payment method added successfully',
            'payment_method': payment_method.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# 删除支付方式
@profile_bp.route('/payment-methods/<int:method_id>', methods=['DELETE'])
@cross_origin()
def delete_payment_method(method_id):
    try:
        payment_method = PaymentMethod.query.get_or_404(method_id)
        db.session.delete(payment_method)
        db.session.commit()
        
        return jsonify({'message': 'Payment method deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

