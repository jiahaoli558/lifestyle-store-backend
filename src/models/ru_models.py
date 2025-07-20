from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

db = SQLAlchemy()

# ========== 汝瓷商品表 ==========
class RuPorcelain(db.Model):
    """汝瓷商品表 - 专门针对汝瓷的属性设计"""
    __tablename__ = 'ru_porcelains'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Decimal(10, 2), nullable=False)
    original_price = db.Column(db.Decimal(10, 2))
    stock = db.Column(db.Integer, default=0)
    sku = db.Column(db.String(50), unique=True)
    
    # ========== 汝瓷专有属性 ==========
    
    # 釉色分类
    glaze_color = db.Column(db.String(50))  # 天青、天蓝、豆绿、粉青、月白等
    glaze_quality = db.Column(db.String(50))  # 釉质：温润如玉、晶莹剔透等
    
    # 开片特征
    crackle_pattern = db.Column(db.String(50))  # 开片：蟹爪纹、鱼鳞纹、冰裂纹等
    crackle_density = db.Column(db.String(20))  # 开片密度：稀疏、适中、密集
    
    # 器型分类
    vessel_type = db.Column(db.String(50))  # 盘、碗、洗、瓶、炉、枕等
    vessel_style = db.Column(db.String(50))  # 宫廷风格、文人风格、民窑风格
    
    # 工艺特征
    firing_method = db.Column(db.String(50))  # 烧制工艺：还原焰、氧化焰
    kiln_type = db.Column(db.String(50))     # 窑口：汝州窑、宝丰窑等
    
    # 历史信息
    dynasty_period = db.Column(db.String(50))  # 朝代：北宋、南宋、现代仿制等
    historical_significance = db.Column(db.Text)  # 历史意义
    
    # 艺术价值
    artist_info = db.Column(db.String(200))    # 制作工匠/艺术家信息
    collection_level = db.Column(db.String(30))  # 收藏等级：博物馆级、收藏级、艺术级、实用级
    authenticity = db.Column(db.String(30))    # 真伪：真品、高仿、工艺品
    
    # 物理属性
    height = db.Column(db.Decimal(8, 2))       # 高度(cm)
    diameter = db.Column(db.Decimal(8, 2))     # 直径(cm)
    bottom_diameter = db.Column(db.Decimal(8, 2))  # 底径(cm)
    weight = db.Column(db.Decimal(8, 2))       # 重量(g)
    thickness = db.Column(db.Decimal(6, 2))    # 胎体厚度(mm)
    
    # 品相描述
    condition = db.Column(db.String(50))       # 品相：完美、良好、一般、有瑕疵
    defects = db.Column(db.Text)              # 瑕疵描述
    restoration = db.Column(db.Text)          # 修复情况
    
    # 证书信息
    certificate_type = db.Column(db.String(50))  # 证书类型：文物证书、鉴定证书、收藏证书
    certificate_number = db.Column(db.String(100))  # 证书编号
    appraiser = db.Column(db.String(100))     # 鉴定专家
    appraisal_date = db.Column(db.Date)       # 鉴定日期
    
    # 来源信息
    provenance = db.Column(db.Text)           # 来源：出土地点、传承历史等
    exhibition_history = db.Column(db.Text)   # 展览历史
    publication_history = db.Column(db.Text)  # 出版著录
    
    # 商品状态
    is_active = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    is_rare = db.Column(db.Boolean, default=False)      # 是否珍品
    is_museum_quality = db.Column(db.Boolean, default=False)  # 是否博物馆级
    
    # 销售数据
    view_count = db.Column(db.Integer, default=0)
    inquiry_count = db.Column(db.Integer, default=0)    # 询价次数
    rating_avg = db.Column(db.Decimal(3, 2), default=0)
    review_count = db.Column(db.Integer, default=0)
    
    # 关系
    category_id = db.Column(db.Integer, db.ForeignKey('ru_categories.id'))
    images = db.relationship('RuPorcelainImage', backref='porcelain', lazy=True, cascade='all, delete-orphan')
    reviews = db.relationship('RuPorcelainReview', backref='porcelain', lazy=True)
    
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
            
            # 汝瓷特有属性
            'glaze_color': self.glaze_color,
            'glaze_quality': self.glaze_quality,
            'crackle_pattern': self.crackle_pattern,
            'crackle_density': self.crackle_density,
            'vessel_type': self.vessel_type,
            'vessel_style': self.vessel_style,
            'firing_method': self.firing_method,
            'kiln_type': self.kiln_type,
            'dynasty_period': self.dynasty_period,
            'historical_significance': self.historical_significance,
            'artist_info': self.artist_info,
            'collection_level': self.collection_level,
            'authenticity': self.authenticity,
            
            # 物理属性
            'height': float(self.height) if self.height else None,
            'diameter': float(self.diameter) if self.diameter else None,
            'bottom_diameter': float(self.bottom_diameter) if self.bottom_diameter else None,
            'weight': float(self.weight) if self.weight else None,
            'thickness': float(self.thickness) if self.thickness else None,
            
            # 品相和证书
            'condition': self.condition,
            'defects': self.defects,
            'restoration': self.restoration,
            'certificate_type': self.certificate_type,
            'certificate_number': self.certificate_number,
            'appraiser': self.appraiser,
            'appraisal_date': self.appraisal_date.isoformat() if self.appraisal_date else None,
            
            # 来源信息
            'provenance': self.provenance,
            'exhibition_history': self.exhibition_history,
            'publication_history': self.publication_history,
            
            # 状态
            'is_active': self.is_active,
            'is_featured': self.is_featured,
            'is_rare': self.is_rare,
            'is_museum_quality': self.is_museum_quality,
            
            # 统计数据
            'view_count': self.view_count,
            'inquiry_count': self.inquiry_count,
            'rating_avg': float(self.rating_avg) if self.rating_avg else 0,
            'review_count': self.review_count,
            
            'category_id': self.category_id,
            'images': [img.to_dict() for img in self.images],
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# ========== 汝瓷分类表 ==========
class RuCategory(db.Model):
    """汝瓷分类表"""
    __tablename__ = 'ru_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    parent_id = db.Column(db.Integer, db.ForeignKey('ru_categories.id'))
    image = db.Column(db.String(500))
    sort_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    
    # 汝瓷特有分类属性
    category_type = db.Column(db.String(50))  # 按器型、按釉色、按年代、按价值等
    
    # 关系
    children = db.relationship('RuCategory', backref=db.backref('parent', remote_side=[id]))
    porcelains = db.relationship('RuPorcelain', backref='category', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'parent_id': self.parent_id,
            'image': self.image,
            'sort_order': self.sort_order,
            'is_active': self.is_active,
            'category_type': self.category_type
        }

