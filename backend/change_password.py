"""
Script to change the admin password.
Usage: python change_password.py
"""

from database import SessionLocal
from models import User
from auth import get_password_hash
import getpass

def change_password():
    db = SessionLocal()
    
    try:
        # Get admin user
        admin_user = db.query(User).filter(User.username == "admin").first()
        
        if not admin_user:
            print("Error: Admin user not found!")
            print("Please run init_db.py first to create the admin user.")
            return
        
        print("Change Admin Password")
        print("=" * 40)
        
        # Get current password for verification
        current_password = getpass.getpass("Enter current password: ")
        
        # Verify current password
        from auth import verify_password
        if not verify_password(current_password, admin_user.password_hash):
            print("Error: Current password is incorrect!")
            return
        
        # Get new password
        new_password = getpass.getpass("Enter new password: ")
        confirm_password = getpass.getpass("Confirm new password: ")
        
        if new_password != confirm_password:
            print("Error: Passwords do not match!")
            return
        
        if len(new_password) < 6:
            print("Error: Password must be at least 6 characters long!")
            return
        
        # Update password
        admin_user.password_hash = get_password_hash(new_password)
        db.commit()
        
        print("=" * 40)
        print("Password changed successfully!")
        print("=" * 40)
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    change_password()

