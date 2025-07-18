from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.types import DECIMAL
from src.database import db 
from datetime import datetime
import json
from werkzeug.security import generate_password_hash, check_password_hash
import uuid


# ========== 用户表模型 ==========
class User(db.Model):
    """用户表：存储用户账户信息"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    phone = db.Column(db.String(20))
    avatar = db.Column(db.String(500))
    
    # 用户状态
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    
    # 会员信息
    member_level = db.Column(db.String(20), default='bronze')  # bronze, silver, gold, platinum
    total_spent = db.Column(db.DECIMAL(10, 2), default=0)
    
    # 时间字段
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # 关系
    orders = db.relationship('Order', backref='user', lazy=True)
    addresses = db.relationship('Address', backref='user', lazy=True)
    reviews = db.relationship('Review', backref='user', lazy=True)
    wishlists = db.relationship('Wishlist', backref='user', lazy=True)
    
    def set_password(self, password):
        """设置密码"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'phone': self.phone,
            'avatar': self.avatar,
            'member_level': self.member_level,
            'total_spent': float(self.total_spent) if self.total_spent else 0,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
# ========== 用户扩展信息表 ==========
class UserProfile(db.Model):
    """用户扩展信息表：存储用户的详细资料，与User表一对一关联"""
    __tablename__ = 'user_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    # 使用 ForeignKey 将其与 users 表的 id 关联，并确保唯一，从而实现一对一关系
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    bio = db.Column(db.Text)  # 个人简介
    birthday = db.Column(db.Date)
    gender = db.Column(db.String(10))  # 'male', 'female', 'other'
    
    # 社交链接
    website_url = db.Column(db.String(255))
    twitter_handle = db.Column(db.String(50))
    facebook_profile = db.Column(db.String(255))
    
    # 偏好设置
    language_preference = db.Column(db.String(10), default='en')
    theme_preference = db.Column(db.String(10), default='light') # 'light', 'dark'
    
    # 建立关系，允许从 UserProfile.user 访问 User 对象
    user = db.relationship('User', backref=db.backref('profile', uselist=False))

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': f"{self.first_name or ''} {self.last_name or ''}".strip(),
            'bio': self.bio,
            'birthday': self.birthday.isoformat() if self.birthday else None,
            'gender': self.gender,
            'website_url': self.website_url,
            'language_preference': self.language_preference,
            'theme_preference': self.theme_preference
        }

# ========== 瓷器分类表 ==========
class Category(db.Model):
    """瓷器分类表"""
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'))  # 支持多级分类
    image = db.Column(db.String(500))
    sort_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    
    # 关系
    children = db.relationship('Category', backref=db.backref('parent', remote_side=[id]))
    products = db.relationship('Product', backref='category', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'parent_id': self.parent_id,
            'image': self.image,
            'sort_order': self.sort_order,
            'is_active': self.is_active
        }

# ========== 瓷器商品表 ==========
class Product(db.Model):
    """瓷器商品表"""
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.DECIMAL(10, 2), nullable=False)
    original_price = db.Column(db.DECIMAL(10, 2))  # 原价，用于显示折扣
    stock = db.Column(db.Integer, default=0)
    sku = db.Column(db.String(50), unique=True)  # 商品编码
    
    # 瓷器特有属性
    material = db.Column(db.String(50))  # 材质：骨瓷、青花瓷、白瓷等
    craft = db.Column(db.String(50))     # 工艺：手绘、贴花、雕刻等
    origin = db.Column(db.String(50))    # 产地：景德镇、德化等
    dynasty = db.Column(db.String(50))   # 朝代/年代
    artist = db.Column(db.String(100))   # 艺术家/工匠
    collection_value = db.Column(db.String(20))  # 收藏价值：日用、礼品、收藏
    
    # 物理属性
    dimensions = db.Column(db.String(100))  # 尺寸：长x宽x高
    weight = db.Column(db.DECIMAL(8, 2))    # 重量（克）
    capacity = db.Column(db.String(50))     # 容量（适用于茶具、餐具）
    
    # 商品状态
    is_active = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)  # 是否推荐
    is_new = db.Column(db.Boolean, default=True)        # 是否新品
    
    # 销售数据
    sales_count = db.Column(db.Integer, default=0)      # 销量
    view_count = db.Column(db.Integer, default=0)       # 浏览量
    rating_avg = db.Column(db.DECIMAL(3, 2), default=0) # 平均评分
    review_count = db.Column(db.Integer, default=0)     # 评价数量
    
    # 关系
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    images = db.relationship('ProductImage', backref='product', lazy=True, cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='product', lazy=True)
    order_items = db.relationship('OrderItem', backref='product', lazy=True)
    
    # 时间字段
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': float(self.price),
            'original_price': float(self.original_price) if self.original_price else None,
            'stock': self.stock,
            'sku': self.sku,
            'material': self.material,
            'craft': self.craft,
            'origin': self.origin,
            'dynasty': self.dynasty,
            'artist': self.artist,
            'collection_value': self.collection_value,
            'dimensions': self.dimensions,
            'weight': float(self.weight) if self.weight else None,
            'capacity': self.capacity,
            'is_active': self.is_active,
            'is_featured': self.is_featured,
            'is_new': self.is_new,
            'sales_count': self.sales_count,
            'view_count': self.view_count,
            'rating_avg': float(self.rating_avg) if self.rating_avg else 0,
            'review_count': self.review_count,
            'category_id': self.category_id,
            'images': [img.to_dict() for img in self.images],
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# ========== 商品图片表 ==========
class ProductImage(db.Model):
    """商品图片表"""
    __tablename__ = 'product_images'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    alt_text = db.Column(db.String(200))
    sort_order = db.Column(db.Integer, default=0)
    is_primary = db.Column(db.Boolean, default=False)  # 是否为主图
    image_type = db.Column(db.String(20), default='product')  # product, detail, scene
    
    def to_dict(self):
        return {
            'id': self.id,
            'image_url': self.image_url,
            'alt_text': self.alt_text,
            'sort_order': self.sort_order,
            'is_primary': self.is_primary,
            'image_type': self.image_type
        }

