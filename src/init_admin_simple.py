#!/usr/bin/env python3
"""
简单的管理员初始化脚本
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.models_fixed import *
from main import app

def init_admin():
    """初始化管理员账户"""
    with app.app_context():
        # 创建所有表
        db.create_all()
        
        print("🔧 开始初始化管理员账户...")
        
        # 创建管理员用户
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                email='admin@ruporcelain.com'
            )
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            print("✅ 创建管理员账户: admin/admin123")
        
        # 创建管理员记录
        admin_record = Admin.query.filter_by(username='admin').first()
        if not admin_record:
            admin_record = Admin(
                username='admin',
                email='admin@ruporcelain.com',
                role='super_admin'
            )
            admin_record.set_password('admin123')
            db.session.add(admin_record)
            print("✅ 创建管理员记录")
        
        # 创建示例分类
        categories_data = [
            {'name': '汝瓷盘', 'description': '各种规格的汝瓷盘类'},
            {'name': '汝瓷碗', 'description': '汝瓷碗类器型'},
            {'name': '汝瓷洗', 'description': '汝瓷洗类器型'},
            {'name': '汝瓷瓶', 'description': '汝瓷瓶类器型'},
            {'name': '汝瓷炉', 'description': '汝瓷香炉类'},
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
        
        # 提交数据
        db.session.commit()
        print("🎉 管理员初始化完成！")
        print("📋 登录信息:")
        print("   管理员: admin / admin123")

if __name__ == '__main__':
    init_admin()

