# app/blueprints/influencers/forms/__init__.py
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, SelectField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, Optional, NumberRange

class InfluencerForm(FlaskForm):
    name = StringField('نام اینفلوئنسر', validators=[DataRequired()])
    instagram_id = StringField('آیدی اینستاگرام', validators=[DataRequired()])
    follower_count = IntegerField('تعداد فالوور', validators=[Optional(), NumberRange(min=0)])
    engagement_rate = FloatField('نرخ تعامل', validators=[Optional(), NumberRange(min=0, max=100)])
    category = SelectField('دسته‌بندی', choices=[
        ('', 'انتخاب کنید'),
        ('fashion', 'فشن و مد'),
        ('beauty', 'زیبایی'),
        ('lifestyle', 'سبک زندگی'),
        ('tech', 'تکنولوژی'),
        ('food', 'غذا'),
        ('travel', 'سفر'),
        ('other', 'سایر')
    ], validators=[DataRequired()])
    contact_info = TextAreaField('اطلاعات تماس')
    notes = TextAreaField('یادداشت‌ها')
    is_active = BooleanField('فعال')