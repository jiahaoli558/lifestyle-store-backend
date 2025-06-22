#!/usr/bin/env python3
"""
完整的数据库初始化脚本
包含admin用户、示例商品数据等
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.models.models import db, User, Role, UserRole, Product, Category
from flask import Flask

def init_database():
    """初始化完整数据库"""
    
    # 创建Flask应用实例
    app = Flask(__name__)
    
    # 配置数据库
    DATABASE_DIR = os.path.join(os.path.dirname(__file__), 'database')
    os.makedirs(DATABASE_DIR, exist_ok=True)
    DB_PATH = os.path.join(DATABASE_DIR, 'app.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DB_PATH}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'
    
    # 初始化数据库
    db.init_app(app)
    
    with app.app_context():
        try:
            # 确保表已创建
            db.create_all()
            print("✓ 数据库表已创建")
            
            # 1. 创建角色
            roles_data = [
                {'name': 'admin', 'description': '系统管理员', 'permissions': ['manage_products', 'manage_orders', 'manage_users', 'view_analytics']},
                {'name': 'user', 'description': '普通用户', 'permissions': ['view_products', 'place_orders']}
            ]
            
            for role_data in roles_data:
                role = Role.query.filter_by(name=role_data['name']).first()
                if not role:
                    role = Role(**role_data)
                    db.session.add(role)
                    print(f"✓ 创建{role_data['name']}角色")
            
            # 2. 创建admin用户
            admin_user = User.query.filter_by(username='admin').first()
            if not admin_user:
                admin_user = User(
                    username='admin',
                    email='admin@example.com'
                )
                admin_user.set_password('admin123')
                db.session.add(admin_user)
                db.session.flush()
                print("✓ 创建admin用户")
                
                # 关联admin角色
                admin_role = Role.query.filter_by(name='admin').first()
                user_role = UserRole(user_id=admin_user.id, role_id=admin_role.id)
                db.session.add(user_role)
                print("✓ 关联admin用户角色")
            
            # 3. 创建商品分类
            categories_data = [
                {
                    'id': 'kitchen',
                    'name': '厨房用品',
                    'description': '让烹饪变得更简单',
                    'image': 'https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=400&h=300&fit=crop'
                },
                {
                    'id': 'home-decor',
                    'name': '家居装饰',
                    'description': '打造温馨的家',
                    'image': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=300&fit=crop'
                },
                {
                    'id': 'personal-care',
                    'name': '个人护理',
                    'description': '呵护每一天',
                    'image': 'https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=400&h=300&fit=crop'
                }
            ]
            
            for cat_data in categories_data:
                category = Category.query.filter_by(id=cat_data['id']).first()
                if not category:
                    category = Category(**cat_data)
                    db.session.add(category)
                    print(f"✓ 创建{cat_data['name']}分类")
            
            # 4. 创建示例商品
            products_data = [
                {
                    'name': '北欧风格陶瓷餐具套装',
                    'description': '简约北欧风格，高品质陶瓷材质，包含4人份餐具',
                    'price': 299.0,
                    'original_price': 399.0,
                    'image': 'https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=400&h=300&fit=crop',
                    'category': 'kitchen',
                    'rating': 4.8,
                    'review_count': 156,
                    'is_new': True,
                    'discount': 25.0,
                    'stock': 50
                },
                {
                    'name': '天然竹制砧板套装',
                    'description': '环保天然竹材，抗菌防霉，包含大中小三个尺寸',
                    'price': 128.0,
                    'image': 'https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=400&h=300&fit=crop',
                    'category': 'kitchen',
                    'rating': 4.6,
                    'review_count': 89,
                    'is_new': False,
                    'stock': 30
                },
                {
                    'name': '简约现代台灯',
                    'description': 'LED护眼台灯，三档调光，USB充电，适合阅读办公',
                    'price': 199.0,
                    'original_price': 259.0,
                    'image': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=300&fit=crop',
                    'category': 'home-decor',
                    'rating': 4.7,
                    'review_count': 234,
                    'is_new': False,
                    'discount': 23.0,
                    'stock': 25
                },
                {
                    'name': '多肉植物装饰摆件',
                    'description': '仿真多肉植物，免打理，北欧风格装饰，适合桌面摆放',
                    'price': 68.0,
                    'image': 'https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=400&h=300&fit=crop',
                    'category': 'home-decor',
                    'rating': 4.5,
                    'review_count': 67,
                    'is_new': True,
                    'stock': 100
                },
                {
                    'name': '天然精油香薰套装',
                    'description': '纯天然植物精油，薰衣草香型，舒缓压力，改善睡眠',
                    'price': 158.0,
                    'image': 'https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=400&h=300&fit=crop',
                    'category': 'personal-care',
                    'rating': 4.9,
                    'review_count': 312,
                    'is_new': False,
                    'stock': 45
                }
            ]
            
            for prod_data in products_data:
                product = Product.query.filter_by(name=prod_data['name']).first()
                if not product:
                    product = Product(**prod_data)
                    db.session.add(product)
                    print(f"✓ 创建商品: {prod_data['name']}")
            
            # 提交所有更改
            db.session.commit()
            print("\n🎉 数据库初始化完成！")
            print("\n管理员登录信息：")
            print("用户名: admin")
            print("密码: admin123")
            print("后台地址: http://localhost:5173/admin/login")
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ 初始化失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    print("开始初始化数据库...")
    success = init_database()
    if success:
        print("\n✅ 数据库初始化成功！")
    else:
        print("\n❌ 数据库初始化失败！")

