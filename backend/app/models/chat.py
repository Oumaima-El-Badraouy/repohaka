from datetime import datetime
from typing import Optional, List
from bson import ObjectId
from app.extensions import mongo

class Chat:
    """Chat model for storing conversation sessions."""
    
    def __init__(self, user_id: str, title: str = "New Chat", 
                 is_ai_session: bool = True, ai_model: str = "gemini-pro"):
        self.user_id = ObjectId(user_id)
        self.title = title.strip()
        self.is_ai_session = is_ai_session
        self.ai_model = ai_model if is_ai_session else None
        self.created_at = datetime.utcnow()
        self.last_activity = datetime.utcnow()
        self.message_count = 0
        self.total_tokens = 0
    
    def save(self):
        """Save chat to database."""
        chat_data = {
            'user_id': self.user_id,
            'title': self.title,
            'is_ai_session': self.is_ai_session,
            'ai_model': self.ai_model,
            'created_at': self.created_at,
            'last_activity': self.last_activity,
            'message_count': self.message_count,
            'total_tokens': self.total_tokens
        }
        result = mongo.db.chats.insert_one(chat_data)
        return str(result.inserted_id)
    
    @staticmethod
    def find_by_id(chat_id: str) -> Optional[dict]:
        """Find chat by ID."""
        try:
            return mongo.db.chats.find_one({'_id': ObjectId(chat_id)})
        except:
            return None
    
    @staticmethod
    def find_by_user(user_id: str, limit: int = 50) -> List[dict]:
        """Find chats by user ID."""
        try:
            return list(
                mongo.db.chats.find({'user_id': ObjectId(user_id)})
                .sort('last_activity', -1)
                .limit(limit)
            )
        except:
            return []
    
    @staticmethod
    def update_activity(chat_id: str, token_count: int = 0):
        """Update chat activity and stats."""
        try:
            updates = {
                '$set': {'last_activity': datetime.utcnow()},
                '$inc': {'message_count': 1}
            }
            
            if token_count > 0:
                updates['$inc']['total_tokens'] = token_count
            
            mongo.db.chats.update_one(
                {'_id': ObjectId(chat_id)},
                updates
            )
            return True
        except:
            return False
    
    @staticmethod
    def update_title(chat_id: str, title: str):
        """Update chat title."""
        try:
            mongo.db.chats.update_one(
                {'_id': ObjectId(chat_id)},
                {'$set': {'title': title.strip()}}
            )
            return True
        except:
            return False
    
    @staticmethod
    def delete_chat(chat_id: str, user_id: str) -> bool:
        """Delete a chat and all its messages."""
        try:
            # First verify ownership
            chat = mongo.db.chats.find_one({
                '_id': ObjectId(chat_id),
                'user_id': ObjectId(user_id)
            })
            
            if not chat:
                return False
            
            # Delete messages
            mongo.db.messages.delete_many({'chat_id': ObjectId(chat_id)})
            
            # Delete ratings
            mongo.db.ratings.delete_many({'chat_id': ObjectId(chat_id)})
            
            # Delete chat
            result = mongo.db.chats.delete_one({'_id': ObjectId(chat_id)})
            
            return result.deleted_count > 0
        except:
            return False
    
    @staticmethod
    def get_user_stats(user_id: str) -> dict:
        """Get user's chat statistics."""
        try:
            pipeline = [
                {'$match': {'user_id': ObjectId(user_id)}},
                {
                    '$group': {
                        '_id': None,
                        'total_chats': {'$sum': 1},
                        'total_messages': {'$sum': '$message_count'},
                        'total_tokens': {'$sum': '$total_tokens'},
                        'ai_sessions': {
                            '$sum': {'$cond': [{'$eq': ['$is_ai_session', True]}, 1, 0]}
                        }
                    }
                }
            ]
            
            result = list(mongo.db.chats.aggregate(pipeline))
            
            if result:
                stats = result[0]
                stats.pop('_id')
                return stats
            
            return {
                'total_chats': 0,
                'total_messages': 0,
                'total_tokens': 0,
                'ai_sessions': 0
            }
        except:
            return {
                'total_chats': 0,
                'total_messages': 0,
                'total_tokens': 0,
                'ai_sessions': 0
            }