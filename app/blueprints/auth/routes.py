from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.user import User
from app.utils.security import hash_password, verify_password
from datetime import datetime
import os
import uuid
from PIL import Image
from werkzeug.utils import secure_filename

from . import auth_bp

# تنظیمات آپلود
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def resize_image(image_path, output_path, size=(200, 200)):
    """تغییر سایز تصویر"""
    try:
        with Image.open(image_path) as img:
            img.thumbnail(size, Image.Resampling.LANCZOS)
            img.save(output_path, optimize=True, quality=85)
        return True
    except Exception as e:
        print(f"خطا در تغییر سایز تصویر: {e}")
        return False

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and verify_password(password, user.password_hash):
            # بررسی وضعیت کاربر
            if user.status == 'rejected':
                flash('❌ حساب کاربری شما رد شده است. لطفاً با مدیر سیستم تماس بگیرید.', 'danger')
                return render_template('auth/login.html')
            
            if user.status == 'pending':
                flash('⏳ حساب کاربری شما در انتظار تایید مدیر است. لطفاً منتظر بمانید.', 'warning')
                return render_template('auth/login.html')
            
            if not user.is_active:
                flash('❌ حساب کاربری شما غیرفعال است. لطفاً با مدیر سیستم تماس بگیرید.', 'danger')
                return render_template('auth/login.html')
            
            # اگر کاربر تایید شده ولی هنوز فعال نشده
            if user.status == 'approved':
                user.activate()  # تغییر وضعیت به فعال
            
            login_user(user, remember=True)
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            flash('✅ با موفقیت وارد شدید!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('❌ نام کاربری یا رمز عبور نادرست است', 'danger')
    
    return render_template('auth/login.html')
@auth_bp.route('/registration-status')
def registration_status():
    """نمایش وضعیت ثبت‌نام"""
    return render_template('auth/registration_status.html')

@auth_bp.route('/check-registration-status', methods=['POST'])
def check_registration_status():
    """بررسی وضعیت ثبت‌نام"""
    username = request.form.get('username')
    
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'success': False, 'message': 'کاربری با این نام کاربری یافت نشد'})
    
    return jsonify({
        'success': True,
        'status': user.status,
        'rejection_reason': user.rejection_reason
    })

@auth_bp.route('/reject-user/<int:user_id>', methods=['POST'])
@login_required
def reject_user(user_id):
    """رد کاربر توسط ادمین"""
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'دسترسی غیرمجاز'})
    
    user = User.query.get_or_404(user_id)
    rejection_reason = request.json.get('rejection_reason', '')
    
    user.reject(current_user, rejection_reason)
    db.session.commit()
    
    flash(f'❌ کاربر {user.full_name} رد شد.', 'success')
    return jsonify({'success': True, 'message': 'کاربر با موفقیت رد شد'})
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        
        # بررسی وجود کاربر
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('❌ این نام کاربری قبلاً ثبت شده است', 'danger')
        else:
            hashed_password = hash_password(password)
            user = User(
                username=username,
                email=email,
                password_hash=hashed_password,
                full_name=full_name,
                role='user',
                is_approved=False
            )
            db.session.add(user)
            db.session.commit()
            flash('✅ حساب کاربری با موفقیت ایجاد شد! منتظر تایید ادمین باشید.', 'success')
            return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('✅ با موفقیت از سیستم خارج شدید.', 'info')
    return redirect(url_for('main.home'))

@auth_bp.route('/profile')
@login_required
def profile():
    return render_template('auth/profile.html')

@auth_bp.route('/user-management')
@login_required
def user_management():
    if not current_user.is_admin:
        flash('❌ دسترسی غیرمجاز', 'danger')
        return redirect(url_for('main.home'))
    
    users = User.query.all()
    pending_users = User.query.filter_by(is_approved=False).count()
    return render_template('auth/user_management.html', users=users, pending_users=pending_users)

