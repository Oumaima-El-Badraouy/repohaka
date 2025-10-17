from datetime import datetime
from typing import Optional, List
from bson import ObjectId
from app.extensions import mongo

class Message:
    """Message model for chat messages."""
    
    def __init__(self, chat_id: str, sender: str, text: str, 
                 tokens_used: int = 0, metadata: dict = None):
        self.chat_id = ObjectId(chat_id)
        self.sender = sender  # 'user', 'ai', 'tutor'
        self.text = text
        self.tokens_used = tokens_used
        self.metadata = metadata or {}  # Store additional data like AI model, response time, etc.
        self.created_at = datetime.utcnow()
        self.is_edited = False
        self.edited_at = None
    
    def save(self):
        """Save message to database."""
        message_data = {
            'chat_id': self.chat_id,
            'sender': self.sender,
            'text': self.text,
            'tokens_used': self.tokens_used,
            'metadata': self.metadata,
            'created_at': self.created_at,
            'is_edited': self.is_edited,
            'edited_at': self.edited_at
        }
        result = mongo.db.messages.insert_one(message_data)
        return str(result.inserted_id)
    
    @staticmethod
    def find_by_id(message_id: str) -> Optional[dict]:
        """Find message by ID."""
        try:
            return mongo.db.messages.find_one({'_id': ObjectId(message_id)})
        except:
            return None
    
    @staticmethod
    def find_by_chat(chat_id: str, limit: int = 100, skip: int = 0) -> List[dict]:
        """Find messages by chat ID with pagination."""
        try:
            return list(
                mongo.db.messages.find({'chat_id': ObjectId(chat_id)})
                .sort('created_at', 1)  # Ascending order for chat history
                .skip(skip)
                .limit(limit)
            )
        except:
            return []
    
    @staticmethod
    def get_latest_messages(chat_id: str, count: int = 10) -> List[dict]:
        """Get latest messages from a chat."""
        try:
            return list(
                mongo.db.messages.find({'chat_id': ObjectId(chat_id)})
                .sort('created_at', -1)
                .limit(count)
            )
        except:
            return []
    
    @staticmethod
    def count_by_chat(chat_id: str) -> int:
        """Count messages in a chat."""
        try:
            return mongo.db.messages.count_documents({'chat_id': ObjectId(chat_id)})
        except:
            return 0
    
    @staticmethod
    def update_message(message_id: str, new_text: str) -> bool:
        """Update message text."""
        try:
            result = mongo.db.messages.update_one(
                {'_id': ObjectId(message_id)},
                {
                    '$set': {
                        'text': new_text,
                        'is_edited': True,
                        'edited_at': datetime.utcnow()
                    }
                }
            )
            return result.modified_count > 0
        except:
            return False
    
    @staticmethod
    def delete_message(message_id: str) -> bool:
        """Delete a message."""
        try:
            result = mongo.db.messages.delete_one({'_id': ObjectId(message_id)})
            return result.deleted_count > 0
        except:
            return False
    
    @staticmethod
    def get_ai_messages_for_rating(chat_id: str) -> List[dict]:
        """Get AI messages that can be rated."""
        try:
            return list(
                mongo.db.messages.find({
                    'chat_id': ObjectId(chat_id),
                    'sender': 'ai'
                }).sort('created_at', -1)
            )
        except:
            return []
    
    @staticmethod
    def search_messages(user_id: str, query: str, limit: int = 50) -> List[dict]:
        """Search messages by text content."""
        try:
            # First get user's chats
            user_chats = mongo.db.chats.find(
                {'user_id': ObjectId(user_id)},
                {'_id': 1}
            )
            chat_ids = [chat['_id'] for chat in user_chats]
            
            # Search messages in user's chats
            return list(
                mongo.db.messages.find({
                    'chat_id': {'$in': chat_ids},
                    'text': {'$regex': query, '$options': 'i'}
                })
                .sort('created_at', -1)
                .limit(limit)
            )
        except:
            return []
    
    @staticmethod
    def get_token_usage_stats(user_id: str = None, date_from: datetime = None) -> dict:
        """Get token usage statistics."""
        try:
            match_filter = {'sender': 'ai'}
            
            if user_id:
                # Get user's chats first
                user_chats = mongo.db.chats.find(
                    {'user_id': ObjectId(user_id)},
                    {'_id': 1}
                )
                chat_ids = [chat['_id'] for chat in user_chats]
                match_filter['chat_id'] = {'$in': chat_ids}
            
            if date_from:
                match_filter['created_at'] = {'$gte': date_from}
            
            pipeline = [
                {'$match': match_filter},
                {
                    '$group': {
                        '_id': None,
                        'total_tokens': {'$sum': '$tokens_used'},
                        'total_messages': {'$sum': 1},
                        'avg_tokens_per_message': {'$avg': '$tokens_used'}
                    }
                }
            ]
            
            result = list(mongo.db.messages.aggregate(pipeline))
            
            if result:
                stats = result[0]
                stats.pop('_id')
                stats['avg_tokens_per_message'] = round(stats.get('avg_tokens_per_message', 0), 2)
                return stats
            
            return {
                'total_tokens': 0,
                'total_messages': 0,
                'avg_tokens_per_message': 0
            }
        except:
            return {
                'total_tokens': 0,
                'total_messages': 0,
                'avg_tokens_per_message': 0
            }