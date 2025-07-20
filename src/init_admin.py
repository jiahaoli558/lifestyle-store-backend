#!/usr/bin/env python3
"""
数据库初始化脚本 - 创建admin用户和角色
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.models.models import db, User, Role, UserRole
from flask import Flask

def init_admin_user():
    """初始化admin用户和角色"""
    
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
            
            # 1. 创建admin角色（如果不存在）
            admin_role = Role.query.filter_by(name='admin').first()
            if not admin_role:
                admin_role = Role(
                    name='admin',
                    description='系统管理员',
                    permissions=['manage_products', 'manage_orders', 'manage_users', 'view_analytics']
                )
                db.session.add(admin_role)
                print("✓ 创建admin角色")
            else:
                print("✓ admin角色已存在")
            
            # 2. 创建admin用户（如果不存在）
            admin_user = User.query.filter_by(username='admin').first()
            if not admin_user:
                admin_user = User(
                    username='admin',
                    email='admin@example.com'
                )
                admin_user.set_password('admin123')  # 使用User模型的set_password方法
                db.session.add(admin_user)
                db.session.flush()  # 获取用户ID
                print("✓ 创建admin用户")
            else:
                print("✓ admin用户已存在")
            
            # 3. 创建用户角色关联（如果不存在）
            user_role = UserRole.query.filter_by(user_id=admin_user.id, role_id=admin_role.id).first()
            if not user_role:
                user_role = UserRole(
                    user_id=admin_user.id,
                    role_id=admin_role.id
                )
                db.session.add(user_role)
                print("✓ 创建admin用户角色关联")
            else:
                print("✓ admin用户角色关联已存在")
            
            # 提交所有更改
            db.session.commit()
            print("\n🎉 Admin用户初始化完成！")
            print("管理员登录信息：")
            print("用户名: admin")
            print("密码: admin123")
            print("登录地址: http://localhost:5173/admin/login")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ 初始化失败: {str(e)}")
            return False
            
    return True

if __name__ == '__main__':
    print("开始初始化admin用户...")
    success = init_admin_user()
    if success:
        print("\n✅ 初始化成功！现在可以使用admin/admin123登录管理后台了。")
    else:
        print("\n❌ 初始化失败！请检查错误信息。")

