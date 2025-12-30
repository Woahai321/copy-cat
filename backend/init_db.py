from database import SessionLocal, engine
from models import Base, User, SystemSettings
from auth import get_password_hash

# Create all tables
Base.metadata.create_all(bind=engine)

# Create session
db = SessionLocal()

# Check if admin user exists
admin_user = db.query(User).filter(User.username == "admin").first()

# Check if scan interval setting exists
scan_interval_setting = db.query(SystemSettings).filter(SystemSettings.key == "scan_interval_seconds").first()

if not admin_user:
    # Create admin user
    hashed_pwd = get_password_hash("changeme")
    print(f"DEBUG: Hashing 'changeme' -> {hashed_pwd}")
    admin_user = User(
        username="admin",
        password_hash=hashed_pwd,
        is_admin=True
    )
    db.add(admin_user)
    db.commit()
    print("=" * 60)
    print("Database initialized successfully!")
    print("=" * 60)
    print("Admin user created:")
    print("  Username: admin")
    print("  Password: changeme")
    print("=" * 60)
    print("IMPORTANT: Please change the default password after first login!")
    print("=" * 60)
else:
    print("Database already initialized. Admin user exists.")

# Create default scan interval setting if it doesn't exist
if not scan_interval_setting:
    scan_interval_setting = SystemSettings(
        key="scan_interval_seconds",
        value="300",  # 5 minutes default
        is_encrypted=False
    )
    db.add(scan_interval_setting)
    db.commit()
    print("Default scan interval setting created: 300 seconds (5 minutes)")
else:
    print("Scan interval setting already exists.")

db.close()

