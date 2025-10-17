// Initialize database with collections and indexes
db = db.getSiblingDB('learning_platform');

// Create collections
db.createCollection('users');
db.createCollection('tutors');
db.createCollection('chats');
db.createCollection('messages');
db.createCollection('ratings');

// Create indexes for better performance
db.users.createIndex({ "email": 1 }, { unique: true });
db.users.createIndex({ "student_id": 1 });
db.users.createIndex({ "role": 1 });
db.users.createIndex({ "is_verified": 1 });

db.tutors.createIndex({ "subjects": 1 });
db.tutors.createIndex({ "school": 1 });
db.tutors.createIndex({ "gpa": -1 });

db.chats.createIndex({ "user_id": 1 });
db.chats.createIndex({ "created_at": -1 });
db.chats.createIndex({ "is_ai_session": 1 });

db.messages.createIndex({ "chat_id": 1 });
db.messages.createIndex({ "created_at": -1 });
db.messages.createIndex({ "sender": 1 });

db.ratings.createIndex({ "chat_id": 1 });
db.ratings.createIndex({ "user_id": 1 });
db.ratings.createIndex({ "rating": 1 });

// Create admin user
db.users.insertOne({
    email: "admin@learningplatform.com",
    password_hash: "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewBN5BHCRvhVMnRy", // password: admin123
    name: "Platform Admin",
    role: "admin",
    school: "Platform",
    student_id: "ADMIN001",
    is_verified: true,
    created_at: new Date(),
    last_login: null
});

print('Database initialized successfully!');
print('Admin user created: admin@learningplatform.com / admin123');