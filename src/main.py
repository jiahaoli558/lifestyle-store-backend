import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, jsonify,request
from flask_cors import CORS
from src.models.models import db, Product, Category, Order, OrderItem, User
from src.routes.user import user_bp
from src.routes.product import product_bp
from flask_bcrypt import Bcrypt # 新增这一行
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Enable CORS for all routes
CORS(app,resources={r"/api/*": {"origins": [
    "https://lifestyle-store-frontend-production.up.railway.app",
    "http://localhost:5173"
]}})

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
migrate = Migrate(app, db)
bcrypt = Bcrypt(app) # 初始化Bcrypt

db.init_app(app) # 将db绑定到app

# Register blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(product_bp, url_prefix='/api')

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

@app.route('/health')
def health_check():
    return {'status': 'healthy', 'message': 'LifeStyle Store Backend API is running'}

@app.route('/api/init-data', methods=['POST'])
def init_data():
    """Initialize database with sample data"""
    try:
        # Seed categories if they don't exist
        if Category.query.count() == 0:
            categories = [
                Category(
                    id='kitchen',
                    name='厨房用品',
                    description='让烹饪变得更简单',
                    image='https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=400&h=300&fit=crop'
                ),
                Category(
                    id='home-decor',
                    name='家居装饰',
                    description='打造温馨的家',
                    image='https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=300&fit=crop'
                ),
                Category(
                    id='personal-care',
                    name='个人护理',
                    description='呵护每一天',
                    image='https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=400&h=300&fit=crop'
                )
            ]
            
            for category in categories:
                db.session.add(category)
        
        # Seed products if they don't exist
        if Product.query.count() == 0:
            products = [
                Product(
                    name='北欧风格陶瓷餐具套装',
                    description='简约北欧风格，高品质陶瓷材质，包含4人份餐具',
                    price=299,
                    original_price=399,
                    image='https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=400&h=300&fit=crop',
                    category='kitchen',
                    rating=4.8,
                    reviews=156,
                    is_new=True,
                    discount=25,
                    stock=50
                ),
                Product(
                    name='天然竹制砧板套装',
                    description='环保天然竹材，抗菌防霉，包含大中小三个尺寸',
                    price=128,
                    image='https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=400&h=300&fit=crop',
                    category='kitchen',
                    rating=4.6,
                    reviews=89,
                    is_new=False,
                    stock=30
                ),
                Product(
                    name='简约现代台灯',
                    description='LED护眼台灯，三档调光，USB充电，适合阅读办公',
                    price=199,
                    original_price=259,
                    image='https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=300&fit=crop',
                    category='home-decor',
                    rating=4.7,
                    reviews=234,
                    is_new=False,
                    discount=23,
                    stock=25
                ),
                Product(
                    name='多肉植物装饰摆件',
                    description='仿真多肉植物，免打理，北欧风格装饰，适合桌面摆放',
                    price=68,
                    image='https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=400&h=300&fit=crop',
                    category='home-decor',
                    rating=4.5,
                    reviews=67,
                    is_new=True,
                    stock=100
                ),
                Product(
                    name='天然精油香薰套装',
                    description='纯天然植物精油，薰衣草香型，舒缓压力，改善睡眠',
                    price=158,
                    image='https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=400&h=300&fit=crop',
                    category='personal-care',
                    rating=4.9,
                    reviews=312,
                    is_new=False,
                    stock=45
                ),
                Product(
                    name='有机棉毛巾套装',
                    description='100%有机棉，柔软吸水，包含浴巾、面巾、方巾各一条',
                    price=89,
                    original_price=119,
                    image='https://images.unsplash.com/photo-1631889993959-41b4e9c6e3c5?w=400&h=300&fit=crop',
                    category='personal-care',
                    rating=4.4,
                    reviews=128,
                    is_new=False,
                    discount=25,
                    stock=60
                ),
                Product(
                    name='不锈钢保温水杯',
                    description='316不锈钢内胆，24小时保温，500ml容量，适合日常使用',
                    price=79,
                    image='https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=400&h=300&fit=crop',
                    category='kitchen',
                    rating=4.6,
                    reviews=203,
                    is_new=True,
                    stock=80
                ),
                Product(
                    name='创意收纳盒套装',
                    description='可折叠收纳盒，多种尺寸，适合衣物、杂物整理收纳',
                    price=45,
                    image='https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&h=300&fit=crop',
                    category='home-decor',
                    rating=4.3,
                    reviews=95,
                    is_new=False,
                    stock=120
                )
            ]
            
            for product in products:
                db.session.add(product)
        
        db.session.commit()
        return jsonify({'message': 'Database initialized successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
