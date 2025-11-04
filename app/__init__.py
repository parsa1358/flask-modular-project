from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
import os

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-key-123'
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'sqlite:///site.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    # Setup login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'لطفاً برای دسترسی به این صفحه وارد شوید.'
    
    # User loader function
    from app.models.user import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # ==================== ثبت فیلترهای تاریخ شمسی ====================
    try:
        from app.utils.jalali_date import register_jalali_filters
        register_jalali_filters(app)
        print("✅ فیلترهای تاریخ شمسی ثبت شدند")
    except Exception as e:
        print(f"⚠️ خطا در ثبت فیلترهای تاریخ شمسی: {e}")
    
    # ثبت blueprintها
    from app.blueprints.auth import auth_bp
    from app.blueprints.main import main_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    
    # Create tables و ایجاد کاربر پیش‌فرض
    with app.app_context():
        try:
            # حذف تمام tables و ایجاد مجدد (برای توسعه)
            db.drop_all()
            db.create_all()
            print("✅ دیتابیس و جداول ایجاد شدند")
            
            from app.models.user import User
            from app.utils.security import hash_password
            
            # ایجاد کاربر ادمین در صورت عدم وجود
            admin_user = User.query.filter_by(username='admin').first()
            if not admin_user:
                admin_password = 'admin123'
                hashed_admin_password = hash_password(admin_password)
                admin_user = User(
                    username='admin',
                    email='admin@system.com',
                    password_hash=hashed_admin_password,
                    full_name='مدیر سیستم',
                    role='super_admin',
                    is_approved=True
                )
                db.session.add(admin_user)
                db.session.commit()
                print(f"✅ کاربر ادمین ایجاد شد (admin/{admin_password})")
            
            # ایجاد کاربر تستی (تایید شده)
            test_user = User.query.filter_by(username='test').first()
            if not test_user:
                test_password = 'test123'
                hashed_test_password = hash_password(test_password)
                test_user = User(
                    username='test',
                    email='test@system.com',
                    password_hash=hashed_test_password,
                    full_name='کاربر تست',
                    role='user',
                    is_approved=True
                )
                db.session.add(test_user)
                db.session.commit()
                print(f"✅ کاربر تست ایجاد شد (test/{test_password})")
                
            print("🎉 سیستم کاربران کامل شد!")
            print("   - ادمین: admin / admin123")
            print("   - کاربر عادی: test / test123")
                
        except Exception as e:
            print(f"⚠️ خطا در ایجاد دیتابیس: {e}")
            import traceback
            traceback.print_exc()
    
    return app