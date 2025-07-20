#!/usr/bin/env python3
"""
汝瓷网站数据初始化脚本（简化版）
创建管理员账户和示例汝瓷数据
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.models_fixed import *
from main import app
from datetime import datetime, date

def init_ru_porcelain_data():
    """初始化汝瓷数据"""
    with app.app_context():
        # 创建所有表
        db.create_all()
        
        print("🏺 开始初始化汝瓷网站数据...")
        
        # 1. 创建管理员角色
        admin_role = Role.query.filter_by(name='admin').first()
        if not admin_role:
            admin_role = Role(
                name='admin',
                description='管理员角色'
            )
            db.session.add(admin_role)
        
        # 2. 创建管理员用户
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                email='admin@ruporcelain.com'
            )
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            db.session.flush()  # 获取用户ID
            
            # 创建用户角色关联
            user_role = UserRole(
                user_id=admin_user.id,
                role_id=admin_role.id
            )
            db.session.add(user_role)
            print("✅ 创建管理员账户: admin/admin123")
        
        # 3. 创建汝瓷分类
        categories_data = [
            {'name': '汝瓷盘', 'description': '各种规格的汝瓷盘类'},
            {'name': '汝瓷碗', 'description': '汝瓷碗类器型'},
            {'name': '汝瓷洗', 'description': '汝瓷洗类器型'},
            {'name': '汝瓷瓶', 'description': '汝瓷瓶类器型'},
            {'name': '汝瓷炉', 'description': '汝瓷香炉类'},
            {'name': '汝瓷枕', 'description': '汝瓷枕类器型'},
            {'name': '汝瓷杯', 'description': '汝瓷茶杯酒杯类'},
        ]
        
        for cat_data in categories_data:
            category = Category.query.filter_by(name=cat_data['name']).first()
            if not category:
                category = Category(
                    name=cat_data['name'],
                    description=cat_data['description']
                )
                db.session.add(category)
                print(f"✅ 创建分类: {cat_data['name']}")
        
        db.session.commit()  # 提交分类数据
        
        # 4. 创建示例汝瓷商品
        products_data = [
            {
                'name': '宋代汝窑天青釉洗',
                'description': '北宋汝窑天青釉洗，釉色纯正，开片自然，为汝窑经典器型。此洗造型端庄，釉面温润如玉，天青色中泛着淡淡的蓝色，开片呈蟹爪纹，是汝瓷中的珍品。',
                'price': 2800000.00,
                'original_price': 3200000.00,
                'stock': 1,
                'sku': 'RU-WASH-001',
                'category': '汝瓷洗',
                'image': 'https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=400&h=400&fit=crop'
            },
            {
                'name': '汝窑天青釉弦纹瓶',
                'description': '汝窑天青釉弦纹瓶，器型优美，釉色天青，弦纹装饰简洁大方。此瓶胎质细腻，釉面光润，天青色深浅变化自然，体现了汝瓷的精湛工艺。',
                'price': 1680000.00,
                'original_price': 1980000.00,
                'stock': 1,
                'sku': 'RU-VASE-002',
                'category': '汝瓷瓶',
                'image': 'https://images.unsplash.com/photo-1565193566173-7a0ee3dbe261?w=400&h=400&fit=crop'
            },
            {
                'name': '现代汝瓷天青釉茶杯',
                'description': '现代工艺制作的汝瓷天青釉茶杯，传承古法，釉色纯正。杯型优雅，手感舒适，适合日常品茶使用，是茶艺爱好者的理想选择。',
                'price': 680.00,
                'original_price': 880.00,
                'stock': 50,
                'sku': 'RU-CUP-003',
                'category': '汝瓷杯',
                'image': 'https://images.unsplash.com/photo-1544787219-7f47ccb76574?w=400&h=400&fit=crop'
            },
            {
                'name': '汝窑豆绿釉盘',
                'description': '汝窑豆绿釉盘，釉色独特，呈现淡雅的豆绿色。盘面平整，釉面均匀，开片细密，是汝瓷中较为少见的釉色品种，具有很高的收藏价值。',
                'price': 45000.00,
                'original_price': 52000.00,
                'stock': 3,
                'sku': 'RU-PLATE-004',
                'category': '汝瓷盘',
                'image': 'https://images.unsplash.com/photo-1449824913935-59a10b8d2000?w=400&h=400&fit=crop'
            },
            {
                'name': '汝瓷月白釉香炉',
                'description': '汝瓷月白釉香炉，釉色如月光般温润，造型古朴典雅。炉身比例协调，三足稳固，是焚香静心的理想器具，也是书房雅室的精美装饰。',
                'price': 12800.00,
                'original_price': 15800.00,
                'stock': 8,
                'sku': 'RU-INCENSE-005',
                'category': '汝瓷炉',
                'image': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400&h=400&fit=crop'
            }
        ]
        
        for product_data in products_data:
            product = Product.query.filter_by(sku=product_data['sku']).first()
            if not product:
                # 查找分类ID
                category = Category.query.filter_by(name=product_data['category']).first()
                category_id = category.id if category else 1
                
                product = Product(
                    name=product_data['name'],
                    description=product_data['description'],
                    price=product_data['price'],
                    original_price=product_data['original_price'],
                    stock=product_data['stock'],
                    sku=product_data['sku'],
                    category_id=category_id,
                    image=product_data['image'],
                    is_active=True
                )
                db.session.add(product)
                print(f"✅ 创建商品: {product_data['name']}")
        
        # 5. 提交所有数据
        db.session.commit()
        print("🎉 汝瓷网站数据初始化完成！")
        print("📋 登录信息:")
        print("   管理员: admin / admin123")
        print("   网站: http://localhost:5173")
        print("   管理后台: http://localhost:5173/admin/login")

if __name__ == '__main__':
    init_ru_porcelain_data()