# ========== 汝瓷图片表 ==========
class RuPorcelainImage(db.Model):
    """汝瓷图片表"""
    __tablename__ = 'ru_porcelain_images'
    
    id = db.Column(db.Integer, primary_key=True)
    porcelain_id = db.Column(db.Integer, db.ForeignKey('ru_porcelains.id'), nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    alt_text = db.Column(db.String(200))
    sort_order = db.Column(db.Integer, default=0)
    is_primary = db.Column(db.Boolean, default=False)
    
    # 汝瓷图片特有类型
    image_type = db.Column(db.String(30), default='overall')  
    # overall:整体图, detail:细节图, bottom:底部图, crackle:开片图, 
    # side:侧面图, interior:内部图, certificate:证书图, comparison:对比图
    
    description = db.Column(db.Text)  # 图片说明
    
    def to_dict(self):
        return {
            'id': self.id,
            'image_url': self.image_url,
            'alt_text': self.alt_text,
            'sort_order': self.sort_order,
            'is_primary': self.is_primary,
            'image_type': self.image_type,
            'description': self.description
        }

# ========== 汝瓷评价表 ==========
class RuPorcelainReview(db.Model):
    """汝瓷评价表"""
    __tablename__ = 'ru_porcelain_reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    porcelain_id = db.Column(db.Integer, db.ForeignKey('ru_porcelains.id'), nullable=False)
    
    # 评分维度（针对汝瓷特点）
    overall_rating = db.Column(db.Integer, nullable=False)  # 总体评分 1-5
    glaze_rating = db.Column(db.Integer)     # 釉色评分
    craft_rating = db.Column(db.Integer)     # 工艺评分
    condition_rating = db.Column(db.Integer) # 品相评分
    value_rating = db.Column(db.Integer)     # 价值评分
    
    title = db.Column(db.String(200))
    content = db.Column(db.Text)
    images = db.Column(db.Text)  # JSON格式存储评价图片
    
    # 专业评价
    is_expert_review = db.Column(db.Boolean, default=False)  # 是否专家评价
    expert_credentials = db.Column(db.String(200))           # 专家资质
    
    is_verified_purchase = db.Column(db.Boolean, default=False)
    is_anonymous = db.Column(db.Boolean, default=False)
    
    # 管理员回复
    admin_reply = db.Column(db.Text)
    admin_reply_at = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    user = db.relationship('User', backref='ru_reviews')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'porcelain_id': self.porcelain_id,
            'overall_rating': self.overall_rating,
            'glaze_rating': self.glaze_rating,
            'craft_rating': self.craft_rating,
            'condition_rating': self.condition_rating,
            'value_rating': self.value_rating,
            'title': self.title,
            'content': self.content,
            'images': json.loads(self.images) if self.images else [],
            'is_expert_review': self.is_expert_review,
            'expert_credentials': self.expert_credentials,
            'is_verified_purchase': self.is_verified_purchase,
            'is_anonymous': self.is_anonymous,
            'admin_reply': self.admin_reply,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'user': self.user.to_dict() if self.user else None
        }

