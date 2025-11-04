from datetime import datetime
import jdatetime

def jalali_date(value, format='%Y/%m/%d'):
    """تبدیل تاریخ میلادی به شمسی"""
    if value is None:
        return ""
    
    try:
        if isinstance(value, str):
            # اگر رشته است، سعی کن به تاریخ تبدیل کن
            try:
                value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                try:
                    value = datetime.strptime(value, '%Y-%m-%d')
                except ValueError:
                    return value
        
        if isinstance(value, datetime):
            jalali_date = jdatetime.datetime.fromgregorian(datetime=value)
            return jalali_date.strftime(format)
        
        return value
    except Exception:
        return value

def jalali_datetime(value, format='%Y/%m/%d %H:%M:%S'):
    """تبدیل تاریخ و زمان میلادی به شمسی"""
    return jalali_date(value, format)

def current_jalali_date(format='%Y/%m/%d'):
    """تاریخ شمسی فعلی"""
    return jdatetime.datetime.now().strftime(format)

def current_jalali_datetime(format='%Y/%m/%d %H:%M:%S'):
    """تاریخ و زمان شمسی فعلی"""
    return jdatetime.datetime.now().strftime(format)

def register_jalali_filters(app):
    """ثبت فیلترها در Jinja2"""
    app.jinja_env.filters['jalali_date'] = jalali_date
    app.jinja_env.filters['jalali_datetime'] = jalali_datetime
    
    # اضافه کردن توابع به context
    @app.context_processor
    def utility_processor():
        return {
            'current_jalali_date': current_jalali_date,
            'current_jalali_datetime': current_jalali_datetime
        }