# ========== 订单表 ==========
class Order(db.Model):
    """订单表"""
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(32), unique=True, nullable=False)  # 订单号
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # 金额信息
    subtotal = db.Column(db.DECIMAL(10, 2), nullable=False)      # 商品小计
    shipping_fee = db.Column(db.DECIMAL(10, 2), default=0)       # 运费
    discount_amount = db.Column(db.DECIMAL(10, 2), default=0)    # 优惠金额
    total_amount = db.Column(db.DECIMAL(10, 2), nullable=False)  # 总金额
    
    # 订单状态
    status = db.Column(db.String(20), default='pending')  # pending, paid, shipped, delivered, cancelled, refunded
    payment_status = db.Column(db.String(20), default='unpaid')  # unpaid, paid, refunded
    payment_method = db.Column(db.String(50))
    
    # 收货信息
    shipping_address = db.Column(db.Text)  # JSON格式存储
    shipping_method = db.Column(db.String(50))
    tracking_number = db.Column(db.String(100))
    
    # 备注信息
    customer_notes = db.Column(db.Text)  # 客户备注
    admin_notes = db.Column(db.Text)     # 管理员备注
    
    # 时间字段
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    paid_at = db.Column(db.DateTime)
    shipped_at = db.Column(db.DateTime)
    delivered_at = db.Column(db.DateTime)
    cancelled_at = db.Column(db.DateTime)
    
    # 关系
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, **kwargs):
        super(Order, self).__init__(**kwargs)
        if not self.order_number:
            self.order_number = self.generate_order_number()
    
    @staticmethod
    def generate_order_number():
        """生成订单号"""
        import time
        timestamp = str(int(time.time()))
        random_str = str(uuid.uuid4()).replace('-', '')[:8]
        return f"PO{timestamp}{random_str}".upper()
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_number': self.order_number,
            'user_id': self.user_id,
            'subtotal': float(self.subtotal),
            'shipping_fee': float(self.shipping_fee),
            'discount_amount': float(self.discount_amount),
            'total_amount': float(self.total_amount),
            'status': self.status,
            'payment_status': self.payment_status,
            'payment_method': self.payment_method,
            'shipping_address': json.loads(self.shipping_address) if self.shipping_address else None,
            'shipping_method': self.shipping_method,
            'tracking_number': self.tracking_number,
            'customer_notes': self.customer_notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'paid_at': self.paid_at.isoformat() if self.paid_at else None,
            'shipped_at': self.shipped_at.isoformat() if self.shipped_at else None,
            'delivered_at': self.delivered_at.isoformat() if self.delivered_at else None,
            'items': [item.to_dict() for item in self.items]
        }

# ========== 订单项表 ==========
class OrderItem(db.Model):
    """订单项表"""
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    
    # 商品信息快照（防止商品信息变更影响历史订单）
    product_name = db.Column(db.String(200), nullable=False)
    product_sku = db.Column(db.String(50))
    product_image = db.Column(db.String(500))
    
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.DECIMAL(10, 2), nullable=False)
    total_price = db.Column(db.DECIMAL(10, 2), nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_name': self.product_name,
            'product_sku': self.product_sku,
            'product_image': self.product_image,
            'quantity': self.quantity,
            'unit_price': float(self.unit_price),
            'total_price': float(self.total_price)
        }

# ========== 地址表 ==========
class Address(db.Model):
    """用户地址表"""
    __tablename__ = 'addresses'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    province = db.Column(db.String(50), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    district = db.Column(db.String(50), nullable=False)
    address_line = db.Column(db.String(200), nullable=False)
    postal_code = db.Column(db.String(10))
    
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'province': self.province,
            'city': self.city,
            'district': self.district,
            'address_line': self.address_line,
            'postal_code': self.postal_code,
            'is_default': self.is_default,
            'full_address': f"{self.province}{self.city}{self.district}{self.address_line}"
        }