# ========== 汝瓷知识库表 ==========
class RuKnowledge(db.Model):
    """汝瓷知识库表 - 存储汝瓷相关的专业知识"""
    __tablename__ = 'ru_knowledge'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50))  # 历史、工艺、鉴别、收藏、保养等
    tags = db.Column(db.String(200))     # 标签，逗号分隔
    
    author = db.Column(db.String(100))   # 作者
    source = db.Column(db.String(200))   # 来源
    
    is_featured = db.Column(db.Boolean, default=False)
    view_count = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'category': self.category,
            'tags': self.tags.split(',') if self.tags else [],
            'author': self.author,
            'source': self.source,
            'is_featured': self.is_featured,
            'view_count': self.view_count,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# ========== 汝瓷询价表 ==========
class RuInquiry(db.Model):
    """汝瓷询价表 - 高价值汝瓷通常需要询价"""
    __tablename__ = 'ru_inquiries'
    
    id = db.Column(db.Integer, primary_key=True)
    porcelain_id = db.Column(db.Integer, db.ForeignKey('ru_porcelains.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # 询价人信息
    contact_name = db.Column(db.String(100), nullable=False)
    contact_phone = db.Column(db.String(20), nullable=False)
    contact_email = db.Column(db.String(120))
    
    # 询价内容
    inquiry_type = db.Column(db.String(30))  # 价格咨询、真伪鉴定、收藏建议等
    message = db.Column(db.Text)
    budget_range = db.Column(db.String(50))  # 预算范围
    
    # 处理状态
    status = db.Column(db.String(20), default='pending')  # pending, replied, closed
    admin_reply = db.Column(db.Text)
    replied_at = db.Column(db.DateTime)
    replied_by = db.Column(db.String(100))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    porcelain = db.relationship('RuPorcelain', backref='inquiries')
    user = db.relationship('User', backref='ru_inquiries')
    
    def to_dict(self):
        return {
            'id': self.id,
            'porcelain_id': self.porcelain_id,
            'user_id': self.user_id,
            'contact_name': self.contact_name,
            'contact_phone': self.contact_phone,
            'contact_email': self.contact_email,
            'inquiry_type': self.inquiry_type,
            'message': self.message,
            'budget_range': self.budget_range,
            'status': self.status,
            'admin_reply': self.admin_reply,
            'replied_at': self.replied_at.isoformat() if self.replied_at else None,
            'replied_by': self.replied_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'porcelain': self.porcelain.to_dict() if self.porcelain else None
        }

# 继续使用之前定义的User, Order, OrderItem, Address等通用表...

