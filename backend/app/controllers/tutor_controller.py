from app.models.tutor import Tutor
from typing import List, Dict

class TutorController:
    """Controller for tutor operations."""
    
    @staticmethod
    def get_all_tutors(active_only: bool = True) -> dict:
        """Get all tutors with optional filtering."""
        try:
            tutors = Tutor.find_all(active_only=active_only)
            
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
                    'contact_info': tutor['contact_info'],
                    'is_active': tutor['is_active']
                })
            
            return {
                'success': True,
                'tutors': tutor_list
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to get tutors: {str(e)}'
            }
    
    @staticmethod
    def get_tutor_by_id(tutor_id: str) -> dict:
        """Get specific tutor details."""
        try:
            tutor = Tutor.find_by_id(tutor_id)
            
            if not tutor:
                return {
                    'success': False,
                    'message': 'Tutor not found'
                }
            
            tutor_data = {
                'id': str(tutor['_id']),
                'name': tutor['name'],
                'subjects': tutor['subjects'],
                'hourly_rate': tutor['hourly_rate'],
                'school': tutor['school'],
                'gpa': tutor['gpa'],
                'rating_average': tutor['rating_average'],
                'total_sessions': tutor['total_sessions'],
                'contact_info': tutor['contact_info'],
                'is_active': tutor['is_active'],
                'created_at': tutor['created_at']
            }
            
            return {
                'success': True,
                'tutor': tutor_data
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to get tutor: {str(e)}'
            }
    
    @staticmethod
    def search_tutors(school: str = None, min_gpa: float = None, 
                     subjects: List[str] = None, max_rate: float = None) -> dict:
        """Search tutors with filters."""
        try:
            tutors = Tutor.search_tutors(school=school, min_gpa=min_gpa, subjects=subjects)
            
            # Apply additional filters
            if max_rate is not None:
                tutors = [t for t in tutors if t['hourly_rate'] <= max_rate]
            
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
                'filters_applied': {
                    'school': school,
                    'min_gpa': min_gpa,
                    'subjects': subjects,
                    'max_rate': max_rate
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Search failed: {str(e)}'
            }
    
    @staticmethod
    def get_tutors_by_subjects(subjects: List[str], limit: int = 10) -> dict:
        """Get tutors by specific subjects."""
        try:
            if not subjects:
                return {
                    'success': False,
                    'message': 'At least one subject is required'
                }
            
            tutors = Tutor.find_by_subjects(subjects, limit)
            
            tutor_list = []
            for tutor in tutors:
                # Calculate subject match percentage
                matching_subjects = set(tutor['subjects']).intersection(set(subjects))
                match_percentage = len(matching_subjects) / len(subjects) * 100
                
                tutor_list.append({
                    'id': str(tutor['_id']),
                    'name': tutor['name'],
                    'subjects': tutor['subjects'],
                    'matching_subjects': list(matching_subjects),
                    'match_percentage': round(match_percentage, 1),
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
                'requested_subjects': subjects
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to get tutors by subjects: {str(e)}'
            }
    
    @staticmethod
    def get_top_tutors(limit: int = 10, sort_by: str = 'gpa') -> dict:
        """Get top tutors sorted by different criteria."""
        try:
            valid_sort_options = ['gpa', 'rating', 'sessions']
            if sort_by not in valid_sort_options:
                sort_by = 'gpa'
            
            tutors = Tutor.find_all(active_only=True)
            
            # Sort tutors
            if sort_by == 'gpa':
                tutors.sort(key=lambda x: x['gpa'], reverse=True)
            elif sort_by == 'rating':
                tutors.sort(key=lambda x: x['rating_average'], reverse=True)
            elif sort_by == 'sessions':
                tutors.sort(key=lambda x: x['total_sessions'], reverse=True)
            
            # Limit results
            tutors = tutors[:limit]
            
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
                'sorted_by': sort_by,
                'total_results': len(tutor_list)
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to get top tutors: {str(e)}'
            }
    
    @staticmethod
    def get_available_subjects() -> dict:
        """Get all unique subjects offered by tutors."""
        try:
            from app.extensions import mongo
            
            # Use aggregation to get unique subjects
            pipeline = [
                {'$match': {'is_active': True}},
                {'$unwind': '$subjects'},
                {'$group': {'_id': '$subjects', 'tutor_count': {'$sum': 1}}},
                {'$sort': {'tutor_count': -1}}
            ]
            
            results = list(mongo.db.tutors.aggregate(pipeline))
            
            subjects = []
            for result in results:
                subjects.append({
                    'subject': result['_id'],
                    'tutor_count': result['tutor_count']
                })
            
            return {
                'success': True,
                'subjects': subjects
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to get subjects: {str(e)}'
            }