# ========== 商品评价表 ==========
class Review(db.Model):
    """商品评价表"""
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    
    rating = db.Column(db.Integer, nullable=False)  # 1-5星评分
    title = db.Column(db.String(200))
    content = db.Column(db.Text)
    images = db.Column(db.Text)  # JSON格式存储评价图片
    
    is_anonymous = db.Column(db.Boolean, default=False)
    is_verified = db.Column(db.Boolean, default=False)  # 是否验证购买
    
    # 管理员回复
    admin_reply = db.Column(db.Text)
    admin_reply_at = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'product_id': self.product_id,
            'rating': self.rating,
            'title': self.title,
            'content': self.content,
            'images': json.loads(self.images) if self.images else [],
            'is_anonymous': self.is_anonymous,
            'is_verified': self.is_verified,
            'admin_reply': self.admin_reply,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'user': self.user.to_dict() if self.user else None
        }

# ========== 收藏夹表 ==========
class Wishlist(db.Model):
    """收藏夹表"""
    __tablename__ = 'wishlists'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 联合唯一约束
    __table_args__ = (db.UniqueConstraint('user_id', 'product_id', name='unique_user_product'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'product_id': self.product_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'product': self.product.to_dict() if self.product else None
        }

# ========== 管理员表 ==========
class Admin(db.Model):
    """管理员表"""
    __tablename__ = 'admins'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    
    role = db.Column(db.String(20), default='admin')  # admin, super_admin
    is_active = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

# ========== 角色与权限模型 ==========

class Role(db.Model):
    """角色表：定义不同的用户角色"""
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)  # e.g., 'admin', 'customer', 'editor'
    description = db.Column(db.String(255))
    
    def __repr__(self):
        return f'<Role {self.name}>'

class UserRole(db.Model):
    """用户角色关联表：将用户和角色关联起来"""
    __tablename__ = 'user_roles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    
    # 建立关系，方便查询
    user = db.relationship('User', backref=db.backref('roles', lazy='dynamic'))
    role = db.relationship('Role', backref=db.backref('users', lazy='dynamic'))

    __table_args__ = (db.UniqueConstraint('user_id', 'role_id', name='_user_role_uc'),)

# ========== 支付相关模型 ==========

class PaymentMethod(db.Model):
    """支付方式表"""
    __tablename__ = 'payment_methods'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # 支付类型: 'credit_card', 'paypal', 'alipay', 'wechat_pay'
    method_type = db.Column(db.String(50), nullable=False)
    # 存储关键信息，如信用卡后四位、账户名等
    details = db.Column(db.String(255), nullable=False)
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='payment_methods')

class Payment(db.Model):
    """支付记录表"""
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    # 交易号，来自第三方支付平台
    transaction_id = db.Column(db.String(128), unique=True, nullable=False)
    amount = db.Column(db.DECIMAL(10, 2), nullable=False)
    # 支付状态: 'succeeded', 'failed', 'pending'
    status = db.Column(db.String(20), nullable=False, default='pending')
    payment_method_details = db.Column(db.String(255)) # 支付方式快照
    paid_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    order = db.relationship('Order', backref='payments')

class Refund(db.Model):
    """退款记录表"""
    __tablename__ = 'refunds'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    payment_id = db.Column(db.Integer, db.ForeignKey('payments.id'))
    # 退款交易号
    refund_transaction_id = db.Column(db.String(128), unique=True)
    amount = db.Column(db.DECIMAL(10, 2), nullable=False)
    reason = db.Column(db.String(255)) # 退款原因
    # 退款状态: 'completed', 'failed', 'processing'
    status = db.Column(db.String(20), nullable=False, default='processing')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    order = db.relationship('Order', backref='refunds')
    payment = db.relationship('Payment', backref='refunds')

# ========== 物流与配送模型 ==========

class Shipment(db.Model):
    """发货单模型"""
    __tablename__ = 'shipments'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    # 物流公司: 'SF Express', 'YTO Express', 'FedEx'
    carrier = db.Column(db.String(100))
    tracking_number = db.Column(db.String(100), unique=True)
    # 发货状态: 'preparing', 'shipped', 'in_transit', 'delivered'
    status = db.Column(db.String(50), default='preparing')
    shipped_at = db.Column(db.DateTime)
    estimated_delivery = db.Column(db.DateTime)
    
    order = db.relationship('Order', backref='shipments')
    # 一个发货单可以有多个物流跟踪记录
    tracking_updates = db.relationship('ShipmentTracking', backref='shipment', cascade='all, delete-orphan')

class ShipmentTracking(db.Model):
    """物流跟踪记录表"""
    __tablename__ = 'shipment_tracking'
    
    id = db.Column(db.Integer, primary_key=True)
    shipment_id = db.Column(db.Integer, db.ForeignKey('shipments.id'), nullable=False)
    location = db.Column(db.String(255)) # 当前位置
    description = db.Column(db.String(255)) # 物流描述，如“已揽收”
    # 状态码，可自定义或使用物流公司标准
    status_code = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ========== 通知模型 ==========

class Notification(db.Model):
    """通知表"""
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # 通知类型: 'order_update', 'promotion', 'system_message'
    type = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    # 是否已读
    is_read = db.Column(db.Boolean, default=False)
    # 点击通知后跳转的链接
    link = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='notifications')

