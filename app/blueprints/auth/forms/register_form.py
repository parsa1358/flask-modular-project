from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp
from app.models.user import UserRole

class UserRegistrationForm(FlaskForm):
    # اطلاعات احراز هویت
    username = StringField('نام کاربری *', validators=[
        DataRequired(message='نام کاربری الزامی است'),
        Length(min=3, max=80, message='نام کاربری باید بین ۳ تا ۸۰ کاراکتر باشد'),
        Regexp('^[A-Za-z0-9_]+$', message='نام کاربری فقط می‌تواند شامل حروف انگلیسی، اعداد و underline باشد')
    ])
    
    email = StringField('ایمیل *', validators=[
        DataRequired(message='ایمیل الزامی است'),
        Email(message='ایمیل معتبر وارد کنید'),
        Length(max=120)
    ])
    
    # اطلاعات شخصی
    first_name = StringField('نام *', validators=[
        DataRequired(message='نام الزامی است'),
        Length(max=50)
    ])
    
    last_name = StringField('نام خانوادگی *', validators=[
        DataRequired(message='نام خانوادگی الزامی است'),
        Length(max=50)
    ])
    
    national_code = StringField('کد ملی', validators=[
        Length(min=10, max=10, message='کد ملی باید ۱۰ رقمی باشد'),
        Regexp('^[0-9]+$', message='کد ملی فقط باید شامل اعداد باشد')
    ])
    
    phone = StringField('تلفن همراه', validators=[
        Length(max=15),
        Regexp('^[0-9+]+$', message='شماره تلفن معتبر وارد کنید')
    ])
    
    address = TextAreaField('آدرس', validators=[
        Length(max=500)
    ])
    
    # اطلاعات سازمانی
    position = StringField('پست سازمانی', validators=[
        Length(max=100)
    ])
    
    department = StringField('بخش', validators=[
        Length(max=100)
    ])
    
    employee_id = StringField('کد پرسنلی', validators=[
        Length(max=20)
    ])
    
    # دسترسی
    role = SelectField('سطح دسترسی', choices=[
        (UserRole.USER.value, 'کاربر عادی'),
        (UserRole.ADMIN.value, 'ادمین'),
        (UserRole.SUPER_ADMIN.value, 'ادمین اصلی')
    ], validators=[
        DataRequired(message='سطح دسترسی الزامی است')
    ])
    
    submit = SubmitField('ایجاد کاربر')