from celery import Celery
from app.extensions import celery
from app.models.chat import Chat
from app.models.message import Message
from app.utils.helpers import generate_chat_title
import google.generativeai as genai
from flask import current_app
import logging

@celery.task
def generate_summary_task(chat_id: str) -> dict:
    """Generate summary for a chat session (async task)."""
    try:
        # Get chat and messages
        chat_data = Chat.find_by_id(chat_id)
        if not chat_data:
            return {'success': False, 'message': 'Chat not found'}
        
        messages = Message.find_by_chat(chat_id, limit=20)  # Last 20 messages
        
        if not messages:
            return {'success': False, 'message': 'No messages to summarize'}
        
        # Prepare conversation text
        conversation = []
        for msg in messages:
            sender = "Student" if msg['sender'] == 'user' else "AI Tutor"
            conversation.append(f"{sender}: {msg['text']}")
        
        conversation_text = "\n".join(conversation)
        
        # Generate summary using Gemini
        try:
            genai.configure(api_key=current_app.config['GEMINI_API_KEY'])
            model = genai.GenerativeModel('gemini-pro')
            
            prompt = (
                "Please provide a concise summary of the following conversation between a student and an AI tutor. "
                "Focus on the main topics discussed and key learning points:\n\n"
                f"{conversation_text}"
            )
            
            response = model.generate_content(prompt)
            summary = response.text
            
            # Update chat title if it's still "New Chat"
            if chat_data.get('title') == 'New Chat' and messages:
                new_title = generate_chat_title(messages[0]['text'])
                Chat.update_title(chat_id, new_title)
            
            return {
                'success': True,
                'summary': summary,
                'chat_id': chat_id
            }
            
        except Exception as e:
            logging.error(f"Failed to generate summary: {str(e)}")
            return {
                'success': False,
                'message': f'Failed to generate summary: {str(e)}'
            }
            
    except Exception as e:
        logging.error(f"Summary task error: {str(e)}")
        return {
            'success': False,
            'message': f'Task failed: {str(e)}'
        }

@celery.task
def generate_quiz_task(chat_id: str, topic: str = None) -> dict:
    """Generate quiz questions based on chat content (async task)."""
    try:
        # Get chat messages
        messages = Message.find_by_chat(chat_id, limit=10)
        
        if not messages:
            return {'success': False, 'message': 'No messages found for quiz generation'}
        
        # Extract content for quiz generation
        content = []
        for msg in messages:
            if msg['sender'] == 'ai':  # Focus on AI responses for educational content
                content.append(msg['text'])
        
        if not content:
            return {'success': False, 'message': 'No educational content found'}
        
        content_text = "\n".join(content)
        
        # Generate quiz using Gemini
        try:
            genai.configure(api_key=current_app.config['GEMINI_API_KEY'])
            model = genai.GenerativeModel('gemini-pro')
            
            quiz_prompt = (
                "Based on the following educational content, create 5 multiple-choice quiz questions. "
                "Format each question with 4 options (A, B, C, D) and indicate the correct answer. "
                "Make the questions test understanding of key concepts:\n\n"
                f"{content_text}"
            )
            
            if topic:
                quiz_prompt = f"Focus on the topic of '{topic}'. " + quiz_prompt
            
            response = model.generate_content(quiz_prompt)
            quiz_content = response.text
            
            return {
                'success': True,
                'quiz': quiz_content,
                'chat_id': chat_id,
                'topic': topic
            }
            
        except Exception as e:
            logging.error(f"Failed to generate quiz: {str(e)}")
            return {
                'success': False,
                'message': f'Failed to generate quiz: {str(e)}'
            }
            
    except Exception as e:
        logging.error(f"Quiz task error: {str(e)}")
        return {
            'success': False,
            'message': f'Task failed: {str(e)}'
        }

@celery.task
def cleanup_old_chats_task() -> dict:
    """Clean up old inactive chats (runs periodically)."""
    try:
        from datetime import datetime, timedelta
        from app.extensions import mongo
        
        # Delete chats older than 90 days with no activity
        cutoff_date = datetime.utcnow() - timedelta(days=90)
        
        # Find old chats
        old_chats = list(mongo.db.chats.find({
            'last_activity': {'$lt': cutoff_date},
            'message_count': {'$lt': 5}  # Only delete chats with very few messages
        }))
        
        deleted_count = 0
        for chat in old_chats:
            chat_id = str(chat['_id'])
            user_id = str(chat['user_id'])
            
            if Chat.delete_chat(chat_id, user_id):
                deleted_count += 1
        
        return {
            'success': True,
            'deleted_chats': deleted_count,
            'message': f'Cleaned up {deleted_count} old chats'
        }
        
    except Exception as e:
        logging.error(f"Cleanup task error: {str(e)}")
        return {
            'success': False,
            'message': f'Cleanup failed: {str(e)}'
        }

@celery.task
def send_notification_task(user_id: str, message: str, notification_type: str = 'info') -> dict:
    """Send notification to user (placeholder for future notification system)."""
    try:
        # This is a placeholder for future notification implementation
        # Could integrate with email, push notifications, etc.
        
        logging.info(
            f"Notification sent - User: {user_id}, Type: {notification_type}, Message: {message}"
        )
        
        return {
            'success': True,
            'user_id': user_id,
            'message': 'Notification sent successfully'
        }
        
    except Exception as e:
        logging.error(f"Notification task error: {str(e)}")
        return {
            'success': False,
            'message': f'Failed to send notification: {str(e)}'
        }

# Periodic tasks configuration (would be set up with celery beat)
@celery.task
def daily_maintenance_task() -> dict:
    """Run daily maintenance tasks."""
    try:
        results = []
        
        # Run cleanup
        cleanup_result = cleanup_old_chats_task.delay()
        results.append(cleanup_result.get())
        
        # Add other maintenance tasks here
        # - Database cleanup
        # - Generate analytics reports
        # - Check system health
        
        return {
            'success': True,
            'maintenance_results': results,
            'message': 'Daily maintenance completed'
        }
        
    except Exception as e:
        logging.error(f"Maintenance task error: {str(e)}")
        return {
            'success': False,
            'message': f'Maintenance failed: {str(e)}'
        }