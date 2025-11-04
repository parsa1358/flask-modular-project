#!/usr/bin/env python3
"""
Check User Model Structure
"""

import os
import sys

def check_user_model():
    print("🔍 Checking User model...")
    
    try:
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from app.models import User
        
        # Check User class attributes
        print("📋 User model attributes:")
        for attr in dir(User):
            if not attr.startswith('_'):
                print(f"   - {attr}")
        
        # Check if is_admin exists
        if hasattr(User, 'is_admin'):
            print("✅ is_admin property exists")
        else:
            print("❌ is_admin property NOT found")
            
        # Check table columns
        from app import create_app, db
        app = create_app()
        
        with app.app_context():
            inspector = db.inspect(db.engine)
            if 'user' in inspector.get_table_names():
                user_columns = [col['name'] for col in inspector.get_columns('user')]
                print(f"📊 User table columns: {user_columns}")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_user_model()