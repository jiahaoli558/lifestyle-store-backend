#!/usr/bin/env python3
"""
汝瓷网站数据初始化脚本
创建管理员账户和示例汝瓷数据
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ==================== 关键修改点 ====================
# 1. 从 main 导入 app 和 db。这是已经配置和绑定好的实例。
from main import app
from src.database import db
# 2. 从 models 导入你需要的模型类，但不再需要导入 db。
from src.models.models import Admin, User
from src.models.ru_models import RuCategory, RuPorcelain, RuPorcelainImage, RuKnowledge
# 3. 导入 date
from datetime import datetime, date

def init_ru_porcelain_data():
    """初始化汝瓷数据"""
    with app.app_context():
        
        print("🏺 开始初始化汝瓷网站数据...")
        
        # 1. 创建管理员账户
        admin = Admin.query.filter_by(username='admin').first()
        if not admin:
            admin = Admin(
                username='admin',
                email='admin@ruporcelain.com',
                role='super_admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            print("✅ 创建管理员账户: admin/admin123")
        
        # 2. 创建汝瓷分类
        categories_data = [
            {
                'name': '按器型分类',
                'description': '根据汝瓷器型进行分类',
                'category_type': 'vessel_type',
                'children': [
                    {'name': '汝瓷盘', 'description': '各种规格的汝瓷盘类'},
                    {'name': '汝瓷碗', 'description': '汝瓷碗类器型'},
                    {'name': '汝瓷洗', 'description': '汝瓷洗类器型'},
                    {'name': '汝瓷瓶', 'description': '汝瓷瓶类器型'},
                    {'name': '汝瓷炉', 'description': '汝瓷香炉类'},
                    {'name': '汝瓷枕', 'description': '汝瓷枕类器型'},
                    {'name': '汝瓷杯', 'description': '汝瓷茶杯酒杯类'},
                ]
            },
            {
                'name': '按釉色分类',
                'description': '根据汝瓷釉色进行分类',
                'category_type': 'glaze_color',
                'children': [
                    {'name': '天青釉', 'description': '经典天青色汝瓷'},
                    {'name': '天蓝釉', 'description': '天蓝色汝瓷'},
                    {'name': '豆绿釉', 'description': '豆绿色汝瓷'},
                    {'name': '粉青釉', 'description': '粉青色汝瓷'},
                    {'name': '月白釉', 'description': '月白色汝瓷'},
                ]
            },
            {
                'name': '按收藏等级',
                'description': '根据收藏价值进行分类',
                'category_type': 'collection_level',
                'children': [
                    {'name': '博物馆级', 'description': '博物馆收藏级别的珍品汝瓷'},
                    {'name': '收藏级', 'description': '高端收藏级汝瓷'},
                    {'name': '艺术级', 'description': '艺术欣赏级汝瓷'},
                    {'name': '实用级', 'description': '日常使用级汝瓷'},
                ]
            },
            {
                'name': '按年代分类',
                'description': '根据制作年代进行分类',
                'category_type': 'dynasty_period',
                'children': [
                    {'name': '宋代汝瓷', 'description': '宋代原品汝瓷'},
                    {'name': '明清仿汝', 'description': '明清时期仿制汝瓷'},
                    {'name': '民国汝瓷', 'description': '民国时期汝瓷'},
                    {'name': '现代汝瓷', 'description': '现代制作的汝瓷'},
                ]
            }
        ]
        
        for cat_data in categories_data:
            parent_cat = RuCategory.query.filter_by(name=cat_data['name']).first()
            if not parent_cat:
                parent_cat = RuCategory(
                    name=cat_data['name'],
                    description=cat_data['description'],
                    category_type=cat_data['category_type'],
                    sort_order=categories_data.index(cat_data)
                )
                db.session.add(parent_cat)
                db.session.flush()  # 获取ID
                
                # 添加子分类
                for i, child_data in enumerate(cat_data['children']):
                    child_cat = RuCategory(
                        name=child_data['name'],
                        description=child_data['description'],
                        parent_id=parent_cat.id,
                        category_type=cat_data['category_type'],
                        sort_order=i
                    )
                    db.session.add(child_cat)
        
        print("✅ 创建汝瓷分类体系")
        
        # 3. 创建示例汝瓷商品
        ru_porcelains_data = [
            {
                'name': '宋代汝窑天青釉洗',
                'description': '北宋汝窑天青釉洗，釉色纯正，开片自然，为汝窑经典器型。此洗造型端庄，釉面温润如玉，天青色中泛着淡淡的蓝色，开片呈蟹爪纹，是汝瓷中的珍品。',
                'price': 2800000.00,
                'original_price': 3200000.00,
                'stock': 1,
                'sku': 'RU-WASH-001',
                'glaze_color': '天青',
                'glaze_quality': '温润如玉',
                'crackle_pattern': '蟹爪纹',
                'crackle_density': '适中',
                'vessel_type': '洗',
                'vessel_style': '宫廷风格',
                'firing_method': '还原焰',
                'kiln_type': '汝州窑',
                'dynasty_period': '北宋',
                'historical_significance': '北宋汝窑为宫廷烧制，传世极少，此洗为典型宋代汝窑作品',
                'artist_info': '宋代汝州窑工匠',
                'collection_level': '博物馆级',
                'authenticity': '真品',
                'height': 3.2,
                'diameter': 13.8,
                'bottom_diameter': 9.2,
                'weight': 285.5,
                'thickness': 2.8,
                'condition': '完美',
                'certificate_type': '文物证书',
                'certificate_number': 'WW-RU-2024-001',
                'appraiser': '故宫博物院陶瓷专家张教授',
                'appraisal_date': date(2024, 1, 15),
                'provenance': '河南汝州窑址出土，后经私人收藏',
                'exhibition_history': '曾在故宫博物院"汝窑瓷器特展"中展出',
                'is_featured': True,
                'is_rare': True,
                'is_museum_quality': True,
                'category_name': '汝瓷洗'
            },
            {
                'name': '汝窑天青釉弦纹瓶',
                'description': '汝窑天青釉弦纹瓶，器型优美，釉色天青，弦纹装饰简洁雅致。此瓶胎质细腻，釉面光润，开片呈鱼鳞纹，是汝瓷中的精品。',
                'price': 1680000.00,
                'stock': 1,
                'sku': 'RU-VASE-002',
                'glaze_color': '天青',
                'glaze_quality': '晶莹剔透',
                'crackle_pattern': '鱼鳞纹',
                'crackle_density': '密集',
                'vessel_type': '瓶',
                'vessel_style': '文人风格',
                'firing_method': '还原焰',
                'kiln_type': '汝州窑',
                'dynasty_period': '北宋',
                'collection_level': '收藏级',
                'authenticity': '真品',
                'height': 18.5,
                'diameter': 8.2,
                'bottom_diameter': 6.8,
                'weight': 420.3,
                'condition': '良好',
                'certificate_type': '鉴定证书',
                'is_featured': True,
                'is_rare': True,
                'category_name': '汝瓷瓶'
            },
            {
                'name': '现代汝瓷天青釉茶杯',
                'description': '现代工艺制作的汝瓷茶杯，传承宋代汝窑工艺，釉色天青，适合日常品茶使用。',
                'price': 680.00,
                'stock': 50,
                'sku': 'RU-CUP-003',
                'glaze_color': '天青',
                'glaze_quality': '温润',
                'crackle_pattern': '细纹开片',
                'crackle_density': '稀疏',
                'vessel_type': '杯',
                'vessel_style': '现代简约',
                'firing_method': '还原焰',
                'kiln_type': '现代汝瓷窑',
                'dynasty_period': '现代',
                'collection_level': '实用级',
                'authenticity': '工艺品',
                'height': 6.5,
                'diameter': 7.8,
                'weight': 85.2,
                'condition': '完美',
                'is_featured': False,
                'category_name': '汝瓷杯'
            },
            {
                'name': '汝窑豆绿釉盘',
                'description': '汝窑豆绿釉盘，釉色独特，呈豆绿色，开片自然，造型端庄大方。',
                'price': 45000.00,
                'stock': 3,
                'sku': 'RU-PLATE-004',
                'glaze_color': '豆绿',
                'glaze_quality': '温润',
                'crackle_pattern': '冰裂纹',
                'crackle_density': '适中',
                'vessel_type': '盘',
                'vessel_style': '民窑风格',
                'dynasty_period': '明代',
                'collection_level': '艺术级',
                'authenticity': '真品',
                'height': 2.8,
                'diameter': 15.2,
                'condition': '良好',
                'category_name': '汝瓷盘'
            },
            {
                'name': '汝瓷月白釉香炉',
                'description': '汝瓷月白釉香炉，釉色如月光般皎洁，三足鼎立，造型古朴典雅，适合焚香静心。',
                'price': 12800.00,
                'stock': 8,
                'sku': 'RU-INCENSE-005',
                'glaze_color': '月白',
                'glaze_quality': '如玉温润',
                'crackle_pattern': '细密开片',
                'vessel_type': '炉',
                'dynasty_period': '现代',
                'collection_level': '艺术级',
                'height': 8.5,
                'diameter': 12.0,
                'condition': '完美',
                'category_name': '汝瓷炉'
            }
        ]
        
        for porcelain_data in ru_porcelains_data:
            # 查找分类
            category = RuCategory.query.filter_by(name=porcelain_data['category_name']).first()
            
            porcelain = RuPorcelain.query.filter_by(sku=porcelain_data['sku']).first()
            if not porcelain:
                porcelain_data_copy = porcelain_data.copy()
                del porcelain_data_copy['category_name']
                porcelain_data_copy['category_id'] = category.id if category else None
                
                porcelain = RuPorcelain(**porcelain_data_copy)
                db.session.add(porcelain)
                db.session.flush()
                
                # 添加示例图片
                images_data = [
                    {
                        'image_url': f'/images/ru-porcelain/{porcelain.sku.lower()}-main.jpg',
                        'alt_text': f'{porcelain.name}主图',
                        'sort_order': 0,
                        'is_primary': True,
                        'image_type': 'overall',
                        'description': '整体展示图'
                    },
                    {
                        'image_url': f'/images/ru-porcelain/{porcelain.sku.lower()}-detail.jpg',
                        'alt_text': f'{porcelain.name}细节图',
                        'sort_order': 1,
                        'image_type': 'detail',
                        'description': '釉面细节展示'
                    },
                    {
                        'image_url': f'/images/ru-porcelain/{porcelain.sku.lower()}-crackle.jpg',
                        'alt_text': f'{porcelain.name}开片图',
                        'sort_order': 2,
                        'image_type': 'crackle',
                        'description': '开片纹理特写'
                    },
                    {
                        'image_url': f'/images/ru-porcelain/{porcelain.sku.lower()}-bottom.jpg',
                        'alt_text': f'{porcelain.name}底部图',
                        'sort_order': 3,
                        'image_type': 'bottom',
                        'description': '底部款识展示'
                    }
                ]
                
                for img_data in images_data:
                    img = RuPorcelainImage(
                        porcelain_id=porcelain.id,
                        **img_data
                    )
                    db.session.add(img)
        
        print("✅ 创建示例汝瓷商品")
        
        # 4. 创建汝瓷知识库
        knowledge_data = [
            {
                'title': '汝瓷的历史与发展',
                'content': '''汝瓷是中国宋代五大名窑之首，以其独特的天青色釉而闻名于世。汝窑始烧于北宋晚期，专为宫廷烧制瓷器，烧制时间仅约20年，传世品极为稀少。

汝瓷的特点：
1. 釉色：以天青色为主，还有天蓝、豆绿、粉青、月白等色
2. 开片：釉面有自然开片，呈蟹爪纹、鱼鳞纹等
3. 胎质：胎质细腻，呈香灰色
4. 工艺：采用还原焰烧制，釉面温润如玉

汝瓷的价值不仅在于其稀有性，更在于其代表了中国陶瓷艺术的最高成就。''',
                'category': '历史',
                'tags': '汝瓷历史,五大名窑,宋代,天青釉',
                'author': '陶瓷专家',
                'is_featured': True
            },
            {
                'title': '如何鉴别汝瓷真伪',
                'content': '''鉴别汝瓷真伪需要从多个方面综合判断：

1. 釉色特征：
   - 真品汝瓷釉色深沉，有内在的光泽
   - 天青色中带有淡淡的蓝色调
   - 釉面温润如玉，有"雨过天青云破处"的意境

2. 开片特征：
   - 开片自然，不规则
   - 开片线条有深浅变化
   - 常见蟹爪纹、鱼鳞纹等

3. 胎质特征：
   - 胎质细腻坚硬
   - 胎色呈香灰色或灰白色
   - 胎体较薄

4. 器型特征：
   - 造型端庄，线条流畅
   - 圈足规整，足端无釉
   - 器物轻重适中

5. 工艺特征：
   - 支钉痕迹细小
   - 釉面无气泡
   - 整体工艺精湛''',
                'category': '鉴别',
                'tags': '汝瓷鉴别,真伪,釉色,开片',
                'author': '鉴定专家',
                'is_featured': True
            },
            {
                'title': '汝瓷的收藏与保养',
                'content': '''汝瓷收藏注意事项：

收藏价值评估：
1. 年代：宋代原品价值最高
2. 品相：完整无损的价值更高
3. 稀有度：传世量少的器型价值高
4. 来源：有明确出处的更有价值

保养方法：
1. 避免磕碰：汝瓷胎薄易碎，需小心保护
2. 清洁方法：用软毛刷轻轻清洁，避免化学清洁剂
3. 存放环境：避免温差过大，湿度适中
4. 定期检查：观察是否有新的开片或损伤

投资建议：
1. 选择有证书的正品
2. 关注市场行情变化
3. 长期持有，不宜频繁交易
4. 学习相关知识，提高鉴赏能力''',
                'category': '收藏',
                'tags': '汝瓷收藏,保养,投资,价值',
                'author': '收藏专家'
            }
        ]
        
        for knowledge in knowledge_data:
            existing = RuKnowledge.query.filter_by(title=knowledge['title']).first()
            if not existing:
                kb = RuKnowledge(**knowledge)
                db.session.add(kb)
        
        print("✅ 创建汝瓷知识库")
        
        # 5. 创建测试用户
        test_user = User.query.filter_by(username='testuser').first()
        if not test_user:
            test_user = User(
                username='testuser',
                email='test@example.com',
                phone='13800138000',
                member_level='gold'
            )
            test_user.set_password('123456')
            db.session.add(test_user)
            print("✅ 创建测试用户: testuser/123456")
        
        # 提交所有更改
        db.session.commit()
        
        print("🎉 汝瓷网站数据初始化完成！")
        print("\n📋 登录信息：")
        print("管理员: admin / admin123")
        print("测试用户: testuser / 123456")
        print("\n🏺 已创建汝瓷商品数量:", RuPorcelain.query.count())
        print("📚 已创建知识库文章数量:", RuKnowledge.query.count())

if __name__ == '__main__':
    init_ru_porcelain_data()

