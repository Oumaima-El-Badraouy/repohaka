import google.generativeai as genai
from app.models.chat import Chat
from app.models.message import Message
from app.models.tutor import Tutor
# Redis removed; rate limiting will be handled in-process or via external service if added
from flask import current_app
import json
import time
from typing import List, Dict

class AIController:
    """Controller for AI interactions."""
    
    def __init__(self):
        self.model = None
        self._initialize_gemini()
    
    def _initialize_gemini(self):
        """Initialize Gemini AI model."""
        try:
            api_key = current_app.config.get('GEMINI_API_KEY')
            if not api_key:
                raise ValueError("Gemini API key not configured")
            
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')
        except Exception as e:
            current_app.logger.error(f"Failed to initialize Gemini: {str(e)}")
            self.model = None
    
    def _get_conversation_context(self, chat_id: str, limit: int = 10) -> List[Dict]:
        """Get recent conversation context."""
        try:
            messages = Message.find_by_chat(chat_id, limit=limit)
            context = []
            
            for msg in messages[-limit:]:  # Get last N messages
                role = "user" if msg['sender'] == 'user' else "model"
                context.append({
                    "role": role,
                    "parts": [msg['text']]
                })
            
            return context
        except:
            return []
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count (rough approximation)."""
        # Rough estimation: 1 token ≈ 4 characters
        return len(text) // 4
    
    def _check_rate_limit(self, user_id: str) -> bool:
        """Check if user has exceeded rate limits."""
        # Redis removed: default to allowing requests here.
        # TODO: Replace with a proper in-memory or persistent rate limiter if needed.
        return True
    
    def _increment_rate_limit(self, user_id: str):
        """Increment rate limit counters."""
        # No-op: Redis removed. Implement counters if needed.
        return
    
    def chat_with_ai(self, user_id: str, chat_id: str, message: str) -> dict:
        """Process AI chat interaction."""
        try:
            # Validate inputs
            if not message.strip():
                return {
                    'success': False,
                    'message': 'Message cannot be empty'
                }
            
            # Check rate limits
            if not self._check_rate_limit(user_id):
                return {
                    'success': False,
                    'message': 'Rate limit exceeded. Please try again later.'
                }
            
            # Check if AI model is available
            if not self.model:
                return {
                    'success': False,
                    'message': 'AI service temporarily unavailable'
                }
            
            # Verify chat ownership
            chat_data = Chat.find_by_id(chat_id)
            if not chat_data or str(chat_data['user_id']) != user_id:
                return {
                    'success': False,
                    'message': 'Chat not found or access denied'
                }
            
            # Save user message
            user_message = Message(
                chat_id=chat_id,
                sender='user',
                text=message.strip()
            )
            user_message.save()
            
            # Get conversation context
            context = self._get_conversation_context(chat_id)
            
            # Prepare prompt with educational context
            system_prompt = (
                "You are an AI tutor helping students learn. Be helpful, clear, and educational. "
                "Provide explanations, break down complex topics, and encourage learning. "
                "If asked about topics you're not certain about, suggest consulting with human tutors."
            )
            
            # Generate AI response
            start_time = time.time()
            
            try:
                # Start a chat with context if available
                if context:
                    chat_session = self.model.start_chat(history=context)
                    response = chat_session.send_message(f"{system_prompt}\n\nStudent: {message}")
                else:
                    response = self.model.generate_content(f"{system_prompt}\n\nStudent: {message}")
                
                ai_response = response.text
                response_time = time.time() - start_time
                
            except Exception as e:
                current_app.logger.error(f"Gemini API error: {str(e)}")
                return {
                    'success': False,
                    'message': 'Failed to generate AI response. Please try again.'
                }
            
            # Estimate tokens used
            tokens_used = self._estimate_tokens(message + ai_response)
            
            # Save AI response
            ai_message = Message(
                chat_id=chat_id,
                sender='ai',
                text=ai_response,
                tokens_used=tokens_used,
                metadata={
                    'model': 'gemini-pro',
                    'response_time': response_time,
                    'tokens_estimated': tokens_used
                }
            )
            ai_message_id = ai_message.save()
            
            # Update chat activity
            Chat.update_activity(chat_id, tokens_used)
            
            # Increment rate limits
            self._increment_rate_limit(user_id)
            
            # Check if we should suggest human tutors
            tutor_suggestions = self._should_suggest_tutors(message, ai_response)
            
            return {
                'success': True,
                'message': ai_response,
                'message_id': ai_message_id,
                'tokens_used': tokens_used,
                'response_time': response_time,
                'tutor_suggestions': tutor_suggestions
            }
            
        except Exception as e:
            current_app.logger.error(f"AI chat error: {str(e)}")
            return {
                'success': False,
                'message': 'An error occurred while processing your request'
            }
    
    def _should_suggest_tutors(self, user_message: str, ai_response: str) -> List[dict]:
        """Determine if human tutors should be suggested."""
        try:
            # Keywords that might indicate need for human help
            complex_keywords = [
                'difficult', 'confused', 'don\'t understand', 'need help',
                'struggling', 'complex', 'advanced', 'detailed explanation'
            ]
            
            # Check if user message contains complexity indicators
            message_lower = user_message.lower()
            needs_human_help = any(keyword in message_lower for keyword in complex_keywords)
            
            # Also check if AI response is very long (might indicate complex topic)
            response_is_long = len(ai_response.split()) > 200
            
            if needs_human_help or response_is_long:
                # Extract potential subjects from the message
                subjects = self._extract_subjects(user_message)
                
                if subjects:
                    # Get tutor recommendations
                    tutors = Tutor.get_recommendations(subjects, limit=3)
                    
                    return [{
                        'id': str(tutor['_id']),
                        'name': tutor['name'],
                        'subjects': tutor['subjects'],
                        'hourly_rate': tutor['hourly_rate'],
                        'gpa': tutor['gpa'],
                        'school': tutor['school']
                    } for tutor in tutors]
            
            return []
        except:
            return []
    
    def _extract_subjects(self, message: str) -> List[str]:
        """Extract potential subjects from user message."""
        # Common academic subjects
        subjects_keywords = {
            'math': ['math', 'mathematics', 'algebra', 'calculus', 'geometry', 'statistics'],
            'physics': ['physics', 'mechanics', 'thermodynamics', 'quantum'],
            'chemistry': ['chemistry', 'organic', 'inorganic', 'biochemistry'],
            'biology': ['biology', 'anatomy', 'genetics', 'molecular'],
            'computer science': ['programming', 'coding', 'algorithm', 'computer science', 'software'],
            'english': ['english', 'literature', 'writing', 'essay', 'grammar'],
            'history': ['history', 'historical', 'ancient', 'modern history'],
            'economics': ['economics', 'microeconomics', 'macroeconomics', 'finance']
        }
        
        message_lower = message.lower()
        detected_subjects = []
        
        for subject, keywords in subjects_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                detected_subjects.append(subject)
        
        return detected_subjects
    
    def create_chat(self, user_id: str, title: str = None) -> dict:
        """Create a new AI chat session."""
        try:
            if not title:
                title = "New Chat"
            
            chat = Chat(
                user_id=user_id,
                title=title.strip(),
                is_ai_session=True,
                ai_model='gemini-pro'
            )
            
            chat_id = chat.save()
            
            return {
                'success': True,
                'chat_id': chat_id,
                'title': title
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to create chat: {str(e)}'
            }
    
    def get_user_chats(self, user_id: str) -> dict:
        """Get user's chat history."""
        try:
            chats = Chat.find_by_user(user_id)
            
            chat_list = []
            for chat in chats:
                chat_list.append({
                    'id': str(chat['_id']),
                    'title': chat['title'],
                    'last_activity': chat['last_activity'],
                    'message_count': chat['message_count'],
                    'total_tokens': chat['total_tokens']
                })
            
            return {
                'success': True,
                'chats': chat_list
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to get chats: {str(e)}'
            }