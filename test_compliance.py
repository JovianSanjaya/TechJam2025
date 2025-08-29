#!/usr/bin/env python3
"""Test compliance analyzer with ChromaDB fallback"""

def collect_user_data(user_id, age, location, email):
    """Collect user data for processing"""
    user_data = {
        'user_id': user_id,
        'age': age, 
        'location': location,
        'email': email
    }
    
    # GDPR violation - no consent for marketing
    send_to_marketing(email, location)
    
    # COPPA violation - storing child data without parental consent  
    if age < 13:
        store_child_preferences(user)
    
    return user_data

def send_to_marketing(email, location):
    """Send user data to marketing"""
    print(f"Sending {email} from {location} to marketing")

def store_child_preferences(user):
    """Store child preferences"""  
    print(f"Storing preferences for child user")
