from flask import Blueprint, request, jsonify
from src.models.models import db, User # User模型现在包含了set_password和check_password方法

class User(db.Model):
    # ... 你的字段 ...
    def set_password(self, password):
        self.password_hash = generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    user_bp = Blueprint('user', __name__)

    # 现有获取所有用户的路由 (保留)
    @user_bp.route('/users', methods=['GET'])
    def get_users():
        try:
            users = User.query.all()
            # 注意：to_dict() 方法不应该返回password_hash，确保它是安全的
            return jsonify([user.to_dict() for user in users])
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # 新增：用户注册路由
    @user_bp.route('/register', methods=['POST'])
    def register():
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not username or not email or not password:
            return jsonify({'message': 'Missing username, email or password'}), 400

        # 检查用户名或邮箱是否已存在
        if User.query.filter_by(username=username).first():
            return jsonify({'message': 'Username already exists'}), 409 # 409 Conflict

        if User.query.filter_by(email=email).first():
            return jsonify({'message': 'Email already exists'}), 409

        new_user = User(username=username, email=email)
        new_user.set_password(password) # 使用User模型的方法设置哈希后的密码
        db.session.add(new_user)
        db.session.commit()

        return jsonify({'message': 'User registered successfully'}), 201 # 201 Created

    # 新增：用户登录路由
    @user_bp.route('/login', methods=['POST'])
    def login():
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'message': 'Missing username or password'}), 400

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password): # 使用User模型的方法检查密码
            # 登录成功，这里可以生成并返回一个token（例如JWT）
            # 为了简化，我们暂时只返回成功信息和用户名
            return jsonify({'message': 'Login successful', 'username': user.username}), 200
        else:
            return jsonify({'message': 'Invalid username or password'}), 401 # 401 Unauthorized

    # 移除或修改原有的 create_user 路由，因为它不安全地直接接收 password_hash
    # @user_bp.route('/users', methods=['POST'])
    # def create_user():
    #     try:
    #         data = request.get_json()
    #         user = User(
    #             username=data['username'],
    #             email=data['email'],
    #             password_hash=data.get('password_hash', '')
    #         )
    #         db.session.add(user)
    #         db.session.commit()
    #         return jsonify({
    #             'message': 'User created successfully',
    #             'user': user.to_dict()
    #         }), 201
    #     except Exception as e:
    #         db.session.rollback()
    #         return jsonify({'error': str(e)}), 500


