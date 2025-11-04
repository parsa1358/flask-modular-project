from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length

class LoginForm(FlaskForm):
    username = StringField('نام کاربری', validators=[
        DataRequired(message='نام کاربری الزامی است'),
        Length(min=3, max=80, message='نام کاربری باید بین ۳ تا ۸۰ کاراکتر باشد')
    ])
    password = PasswordField('رمز عبور', validators=[
        DataRequired(message='رمز عبور الزامی است')
    ])
    remember_me = BooleanField('مرا به خاطر بسپار')
    submit = SubmitField('ورود به سیستم')