from datetime import datetime
from typing import Optional, List
from bson import ObjectId
from app.extensions import mongo

class Rating:
    """Rating model for AI responses."""
    
    def __init__(self, chat_id: str, message_id: str, user_id: str, 
                 rating: int, feedback: str = None):
        self.chat_id = ObjectId(chat_id)
        self.message_id = ObjectId(message_id)
        self.user_id = ObjectId(user_id)
        self.rating = rating  # 1-5 stars
        self.feedback = feedback.strip() if feedback else None
        self.created_at = datetime.utcnow()
    
    def save(self):
        """Save rating to database."""
        rating_data = {
            'chat_id': self.chat_id,
            'message_id': self.message_id,
            'user_id': self.user_id,
            'rating': self.rating,
            'feedback': self.feedback,
            'created_at': self.created_at
        }
        result = mongo.db.ratings.insert_one(rating_data)
        return str(result.inserted_id)
    
    @staticmethod
    def find_by_message(message_id: str) -> Optional[dict]:
        """Find rating by message ID."""
        try:
            return mongo.db.ratings.find_one({'message_id': ObjectId(message_id)})
        except:
            return None
    
    @staticmethod
    def find_by_user(user_id: str, limit: int = 50) -> List[dict]:
        """Find ratings by user ID."""
        try:
            return list(
                mongo.db.ratings.find({'user_id': ObjectId(user_id)})
                .sort('created_at', -1)
                .limit(limit)
            )
        except:
            return []
    
    @staticmethod
    def upsert_rating(chat_id: str, message_id: str, user_id: str, 
                     rating: int, feedback: str = None) -> str:
        """Create or update a rating."""
        try:
            rating_data = {
                'chat_id': ObjectId(chat_id),
                'message_id': ObjectId(message_id),
                'user_id': ObjectId(user_id),
                'rating': rating,
                'feedback': feedback.strip() if feedback else None,
                'created_at': datetime.utcnow()
            }
            
            result = mongo.db.ratings.update_one(
                {
                    'message_id': ObjectId(message_id),
                    'user_id': ObjectId(user_id)
                },
                {'$set': rating_data},
                upsert=True
            )
            
            if result.upserted_id:
                return str(result.upserted_id)
            else:
                # Find the existing rating
                existing = mongo.db.ratings.find_one({
                    'message_id': ObjectId(message_id),
                    'user_id': ObjectId(user_id)
                })
                return str(existing['_id']) if existing else None
        except:
            return None
    
    @staticmethod
    def get_average_rating() -> float:
        """Get overall average rating for AI responses."""
        try:
            pipeline = [
                {
                    '$group': {
                        '_id': None,
                        'avg_rating': {'$avg': '$rating'}
                    }
                }
            ]
            
            result = list(mongo.db.ratings.aggregate(pipeline))
            
            if result:
                return round(result[0]['avg_rating'], 2)
            
            return 0.0
        except:
            return 0.0
    
    @staticmethod
    def get_rating_distribution() -> dict:
        """Get distribution of ratings (1-5 stars)."""
        try:
            pipeline = [
                {
                    '$group': {
                        '_id': '$rating',
                        'count': {'$sum': 1}
                    }
                },
                {'$sort': {'_id': 1}}
            ]
            
            result = list(mongo.db.ratings.aggregate(pipeline))
            
            # Initialize with all ratings
            distribution = {i: 0 for i in range(1, 6)}
            
            for item in result:
                distribution[item['_id']] = item['count']
            
            return distribution
        except:
            return {i: 0 for i in range(1, 6)}
    
    @staticmethod
    def get_user_rating_stats(user_id: str) -> dict:
        """Get rating statistics for a specific user."""
        try:
            pipeline = [
                {'$match': {'user_id': ObjectId(user_id)}},
                {
                    '$group': {
                        '_id': None,
                        'avg_rating': {'$avg': '$rating'},
                        'total_ratings': {'$sum': 1},
                        'rating_distribution': {
                            '$push': '$rating'
                        }
                    }
                }
            ]
            
            result = list(mongo.db.ratings.aggregate(pipeline))
            
            if result:
                stats = result[0]
                rating_dist = {i: 0 for i in range(1, 6)}
                
                for rating in stats['rating_distribution']:
                    rating_dist[rating] += 1
                
                return {
                    'avg_rating': round(stats['avg_rating'], 2),
                    'total_ratings': stats['total_ratings'],
                    'rating_distribution': rating_dist
                }
            
            return {
                'avg_rating': 0.0,
                'total_ratings': 0,
                'rating_distribution': {i: 0 for i in range(1, 6)}
            }
        except:
            return {
                'avg_rating': 0.0,
                'total_ratings': 0,
                'rating_distribution': {i: 0 for i in range(1, 6)}
            }
    
    @staticmethod
    def get_recent_feedback(limit: int = 20) -> List[dict]:
        """Get recent feedback with ratings."""
        try:
            return list(
                mongo.db.ratings.find(
                    {'feedback': {'$ne': None, '$exists': True}}
                )
                .sort('created_at', -1)
                .limit(limit)
            )
        except:
            return []
    
    @staticmethod
    def delete_rating(rating_id: str, user_id: str) -> bool:
        """Delete a rating (only by the user who created it)."""
        try:
            result = mongo.db.ratings.delete_one({
                '_id': ObjectId(rating_id),
                'user_id': ObjectId(user_id)
            })
            return result.deleted_count > 0
        except:
            return False