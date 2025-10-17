# Database Seeder

This folder contains a small seeder script to populate the `learning_platform` MongoDB with an admin user and sample student registrations.

Files
- `seed_db.py` - Python script that reads `mock_data.json` and inserts users into MongoDB.
- `mock_data.json` - Example admin and students (some verified, some pending).

Usage
1. Ensure MongoDB is running and reachable. By default the script uses the `MONGO_URI` from `app/config.py` (`mongodb://localhost:27017/learning_platform`).

2. (Optional) Set the environment variable `FLASK_CONFIG` to select another config (e.g., `production` or `testing`).

3. Run the seeder from the `backend` folder:

```powershell
cd c:\Users\hp\Downloads\package (8)\backend
python seed_db.py
```

4. After seeding, you can log in as the admin using the email `admin@school.edu` and the password from `mock_data.json` (`AdminPass123!` by default). Use the app's login endpoint (frontend or backend auth route) to obtain a token and access admin features.

Accepting student registrations

Once logged in as admin, use the admin dashboard or call the backend admin endpoints to list and verify pending students. The admin controller provides `get_pending_students()` and `verify_student(student_id)` which the app's views/controllers call to support the dashboard.
