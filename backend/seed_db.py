import os
import json
from getpass import getpass
from datetime import datetime

from app.config import config
from werkzeug.security import generate_password_hash


def load_config():
    env = os.environ.get('FLASK_CONFIG', 'development')
    return config.get(env)()


def connect_app(cfg):
    """Initialize PyMongo with MONGO_URI from config."""
    # Flask app context is not required for PyMongo in this simple script
    os.environ.setdefault('MONGO_URI', cfg.MONGO_URI)
    # Create a minimal object with db attribute expected by extensions
    from pymongo import MongoClient
    client = MongoClient(cfg.MONGO_URI)
    return client


def seed_database(client, data):
    db = client.get_default_database()
    users_coll = db.get_collection('users')

    # Upsert admin
    admin = data.get('admin')
    if admin:
        email = admin['email'].lower().strip()
        existing = users_coll.find_one({'email': email})
        if existing:
            print(f"Admin already exists: {email} (skipping)")
            admin_id = str(existing['_id'])
        else:
            # Build admin document and hash password
            admin_doc = {
                'email': email,
                'password_hash': generate_password_hash(admin['password']),
                'name': admin.get('name', 'Admin').strip(),
                'role': 'admin',
                'school': admin.get('school', '').strip(),
                'student_id': admin.get('student_id', '').strip(),
                'is_verified': True,
                'created_at': datetime.utcnow(),
                'last_login': None
            }
            res = users_coll.insert_one(admin_doc)
            admin_id = str(res.inserted_id)
            print(f"Inserted admin: {email} -> id: {admin_id}")

    # Insert students
    students = data.get('students', [])
    for s in students:
        email = s['email'].lower().strip()
        if users_coll.find_one({'email': email}):
            print(f"Student already exists: {email} (skipping)")
            continue

        student_doc = {
            'email': email,
            'password_hash': generate_password_hash(s.get('password', 'password123')),
            'name': s.get('name', '').strip(),
            'role': 'student',
            'school': s.get('school', '').strip(),
            'student_id': s.get('student_id', '').strip(),
            'is_verified': bool(s.get('is_verified', False)),
            'created_at': datetime.utcnow(),
            'last_login': None
        }

        res = users_coll.insert_one(student_doc)
        sid = str(res.inserted_id)
        print(f"Inserted student: {email} -> id: {sid} (verified={student_doc['is_verified']})")


def main():
    print("Seeding database for learning_platform...")

    cfg = load_config()
    client = connect_app(cfg)

    # Load mock data file next to the script
    script_dir = os.path.dirname(__file__)
    data_file = os.path.join(script_dir, 'mock_data.json')

    if not os.path.exists(data_file):
        print(f"mock_data.json not found at {data_file}")
        return

    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    seed_database(client, data)


if __name__ == '__main__':
    main()
