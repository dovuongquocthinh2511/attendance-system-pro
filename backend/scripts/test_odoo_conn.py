import sys
import os

# Add backend to path (assumes this script is in backend/scripts/)
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
sys.path.append(backend_dir)

from app.services.odoo_client import odoo_client

def test_connection():
    print(f"--- Testing Odoo Connection to {odoo_client.url} ---")
    try:
        odoo_client.connect()
        print("✅ KẾT NỐI THÀNH CÔNG!")
        print(f"✅ Authenticated UID: {odoo_client.uid}")
        
        # Try fetching user info to verify read access
        print("--- Fetching Current User Info ---")
        user_info = odoo_client.search_read('res.users', [['id', '=', odoo_client.uid]], ['name', 'login'])
        print(f"✅ User Data: {user_info}")
        
    except Exception as e:
        print(f"❌ KẾT NỐI THẤT BẠI: {e}")

if __name__ == "__main__":
    test_connection()
