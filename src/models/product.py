from flask import Blueprint, request, jsonify, current_app
from flask_cors import cross_origin
from src.models.models import db, Product, Category, Order, OrderItem, User

product_bp = Blueprint('product', __name__)

@product_bp.route('/products', methods=['GET'])
@cross_origin()
def get_products():
    try:
        # Get query parameters
        category = request.args.get('category')
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        sort_by = request.args.get('sort_by', 'default')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Build query
        query = Product.query
        
        if category:
            query = query.filter(Product.category == category)
        
        if min_price is not None:
            query = query.filter(Product.price >= min_price)
            
        if max_price is not None:
            query = query.filter(Product.price <= max_price)
        
        # Apply sorting
        if sort_by == 'price-low':
            query = query.order_by(Product.price.asc())
        elif sort_by == 'price-high':
            query = query.order_by(Product.price.desc())
        elif sort_by == 'rating':
            query = query.order_by(Product.rating.desc())
        elif sort_by == 'newest':
            query = query.order_by(Product.is_new.desc(), Product.created_at.desc())
        
        # Paginate
        products = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'products': [product.to_dict() for product in products.items],
            'total': products.total,
            'pages': products.pages,
            'current_page': page
        })
    except Exception as e:
        current_app.logger.exception("--- ERROR IN GET_PRODUCTS ---")
        return jsonify({'error': str(e)}), 500

@product_bp.route('/products/<int:product_id>', methods=['GET'])
@cross_origin()
def get_product(product_id):
    try:
        product = Product.query.get_or_404(product_id)
        return jsonify(product.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@product_bp.route('/categories', methods=['GET'])
@cross_origin()
def get_categories():
    try:
        categories = Category.query.filter_by(is_active=True).all()
        return jsonify([category.to_dict() for category in categories])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@product_bp.route('/orders', methods=['POST'])
@cross_origin()
def create_order():
    try:
        data = request.get_json()
        
        # Create new order
        order = Order(
            total_amount=data['total_amount'],
            shipping_address=data['shipping_address'],
            payment_method=data['payment_method']
        )
        
        db.session.add(order)
        db.session.flush()  # Get the order ID
        
        # Add order items
        for item_data in data['items']:
            product = Product.query.get(item_data['product_id'])
            if not product:
                return jsonify({'error': f'Product {item_data["product_id"]} not found'}), 400
            
            if product.stock < item_data['quantity']:
                return jsonify({'error': f'Insufficient stock for product {product.name}'}), 400
            
            order_item = OrderItem(
                order_id=order.id,
                product_id=item_data['product_id'],
                quantity=item_data['quantity'],
                unit_price=product.price,
                total_price=product.price * item_data['quantity']
            )
            
            # Update product stock
            product.stock -= item_data['quantity']
            
            db.session.add(order_item)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Order created successfully',
            'order_id': order.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@product_bp.route('/orders/<int:order_id>', methods=['GET'])
@cross_origin()
def get_order(order_id):
    try:
        order = Order.query.get_or_404(order_id)
        return jsonify(order.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Admin routes for product management
@product_bp.route('/admin/products', methods=['POST'])
@cross_origin()
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
            rating=data.get('rating', 0.0),
            reviews=data.get('reviews', 0),
            is_new=data.get('is_new', False),
            discount=data.get('discount', 0),
            stock=data.get('stock', 0)
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

@product_bp.route('/admin/products/<int:product_id>', methods=['PUT'])
@cross_origin()
def update_product(product_id):
    try:
        product = Product.query.get_or_404(product_id)
        data = request.get_json()
        
        # Update product fields
        for field in ['name', 'description', 'price', 'original_price', 'image', 
                     'category', 'rating', 'reviews', 'is_new', 'discount', 'stock']:
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

@product_bp.route('/admin/products/<int:product_id>', methods=['DELETE'])
@cross_origin()
def delete_product(product_id):
    try:
        product = Product.query.get_or_404(product_id)
        db.session.delete(product)
        db.session.commit()
        
        return jsonify({'message': 'Product deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

