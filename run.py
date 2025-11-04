from app import create_app

app = create_app()

if __name__ == '__main__':
    print("🚀 اجرای برنامه اصلی Flask...")
    print("📁 پروژه: سیستم مدیریت ماژولار")
    print("🌐 آدرس: http://localhost:5000")
    print("🔧 حالت: توسعه (Debug)")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
