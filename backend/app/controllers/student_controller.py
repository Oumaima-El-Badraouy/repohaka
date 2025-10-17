from app.models.chat import Chat
from app.models.message import Message
from app.models.rating import Rating
from app.models.tutor import Tutor
from typing import List, Dict

class StudentController:
    """Controller for student operations."""
    
    @staticmethod
    def get_profile(user_id: str) -> dict:
        """Get student profile with statistics."""
        try:
            from app.models.user import User
            user_data = User.find_by_id(user_id)
            
            if not user_data:
                return {
                    'success': False,
                    'message': 'User not found'
                }
            
            # Get user statistics
            chat_stats = Chat.get_user_stats(user_id)
            rating_stats = Rating.get_user_rating_stats(user_id)
            
            profile = {
                'id': str(user_data['_id']),
                'name': user_data['name'],
                'email': user_data['email'],
                'school': user_data['school'],
                'student_id': user_data['student_id'],
                'is_verified': user_data['is_verified'],
                'created_at': user_data['created_at'],
                'last_login': user_data['last_login'],
                'statistics': {
                    'chats': chat_stats,
                    'ratings': rating_stats
                }
            }
            
            return {
                'success': True,
                'profile': profile
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to get profile: {str(e)}'
            }
    
    @staticmethod
    def get_chat_history(user_id: str, chat_id: str = None, page: int = 1, per_page: int = 50) -> dict:
        """Get chat history for a student."""
        try:
            if chat_id:
                # Get specific chat
                chat_data = Chat.find_by_id(chat_id)
                
                if not chat_data or str(chat_data['user_id']) != user_id:
                    return {
                        'success': False,
                        'message': 'Chat not found or access denied'
                    }
                
                # Get messages with pagination
                skip = (page - 1) * per_page
                messages = Message.find_by_chat(chat_id, limit=per_page, skip=skip)
                total_messages = Message.count_by_chat(chat_id)
                
                message_list = []
                for msg in messages:
                    message_data = {
                        'id': str(msg['_id']),
                        'sender': msg['sender'],
                        'text': msg['text'],
                        'created_at': msg['created_at'],
                        'is_edited': msg.get('is_edited', False)
                    }
                    
                    # Include rating if it's an AI message
                    if msg['sender'] == 'ai':
                        rating = Rating.find_by_message(str(msg['_id']))
                        if rating:
                            message_data['rating'] = {
                                'rating': rating['rating'],
                                'feedback': rating.get('feedback')
                            }
                    
                    message_list.append(message_data)
                
                return {
                    'success': True,
                    'chat': {
                        'id': str(chat_data['_id']),
                        'title': chat_data['title'],
                        'created_at': chat_data['created_at'],
                        'last_activity': chat_data['last_activity'],
                        'message_count': chat_data['message_count'],
                        'total_tokens': chat_data['total_tokens']
                    },
                    'messages': message_list,
                    'pagination': {
                        'page': page,
                        'per_page': per_page,
                        'total': total_messages,
                        'pages': (total_messages + per_page - 1) // per_page
                    }
                }
            else:
                # Get all chats for user
                chats = Chat.find_by_user(user_id)
                
                chat_list = []
                for chat in chats:
                    chat_list.append({
                        'id': str(chat['_id']),
                        'title': chat['title'],
                        'created_at': chat['created_at'],
                        'last_activity': chat['last_activity'],
                        'message_count': chat['message_count'],
                        'total_tokens': chat['total_tokens'],
                        'is_ai_session': chat['is_ai_session']
                    })
                
                return {
                    'success': True,
                    'chats': chat_list
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to get chat history: {str(e)}'
            }
    
    @staticmethod
    def rate_ai_response(user_id: str, message_id: str, rating: int, feedback: str = None) -> dict:
        """Rate an AI response."""
        try:
            # Validate rating
            if not isinstance(rating, int) or rating < 1 or rating > 5:
                return {
                    'success': False,
                    'message': 'Rating must be between 1 and 5'
                }
            
            # Find the message
            message_data = Message.find_by_id(message_id)
            if not message_data:
                return {
                    'success': False,
                    'message': 'Message not found'
                }
            
            # Verify it's an AI message
            if message_data['sender'] != 'ai':
                return {
                    'success': False,
                    'message': 'Can only rate AI messages'
                }
            
            # Verify user owns the chat
            chat_data = Chat.find_by_id(str(message_data['chat_id']))
            if not chat_data or str(chat_data['user_id']) != user_id:
                return {
                    'success': False,
                    'message': 'Access denied'
                }
            
            # Create or update rating
            rating_id = Rating.upsert_rating(
                chat_id=str(message_data['chat_id']),
                message_id=message_id,
                user_id=user_id,
                rating=rating,
                feedback=feedback
            )
            
            if rating_id:
                return {
                    'success': True,
                    'message': 'Rating saved successfully',
                    'rating_id': rating_id
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to save rating'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to rate response: {str(e)}'
            }
    
    @staticmethod
    def search_messages(user_id: str, query: str, limit: int = 20) -> dict:
        """Search user's messages."""
        try:
            if not query.strip():
                return {
                    'success': False,
                    'message': 'Search query cannot be empty'
                }
            
            messages = Message.search_messages(user_id, query.strip(), limit)
            
            message_list = []
            for msg in messages:
                # Get chat info
                chat_data = Chat.find_by_id(str(msg['chat_id']))
                
                message_list.append({
                    'id': str(msg['_id']),
                    'text': msg['text'],
                    'sender': msg['sender'],
                    'created_at': msg['created_at'],
                    'chat': {
                        'id': str(msg['chat_id']),
                        'title': chat_data['title'] if chat_data else 'Unknown Chat'
                    }
                })
            
            return {
                'success': True,
                'results': message_list,
                'query': query,
                'total_results': len(message_list)
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Search failed: {str(e)}'
            }
    
    @staticmethod
    def delete_chat(user_id: str, chat_id: str) -> dict:
        """Delete a chat and all its messages."""
        try:
            success = Chat.delete_chat(chat_id, user_id)
            
            if success:
                return {
                    'success': True,
                    'message': 'Chat deleted successfully'
                }
            else:
                return {
                    'success': False,
                    'message': 'Chat not found or access denied'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to delete chat: {str(e)}'
            }
    
    @staticmethod
    def update_chat_title(user_id: str, chat_id: str, title: str) -> dict:
        """Update chat title."""
        try:
            if not title.strip():
                return {
                    'success': False,
                    'message': 'Title cannot be empty'
                }
            
            # Verify chat ownership
            chat_data = Chat.find_by_id(chat_id)
            if not chat_data or str(chat_data['user_id']) != user_id:
                return {
                    'success': False,
                    'message': 'Chat not found or access denied'
                }
            
            success = Chat.update_title(chat_id, title.strip())
            
            if success:
                return {
                    'success': True,
                    'message': 'Chat title updated successfully'
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to update chat title'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to update chat title: {str(e)}'
            }
    
    @staticmethod
    def get_recommended_tutors(user_id: str, subjects: List[str] = None, limit: int = 5) -> dict:
        """Get recommended tutors for a student."""
        try:
            if subjects:
                # Get tutors for specific subjects
                tutors = Tutor.find_by_subjects(subjects, limit)
            else:
                # Get general recommendations (top-rated tutors)
                tutors = Tutor.get_recommendations([], limit)
            
            tutor_list = []
            for tutor in tutors:
                tutor_list.append({
                    'id': str(tutor['_id']),
                    'name': tutor['name'],
                    'subjects': tutor['subjects'],
                    'hourly_rate': tutor['hourly_rate'],
                    'school': tutor['school'],
                    'gpa': tutor['gpa'],
                    'rating_average': tutor['rating_average'],
                    'total_sessions': tutor['total_sessions'],
                    'contact_info': tutor['contact_info']
                })
            
            return {
                'success': True,
                'tutors': tutor_list,
                'subjects_searched': subjects or []
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to get tutor recommendations: {str(e)}'
            }