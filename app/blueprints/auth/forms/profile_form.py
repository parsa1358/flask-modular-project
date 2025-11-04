from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FileField, SubmitField
from wtforms.validators import Length, Email

class ProfileForm(FlaskForm):
    first_name = StringField('نام', validators=[
        Length(max=50)
    ])
    
    last_name = StringField('نام خانوادگی', validators=[
        Length(max=50)
    ])
    
    email = StringField('ایمیل', validators=[
        Email(message='ایمیل معتبر وارد کنید'),
        Length(max=120)
    ])
    
    phone = StringField('تلفن همراه', validators=[
        Length(max=15)
    ])
    
    address = TextAreaField('آدرس', validators=[
        Length(max=500)
    ])
    
    position = StringField('پست سازمانی', validators=[
        Length(max=100)
    ])
    
    department = StringField('بخش', validators=[
        Length(max=100)
    ])
    
    profile_image = FileField('تصویر پروفایل')
    
    submit = SubmitField('بروزرسانی پروفایل')