@auth_bp.route('/approve-user/<int:user_id>', methods=['POST'])
@login_required
def approve_user(user_id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'دسترسی غیرمجاز'})
    
    user = User.query.get_or_404(user_id)
    user.is_approved = True
    user.approved_at = datetime.utcnow()
    user.approved_by = current_user.id
    db.session.commit()
    
    flash(f'✅ کاربر {user.full_name} با موفقیت تایید شد.', 'success')
    return jsonify({'success': True, 'message': 'کاربر با موفقیت تایید شد'})

@auth_bp.route('/create-user', methods=['GET', 'POST'])
@login_required
def create_user():
    if not current_user.is_admin:
        flash('❌ دسترسی غیرمجاز', 'danger')
        return redirect(url_for('main.home'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        role = request.form.get('role', 'user')
        phone = request.form.get('phone')
        department = request.form.get('department')
        
        # بررسی وجود کاربر
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('❌ این نام کاربری قبلاً ثبت شده است', 'danger')
        else:
            hashed_password = hash_password(password)
            user = User(
                username=username,
                email=email,
                password_hash=hashed_password,
                full_name=full_name,
                role=role,
                phone=phone,
                department=department,
                is_approved=True,
                approved_by=current_user.id
            )
            
            # پردازش تصویر پروفایل اگر آپلود شده
            if 'profile_picture' in request.files:
                file = request.files['profile_picture']
                if file and file.filename != '' and allowed_file(file.filename):
                    # بررسی حجم فایل
                    file.seek(0, os.SEEK_END)
                    file_length = file.tell()
                    file.seek(0)
                    
                    if file_length <= MAX_FILE_SIZE:
                        # ایجاد نام فایل منحصر به فرد
                        file_ext = file.filename.rsplit('.', 1)[1].lower()
                        filename = f"{username}_{uuid.uuid4().hex[:8]}.{file_ext}"
                        
                        # مسیر ذخیره‌سازی
                        from app import create_app
                        app = create_app()
                        with app.app_context():
                            upload_dir = os.path.join(app.root_path, 'static', 'uploads', 'profiles')
                            temp_dir = os.path.join(app.root_path, 'static', 'uploads', 'temp')
                            os.makedirs(upload_dir, exist_ok=True)
                            os.makedirs(temp_dir, exist_ok=True)
                            
                            file_path = os.path.join(upload_dir, filename)
                            
                            try:
                                # ذخیره فایل موقت
                                temp_path = os.path.join(temp_dir, filename)
                                file.save(temp_path)
                                
                                # تغییر سایز تصویر
                                if resize_image(temp_path, file_path):
                                    # حذف فایل موقت
                                    os.remove(temp_path)
                                    user.profile_picture = filename
                                else:
                                    flash('⚠️ خطا در پردازش تصویر. از تصویر پیش‌فرض استفاده شد.', 'warning')
                            except Exception as e:
                                print(f"خطا در آپلود تصویر: {e}")
                                flash('⚠️ خطا در آپلود تصویر. از تصویر پیش‌فرض استفاده شد.', 'warning')
                    else:
                        flash('⚠️ حجم فایل تصویر بسیار بزرگ است. از تصویر پیش‌فرض استفاده شد.', 'warning')
            
            db.session.add(user)
            db.session.commit()
            flash(f'✅ کاربر {full_name} با موفقیت ایجاد و تایید شد.', 'success')
            return redirect(url_for('auth.user_management'))
    
    return render_template('auth/create_user.html')

@auth_bp.route('/edit-user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if not current_user.is_admin:
        flash('❌ دسترسی غیرمجاز', 'danger')
        return redirect(url_for('main.home'))
    
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        user.full_name = request.form.get('full_name')
        user.email = request.form.get('email')
        user.role = request.form.get('role')
        user.phone = request.form.get('phone')
        user.department = request.form.get('department')
        
        # پردازش تصویر پروفایل اگر آپلود شده
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and file.filename != '' and allowed_file(file.filename):
                # بررسی حجم فایل
                file.seek(0, os.SEEK_END)
                file_length = file.tell()
                file.seek(0)
                
                if file_length <= MAX_FILE_SIZE:
                    # ایجاد نام فایل منحصر به فرد
                    file_ext = file.filename.rsplit('.', 1)[1].lower()
                    filename = f"{user.username}_{uuid.uuid4().hex[:8]}.{file_ext}"
                    
                    # مسیر ذخیره‌سازی
                    from app import create_app
                    app = create_app()
                    with app.app_context():
                        upload_dir = os.path.join(app.root_path, 'static', 'uploads', 'profiles')
                        temp_dir = os.path.join(app.root_path, 'static', 'uploads', 'temp')
                        os.makedirs(upload_dir, exist_ok=True)
                        os.makedirs(temp_dir, exist_ok=True)
                        
                        file_path = os.path.join(upload_dir, filename)
                        
                        try:
                            # ذخیره فایل موقت
                            temp_path = os.path.join(temp_dir, filename)
                            file.save(temp_path)
                            
                            # تغییر سایز تصویر
                            if resize_image(temp_path, file_path):
                                # حذف فایل موقت
                                os.remove(temp_path)
                                
                                # حذف تصویر قبلی اگر وجود دارد
                                if user.profile_picture and user.profile_picture != 'default_avatar.png':
                                    old_file_path = os.path.join(upload_dir, user.profile_picture)
                                    if os.path.exists(old_file_path):
                                        os.remove(old_file_path)
                                
                                user.profile_picture = filename
                            else:
                                flash('⚠️ خطا در پردازش تصویر. تصویر قبلی حفظ شد.', 'warning')
                        except Exception as e:
                            print(f"خطا در آپلود تصویر: {e}")
                            flash('⚠️ خطا در آپلود تصویر. تصویر قبلی حفظ شد.', 'warning')
                else:
                    flash('⚠️ حجم فایل تصویر بسیار بزرگ است. تصویر قبلی حفظ شد.', 'warning')
        
        # اگر رمز عبور جدید وارد شده، آن را تغییر بده
        new_password = request.form.get('password')
        if new_password:
            user.password_hash = hash_password(new_password)
        
        db.session.commit()
        flash(f'✅ کاربر {user.full_name} با موفقیت ویرایش شد.', 'success')
        return redirect(url_for('auth.user_management'))
    
    return render_template('auth/edit_user.html', user=user)

@auth_bp.route('/delete-user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'دسترسی غیرمجاز'})
    
    user = User.query.get_or_404(user_id)
    
    # کاربر نمی‌تواند خودش را حذف کند
    if user.id == current_user.id:
        return jsonify({'success': False, 'message': 'شما نمی‌توانید حساب خودتان را حذف کنید'})
    
    username = user.username
    full_name = user.full_name
    
    # حذف تصویر پروفایل اگر وجود دارد
    if user.profile_picture and user.profile_picture != 'default_avatar.png':
        try:
            from app import create_app
            app = create_app()
            with app.app_context():
                upload_dir = os.path.join(app.root_path, 'static', 'uploads', 'profiles')
                file_path = os.path.join(upload_dir, user.profile_picture)
                if os.path.exists(file_path):
                    os.remove(file_path)
        except Exception as e:
            print(f"خطا در حذف تصویر پروفایل: {e}")
    
    db.session.delete(user)
    db.session.commit()
    
    flash(f'✅ کاربر {full_name} با موفقیت حذف شد.', 'success')
    return jsonify({'success': True, 'message': 'کاربر با موفقیت حذف شد'})

@auth_bp.route('/toggle-user-active/<int:user_id>', methods=['POST'])
@login_required
def toggle_user_active(user_id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'دسترسی غیرمجاز'})
    
    user = User.query.get_or_404(user_id)
    
    # کاربر نمی‌تواند وضعیت خودش را تغییر دهد
    if user.id == current_user.id:
        return jsonify({'success': False, 'message': 'شما نمی‌توانید وضعیت حساب خودتان را تغییر دهید'})
    
    user.is_active = not user.is_active
    db.session.commit()
    
    status = "فعال" if user.is_active else "غیرفعال"
    flash(f'✅ کاربر {user.full_name} {status} شد.', 'success')
    return jsonify({'success': True, 'message': f'وضعیت کاربر به {status} تغییر یافت'})

@auth_bp.route('/upload-profile-picture', methods=['POST'])
@login_required
def upload_profile_picture():
    if 'profile_picture' not in request.files:
        return jsonify({'success': False, 'message': 'فایلی انتخاب نشده است'})
    
    file = request.files['profile_picture']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'فایلی انتخاب نشده است'})
    
    if file and allowed_file(file.filename):
        # بررسی حجم فایل
        file.seek(0, os.SEEK_END)
        file_length = file.tell()
        file.seek(0)
        
        if file_length > MAX_FILE_SIZE:
            return jsonify({'success': False, 'message': 'حجم فایل باید کمتر از ۲ مگابایت باشد'})
        
        # ایجاد نام فایل منحصر به فرد
        file_ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{current_user.username}_{uuid.uuid4().hex[:8]}.{file_ext}"
        
        # مسیر ذخیره‌سازی
        from app import create_app
        app = create_app()
        with app.app_context():
            upload_dir = os.path.join(app.root_path, 'static', 'uploads', 'profiles')
            temp_dir = os.path.join(app.root_path, 'static', 'uploads', 'temp')
            os.makedirs(upload_dir, exist_ok=True)
            os.makedirs(temp_dir, exist_ok=True)
            
            file_path = os.path.join(upload_dir, filename)
            
            try:
                # ذخیره فایل موقت
                temp_path = os.path.join(temp_dir, filename)
                file.save(temp_path)
                
                # تغییر سایز تصویر
                if resize_image(temp_path, file_path):
                    # حذف فایل موقت
                    os.remove(temp_path)
                    
                    # حذف تصویر قبلی اگر وجود دارد
                    if current_user.profile_picture and current_user.profile_picture != 'default_avatar.png':
                        old_file_path = os.path.join(upload_dir, current_user.profile_picture)
                        if os.path.exists(old_file_path):
                            os.remove(old_file_path)
                    
                    # آپدیت اطلاعات کاربر
                    current_user.profile_picture = filename
                    db.session.commit()
                    
                    return jsonify({
                        'success': True, 
                        'message': 'تصویر پروفایل با موفقیت آپلود شد',
                        'image_url': current_user.get_profile_picture_url()
                    })
                else:
                    return jsonify({'success': False, 'message': 'خطا در پردازش تصویر'})
                    
            except Exception as e:
                return jsonify({'success': False, 'message': f'خطا در آپلود فایل: {str(e)}'})
    
    return jsonify({'success': False, 'message': 'فرمت فایل مجاز نیست (فقط png, jpg, jpeg, gif)'})

@auth_bp.route('/remove-profile-picture', methods=['POST'])
@login_required
def remove_profile_picture():
    try:
        if current_user.profile_picture and current_user.profile_picture != 'default_avatar.png':
            # حذف فایل از سرور
            from app import create_app
            app = create_app()
            with app.app_context():
                upload_dir = os.path.join(app.root_path, 'static', 'uploads', 'profiles')
                file_path = os.path.join(upload_dir, current_user.profile_picture)
                if os.path.exists(file_path):
                    os.remove(file_path)
        
        # بازگشت به تصویر پیش‌فرض
        current_user.profile_picture = 'default_avatar.png'
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': 'تصویر پروفایل حذف شد',
            'image_url': current_user.get_profile_picture_url()
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'خطا در حذف تصویر: {str(e)}'})

@auth_bp.route('/update-profile', methods=['POST'])
@login_required
def update_profile():
    try:
        current_user.full_name = request.form.get('full_name')
        current_user.email = request.form.get('email')
        current_user.phone = request.form.get('phone')
        current_user.department = request.form.get('department')
        
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': 'پروفایل با موفقیت بروزرسانی شد'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'خطا در بروزرسانی پروفایل: {str(e)}'})