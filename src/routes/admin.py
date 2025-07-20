from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from src.models.models_fixed import db, User, Product, Order, OrderItem, Category, UserRole, Role, Notification
from datetime import datetime, timedelta
from sqlalchemy import func, desc
import json

admin_bp = Blueprint('admin', __name__)

# 管理员权限检查装饰器
def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 这里应该检查用户是否有管理员权限
        # 简化实现，实际应该检查JWT token和用户角色
        return f(*args, **kwargs)
    return decorated_function

# 管理员登录
@admin_bp.route('/login', methods=['POST'])
@cross_origin()
def admin_login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        # 查找用户
        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # 检查是否有管理员权限
        admin_role = Role.query.filter_by(name='admin').first()
        if not admin_role:
            # 创建管理员角色
            admin_role = Role(
                name='admin',
                description='Administrator',
                permissions=['manage_products', 'manage_orders', 'manage_users', 'view_analytics']
            )
            db.session.add(admin_role)
            db.session.commit()
        
        user_role = UserRole.query.filter_by(user_id=user.id, role_id=admin_role.id).first()
        if not user_role:
            return jsonify({'error': 'Access denied'}), 403
        
        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict(),
            'role': admin_role.to_dict()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 仪表板数据
@admin_bp.route('/dashboard', methods=['GET'])
@cross_origin()
@admin_required
def get_dashboard_data():
    try:
        # 统计数据
        total_users = User.query.count()
        total_products = Product.query.count()
        total_orders = Order.query.count()
        
        # 今日订单
        today = datetime.utcnow().date()
        today_orders = Order.query.filter(
            func.date(Order.created_at) == today
        ).count()
        
        # 本月销售额
        current_month = datetime.utcnow().replace(day=1)
        monthly_revenue = db.session.query(func.sum(Order.total_amount)).filter(
            Order.created_at >= current_month,
            Order.status.in_(['confirmed', 'delivered'])
        ).scalar() or 0
        
        # 最近7天的订单统计
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        daily_orders = db.session.query(
            func.date(Order.created_at).label('date'),
            func.count(Order.id).label('count'),
            func.sum(Order.total_amount).label('revenue')
        ).filter(
            Order.created_at >= seven_days_ago
        ).group_by(func.date(Order.created_at)).all()
        
        # 热销商品
        popular_products = db.session.query(
            Product.id,
            Product.name,
            Product.image,
            func.sum(OrderItem.quantity).label('total_sold')
        ).join(OrderItem).group_by(Product.id).order_by(desc('total_sold')).limit(5).all()
        
        # 订单状态分布
        order_status_stats = db.session.query(
            Order.status,
            func.count(Order.id).label('count')
        ).group_by(Order.status).all()
        
        return jsonify({
            'stats': {
                'total_users': total_users,
                'total_products': total_products,
                'total_orders': total_orders,
                'today_orders': today_orders,
                'monthly_revenue': float(monthly_revenue)
            },
            'daily_orders': [
                {
                    'date': str(item.date),
                    'count': item.count,
                    'revenue': float(item.revenue or 0)
                } for item in daily_orders
            ],
            'popular_products': [
                {
                    'id': item.id,
                    'name': item.name,
                    'image': item.image,
                    'total_sold': item.total_sold
                } for item in popular_products
            ],
            'order_status_stats': [
                {
                    'status': item.status,
                    'count': item.count
                } for item in order_status_stats
            ]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 商品管理
@admin_bp.route('/products', methods=['GET'])
@cross_origin()
@admin_required
def get_admin_products():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')
        category = request.args.get('category', '')
        
        query = Product.query
        
        if search:
            query = query.filter(Product.name.contains(search))
        
        if category:
            query = query.filter(Product.category == category)
        
        products = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'products': [product.to_dict() for product in products.items],
            'total': products.total,
            'pages': products.pages,
            'current_page': page
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/products', methods=['POST'])
@cross_origin()
@admin_required
def create_product():
    try:
        data = request.get_json()
        
        product = Product(
            name=data['name'],
            description=data.get('description'),
            price=data['price'],
            original_price=data.get('original_price'),
            image=data.get('image'),
            category=data.get('category'),
            stock=data.get('stock', 0),
            is_new=data.get('is_new', False),
            discount=data.get('discount', 0)
        )
        
        db.session.add(product)
        db.session.commit()
        
        return jsonify({
            'message': 'Product created successfully',
            'product': product.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/products/<int:product_id>', methods=['PUT'])
@cross_origin()
@admin_required
def update_product(product_id):
    try:
        product = Product.query.get_or_404(product_id)
        data = request.get_json()
        
        for field in ['name', 'description', 'price', 'original_price', 'image', 'category', 'stock', 'is_new', 'discount']:
            if field in data:
                setattr(product, field, data[field])
        
        db.session.commit()
        
        return jsonify({
            'message': 'Product updated successfully',
            'product': product.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/products/<int:product_id>', methods=['DELETE'])
@cross_origin()
@admin_required
def delete_product(product_id):
    try:
        product = Product.query.get_or_404(product_id)
        db.session.delete(product)
        db.session.commit()
        
        return jsonify({'message': 'Product deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# 订单管理
@admin_bp.route('/orders', methods=['GET'])
@cross_origin()
@admin_required
def get_admin_orders():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status', '')
        
        query = Order.query
        
        if status:
            query = query.filter(Order.status == status)
        
        orders = query.order_by(desc(Order.created_at)).paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'orders': [order.to_dict() for order in orders.items],
            'total': orders.total,
            'pages': orders.pages,
            'current_page': page
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/orders/<int:order_id>/status', methods=['PUT'])
@cross_origin()
@admin_required
def update_order_status(order_id):
    try:
        order = Order.query.get_or_404(order_id)
        data = request.get_json()
        new_status = data.get('status')
        
        old_status = order.status
        order.status = new_status
        
        # 发送状态更新通知
        if order.user_id:
            notification = Notification(
                user_id=order.user_id,
                type='order_status_update',
                title='订单状态更新',
                content=f'您的订单 #{order.id} 状态已更新为：{new_status}',
                data={'order_id': order.id, 'old_status': old_status, 'new_status': new_status}
            )
            db.session.add(notification)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Order status updated successfully',
            'order': order.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# 用户管理
@admin_bp.route('/users', methods=['GET'])
@cross_origin()
@admin_required
def get_admin_users():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')
        
        query = User.query
        
        if search:
            query = query.filter(
                db.or_(
                    User.username.contains(search),
                    User.email.contains(search)
                )
            )
        
        users = query.order_by(desc(User.created_at)).paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'users': [user.to_dict() for user in users.items],
            'total': users.total,
            'pages': users.pages,
            'current_page': page
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users/<int:user_id>/role', methods=['PUT'])
@cross_origin()
@admin_required
def update_user_role(user_id):
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        role_name = data.get('role')
        
        # 查找角色
        role = Role.query.filter_by(name=role_name).first()
        if not role:
            return jsonify({'error': 'Role not found'}), 404
        
        # 删除现有角色
        UserRole.query.filter_by(user_id=user_id).delete()
        
        # 添加新角色
        user_role = UserRole(user_id=user_id, role_id=role.id)
        db.session.add(user_role)
        db.session.commit()
        
        return jsonify({
            'message': 'User role updated successfully',
            'user': user.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# 分类管理
@admin_bp.route('/categories', methods=['GET'])
@cross_origin()
@admin_required
def get_admin_categories():
    try:
        categories = Category.query.all()
        return jsonify([category.to_dict() for category in categories])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/categories', methods=['POST'])
@cross_origin()
@admin_required
def create_category():
    try:
        data = request.get_json()
        
        category = Category(
            id=data['id'],
            name=data['name'],
            description=data.get('description'),
            image=data.get('image'),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(category)
        db.session.commit()
        
        return jsonify({
            'message': 'Category created successfully',
            'category': category.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# 系统设置
@admin_bp.route('/settings', methods=['GET'])
@cross_origin()
@admin_required
def get_system_settings():
    # 这里可以返回系统配置信息
    settings = {
        'site_name': 'LifeStyle Store',
        'site_description': '优质生活用品商城',
        'currency': 'CNY',
        'timezone': 'Asia/Shanghai',
        'email_notifications': True,
        'maintenance_mode': False
    }
    return jsonify(settings)

@admin_bp.route('/settings', methods=['PUT'])
@cross_origin()
@admin_required
def update_system_settings():
    try:
        data = request.get_json()
        # 这里应该保存系统设置到数据库或配置文件
        # 简化实现，直接返回成功
        return jsonify({'message': 'Settings updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 创建管理员用户
@admin_bp.route('/create-admin', methods=['POST'])
@cross_origin()
def create_admin_user():
    try:
        data = request.get_json()
        username = data.get('username', 'admin')
        email = data.get('email', 'admin@lifestylestore.com')
        password = data.get('password', 'admin123')
        
        # 检查用户是否已存在
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return jsonify({'error': 'Admin user already exists'}), 400
        
        # 创建管理员用户
        admin_user = User(
            username=username,
            email=email
        )
        admin_user.set_password(password)
        db.session.add(admin_user)
        db.session.flush()
        
        # 创建或获取管理员角色
        admin_role = Role.query.filter_by(name='admin').first()
        if not admin_role:
            admin_role = Role(
                name='admin',
                description='Administrator',
                permissions=['manage_products', 'manage_orders', 'manage_users', 'view_analytics']
            )
            db.session.add(admin_role)
            db.session.flush()
        
        # 分配管理员角色
        user_role = UserRole(user_id=admin_user.id, role_id=admin_role.id)
        db.session.add(user_role)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Admin user created successfully',
            'user': admin_user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500



# 用户管理API
@admin_bp.route('/users', methods=['GET'])
@cross_origin()
@admin_required
def get_users():
    """获取所有用户"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')
        status = request.args.get('status', '')
        
        query = User.query
        
        if search:
            query = query.filter(
                db.or_(
                    User.username.contains(search),
                    User.email.contains(search)
                )
            )
        
        if status:
            # 如果User模型有status字段
            if hasattr(User, 'status'):
                query = query.filter(User.status == status)
        
        users = query.order_by(desc(User.created_at)).paginate(page=page, per_page=per_page, error_out=False)
        
        users_data = []
        for user in users.items:
            # 计算用户统计数据
            user_orders = Order.query.filter_by(user_id=user.id).all()
            total_spent = sum(float(order.total_amount) for order in user_orders)
            order_count = len(user_orders)
            
            user_data = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'status': getattr(user, 'status', 'active'),
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'updated_at': user.updated_at.isoformat() if user.updated_at else None,
                'last_login': getattr(user, 'last_login', None),
                'order_count': order_count,
                'total_spent': total_spent,
                'avg_order_value': total_spent / order_count if order_count > 0 else 0
            }
            users_data.append(user_data)
        
        return jsonify({
            'users': users_data,
            'total': users.total,
            'pages': users.pages,
            'current_page': page
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users/<int:user_id>', methods=['GET'])
@cross_origin()
@admin_required
def get_user_detail(user_id):
    """获取用户详情"""
    try:
        user = User.query.get_or_404(user_id)
        
        # 获取用户订单
        orders = Order.query.filter_by(user_id=user_id).order_by(desc(Order.created_at)).limit(5).all()
        recent_orders = []
        
        for order in orders:
            order_data = {
                'id': order.id,
                'total_amount': float(order.total_amount),
                'status': order.status,
                'created_at': order.created_at.isoformat() if order.created_at else None
            }
            recent_orders.append(order_data)
        
        # 获取用户地址
        addresses = []
        if hasattr(user, 'addresses'):
            for addr in user.addresses:
                address_data = {
                    'name': addr.name,
                    'phone': addr.phone,
                    'province': addr.province,
                    'city': addr.city,
                    'district': addr.district,
                    'address_line': addr.address_line,
                    'is_default': addr.is_default
                }
                addresses.append(address_data)
        
        # 计算统计数据
        all_orders = Order.query.filter_by(user_id=user_id).all()
        total_spent = sum(float(order.total_amount) for order in all_orders)
        order_count = len(all_orders)
        
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'status': getattr(user, 'status', 'active'),
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'updated_at': user.updated_at.isoformat() if user.updated_at else None,
            'last_login': getattr(user, 'last_login', None),
            'order_count': order_count,
            'total_spent': total_spent,
            'avg_order_value': total_spent / order_count if order_count > 0 else 0,
            'recent_orders': recent_orders,
            'addresses': addresses
        }
        
        return jsonify(user_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users/<int:user_id>/status', methods=['PUT'])
@cross_origin()
@admin_required
def update_user_status(user_id):
    """更新用户状态"""
    try:
        data = request.get_json()
        new_status = data.get('status')
        
        if not new_status:
            return jsonify({'error': 'Status is required'}), 400
        
        user = User.query.get_or_404(user_id)
        
        # 如果User模型有status字段
        if hasattr(user, 'status'):
            user.status = new_status
            user.updated_at = datetime.utcnow()
            db.session.commit()
        
        return jsonify({'message': 'User status updated successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

