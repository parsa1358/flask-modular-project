import hashlib
import secrets
from datetime import datetime, timedelta

def hash_password(password):
    """هش کردن رمز عبور با الگوریتم SHA-256"""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def verify_password(password, hashed):
    """بررسی تطابق رمز عبور با هش ذخیره شده"""
    return hash_password(password) == hashed

def generate_temp_password(length=8):
    """تولید رمز عبور موقت"""
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def is_password_strong(password):
    """بررسی قدرت رمز عبور"""
    if len(password) < 6:
        return False, "رمز عبور باید حداقل ۶ کاراکتر باشد"
    return True, "رمز عبور قابل قبول است"