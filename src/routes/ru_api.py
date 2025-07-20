from flask import Blueprint, request, jsonify
from models.models import db, User, Order, OrderItem, Address
from models.ru_models import RuPorcelain, RuCategory, RuPorcelainImage, RuPorcelainReview, RuKnowledge, RuInquiry
from datetime import datetime
import json

ru_bp = Blueprint('ru', __name__)

# ========== 汝瓷商品相关API ==========

@ru_bp.route('/porcelains', methods=['GET'])
def get_porcelains():
    """获取汝瓷商品列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 12, type=int)
        category_id = request.args.get('category_id', type=int)
        glaze_color = request.args.get('glaze_color')
        vessel_type = request.args.get('vessel_type')
        collection_level = request.args.get('collection_level')
        dynasty_period = request.args.get('dynasty_period')
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        search = request.args.get('search')
        sort_by = request.args.get('sort_by', 'created_at')  # created_at, price, view_count
        sort_order = request.args.get('sort_order', 'desc')  # asc, desc
        
        # 构建查询
        query = RuPorcelain.query.filter_by(is_active=True)
        
        # 分类筛选
        if category_id:
            query = query.filter_by(category_id=category_id)
        
        # 汝瓷特有属性筛选
        if glaze_color:
            query = query.filter_by(glaze_color=glaze_color)
        if vessel_type:
            query = query.filter_by(vessel_type=vessel_type)
        if collection_level:
            query = query.filter_by(collection_level=collection_level)
        if dynasty_period:
            query = query.filter_by(dynasty_period=dynasty_period)
        
        # 价格筛选
        if min_price:
            query = query.filter(RuPorcelain.price >= min_price)
        if max_price:
            query = query.filter(RuPorcelain.price <= max_price)
        
        # 搜索
        if search:
            search_term = f'%{search}%'
            query = query.filter(
                db.or_(
                    RuPorcelain.name.like(search_term),
                    RuPorcelain.description.like(search_term),
                    RuPorcelain.artist_info.like(search_term),
                    RuPorcelain.provenance.like(search_term)
                )
            )
        
        # 排序
        if sort_by == 'price':
            if sort_order == 'asc':
                query = query.order_by(RuPorcelain.price.asc())
            else:
                query = query.order_by(RuPorcelain.price.desc())
        elif sort_by == 'view_count':
            query = query.order_by(RuPorcelain.view_count.desc())
        else:  # created_at
            if sort_order == 'asc':
                query = query.order_by(RuPorcelain.created_at.asc())
            else:
                query = query.order_by(RuPorcelain.created_at.desc())
        
        # 分页
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        porcelains = [p.to_dict() for p in pagination.items]
        
        return jsonify({
            'success': True,
            'data': {
                'porcelains': porcelains,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': pagination.total,
                    'pages': pagination.pages,
                    'has_next': pagination.has_next,
                    'has_prev': pagination.has_prev
                }
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@ru_bp.route('/porcelains/<int:porcelain_id>', methods=['GET'])
def get_porcelain_detail(porcelain_id):
    """获取汝瓷详情"""
    try:
        porcelain = RuPorcelain.query.get_or_404(porcelain_id)
        
        # 增加浏览量
        porcelain.view_count += 1
        db.session.commit()
        
        # 获取相关推荐（同类型或同釉色）
        related_query = RuPorcelain.query.filter(
            RuPorcelain.id != porcelain_id,
            RuPorcelain.is_active == True
        )
        
        if porcelain.vessel_type:
            related_query = related_query.filter_by(vessel_type=porcelain.vessel_type)
        elif porcelain.glaze_color:
            related_query = related_query.filter_by(glaze_color=porcelain.glaze_color)
        
        related_porcelains = related_query.limit(4).all()
        
        return jsonify({
            'success': True,
            'data': {
                'porcelain': porcelain.to_dict(),
                'related_porcelains': [p.to_dict() for p in related_porcelains]
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@ru_bp.route('/porcelains/featured', methods=['GET'])
def get_featured_porcelains():
    """获取推荐汝瓷"""
    try:
        limit = request.args.get('limit', 8, type=int)
        
        porcelains = RuPorcelain.query.filter_by(
            is_active=True, 
            is_featured=True
        ).order_by(RuPorcelain.created_at.desc()).limit(limit).all()
        
        return jsonify({
            'success': True,
            'data': [p.to_dict() for p in porcelains]
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@ru_bp.route('/porcelains/rare', methods=['GET'])
def get_rare_porcelains():
    """获取珍品汝瓷"""
    try:
        limit = request.args.get('limit', 6, type=int)
        
        porcelains = RuPorcelain.query.filter_by(
            is_active=True, 
            is_rare=True
        ).order_by(RuPorcelain.price.desc()).limit(limit).all()
        
        return jsonify({
            'success': True,
            'data': [p.to_dict() for p in porcelains]
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ========== 汝瓷分类相关API ==========

@ru_bp.route('/categories', methods=['GET'])
def get_categories():
    """获取汝瓷分类"""
    try:
        category_type = request.args.get('type')  # vessel_type, glaze_color, collection_level, dynasty_period
        
        query = RuCategory.query.filter_by(is_active=True)
        
        if category_type:
            query = query.filter_by(category_type=category_type)
        
        categories = query.order_by(RuCategory.sort_order).all()
        
        # 构建树形结构
        category_tree = []
        category_dict = {cat.id: cat.to_dict() for cat in categories}
        
        for cat in categories:
            cat_dict = category_dict[cat.id]
            if cat.parent_id is None:
                cat_dict['children'] = []
                category_tree.append(cat_dict)
            else:
                if cat.parent_id in category_dict:
                    if 'children' not in category_dict[cat.parent_id]:
                        category_dict[cat.parent_id]['children'] = []
                    category_dict[cat.parent_id]['children'].append(cat_dict)
        
        return jsonify({
            'success': True,
            'data': category_tree
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ========== 汝瓷筛选选项API ==========

@ru_bp.route('/filter-options', methods=['GET'])
def get_filter_options():
    """获取筛选选项"""
    try:
        # 获取所有可用的筛选选项
        glaze_colors = db.session.query(RuPorcelain.glaze_color).filter(
            RuPorcelain.glaze_color.isnot(None),
            RuPorcelain.is_active == True
        ).distinct().all()
        
        vessel_types = db.session.query(RuPorcelain.vessel_type).filter(
            RuPorcelain.vessel_type.isnot(None),
            RuPorcelain.is_active == True
        ).distinct().all()
        
        collection_levels = db.session.query(RuPorcelain.collection_level).filter(
            RuPorcelain.collection_level.isnot(None),
            RuPorcelain.is_active == True
        ).distinct().all()
        
        dynasty_periods = db.session.query(RuPorcelain.dynasty_period).filter(
            RuPorcelain.dynasty_period.isnot(None),
            RuPorcelain.is_active == True
        ).distinct().all()
        
        # 价格范围
        price_range = db.session.query(
            db.func.min(RuPorcelain.price),
            db.func.max(RuPorcelain.price)
        ).filter(RuPorcelain.is_active == True).first()
        
        return jsonify({
            'success': True,
            'data': {
                'glaze_colors': [color[0] for color in glaze_colors if color[0]],
                'vessel_types': [vtype[0] for vtype in vessel_types if vtype[0]],
                'collection_levels': [level[0] for level in collection_levels if level[0]],
                'dynasty_periods': [period[0] for period in dynasty_periods if period[0]],
                'price_range': {
                    'min': float(price_range[0]) if price_range[0] else 0,
                    'max': float(price_range[1]) if price_range[1] else 0
                }
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ========== 汝瓷知识库API ==========

@ru_bp.route('/knowledge', methods=['GET'])
def get_knowledge():
    """获取汝瓷知识库"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        category = request.args.get('category')
        featured_only = request.args.get('featured', False, type=bool)
        
        query = RuKnowledge.query
        
        if category:
            query = query.filter_by(category=category)
        
        if featured_only:
            query = query.filter_by(is_featured=True)
        
        query = query.order_by(RuKnowledge.created_at.desc())
        
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        articles = [article.to_dict() for article in pagination.items]
        
        return jsonify({
            'success': True,
            'data': {
                'articles': articles,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': pagination.total,
                    'pages': pagination.pages
                }
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@ru_bp.route('/knowledge/<int:article_id>', methods=['GET'])
def get_knowledge_detail(article_id):
    """获取知识库文章详情"""
    try:
        article = RuKnowledge.query.get_or_404(article_id)
        
        # 增加浏览量
        article.view_count += 1
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': article.to_dict()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ========== 汝瓷询价API ==========

@ru_bp.route('/inquiries', methods=['POST'])
def create_inquiry():
    """创建询价"""
    try:
        data = request.get_json()
        
        inquiry = RuInquiry(
            porcelain_id=data['porcelain_id'],
            user_id=data.get('user_id'),
            contact_name=data['contact_name'],
            contact_phone=data['contact_phone'],
            contact_email=data.get('contact_email'),
            inquiry_type=data.get('inquiry_type', '价格咨询'),
            message=data.get('message'),
            budget_range=data.get('budget_range')
        )
        
        db.session.add(inquiry)
        
        # 增加商品询价次数
        porcelain = RuPorcelain.query.get(data['porcelain_id'])
        if porcelain:
            porcelain.inquiry_count += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '询价提交成功，我们会尽快回复您',
            'data': inquiry.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# ========== 汝瓷评价API ==========

@ru_bp.route('/porcelains/<int:porcelain_id>/reviews', methods=['GET'])
def get_porcelain_reviews(porcelain_id):
    """获取汝瓷评价"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        pagination = RuPorcelainReview.query.filter_by(
            porcelain_id=porcelain_id
        ).order_by(RuPorcelainReview.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        reviews = [review.to_dict() for review in pagination.items]
        
        return jsonify({
            'success': True,
            'data': {
                'reviews': reviews,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': pagination.total,
                    'pages': pagination.pages
                }
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@ru_bp.route('/porcelains/<int:porcelain_id>/reviews', methods=['POST'])
def create_porcelain_review(porcelain_id):
    """创建汝瓷评价"""
    try:
        data = request.get_json()
        
        review = RuPorcelainReview(
            porcelain_id=porcelain_id,
            user_id=data['user_id'],
            overall_rating=data['overall_rating'],
            glaze_rating=data.get('glaze_rating'),
            craft_rating=data.get('craft_rating'),
            condition_rating=data.get('condition_rating'),
            value_rating=data.get('value_rating'),
            title=data.get('title'),
            content=data.get('content'),
            images=json.dumps(data.get('images', [])),
            is_expert_review=data.get('is_expert_review', False),
            expert_credentials=data.get('expert_credentials'),
            is_verified_purchase=data.get('is_verified_purchase', False),
            is_anonymous=data.get('is_anonymous', False)
        )
        
        db.session.add(review)
        
        # 更新商品评分统计
        porcelain = RuPorcelain.query.get(porcelain_id)
        if porcelain:
            reviews = RuPorcelainReview.query.filter_by(porcelain_id=porcelain_id).all()
            total_rating = sum(r.overall_rating for r in reviews) + data['overall_rating']
            porcelain.review_count = len(reviews) + 1
            porcelain.rating_avg = total_rating / porcelain.review_count
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '评价提交成功',
            'data': review.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# ========== 统计API ==========

@ru_bp.route('/stats', methods=['GET'])
def get_stats():
    """获取汝瓷统计数据"""
    try:
        total_porcelains = RuPorcelain.query.filter_by(is_active=True).count()
        rare_porcelains = RuPorcelain.query.filter_by(is_active=True, is_rare=True).count()
        museum_quality = RuPorcelain.query.filter_by(is_active=True, is_museum_quality=True).count()
        
        # 按釉色统计
        glaze_stats = db.session.query(
            RuPorcelain.glaze_color,
            db.func.count(RuPorcelain.id)
        ).filter(
            RuPorcelain.is_active == True,
            RuPorcelain.glaze_color.isnot(None)
        ).group_by(RuPorcelain.glaze_color).all()
        
        # 按器型统计
        vessel_stats = db.session.query(
            RuPorcelain.vessel_type,
            db.func.count(RuPorcelain.id)
        ).filter(
            RuPorcelain.is_active == True,
            RuPorcelain.vessel_type.isnot(None)
        ).group_by(RuPorcelain.vessel_type).all()
        
        return jsonify({
            'success': True,
            'data': {
                'total_porcelains': total_porcelains,
                'rare_porcelains': rare_porcelains,
                'museum_quality': museum_quality,
                'glaze_distribution': [
                    {'glaze_color': stat[0], 'count': stat[1]} 
                    for stat in glaze_stats
                ],
                'vessel_distribution': [
                    {'vessel_type': stat[0], 'count': stat[1]} 
                    for stat in vessel_stats
                ]
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

