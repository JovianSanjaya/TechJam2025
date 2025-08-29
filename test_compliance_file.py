#!/usr/bin/env python3
"""Test file for VS Code extension analysis"""

def process_user_data(user_id, age, email, location):
    """Process user data with potential compliance issues"""
    
    # Store user information
    user_profile = {
        'id': user_id,
        'age': age,
        'email': email,
        'location': location,
        'created_at': '2024-01-01'
    }
    
    # CRITICAL ISSUE: No consent check for marketing
    send_marketing_email(email, location)
    
    # CRITICAL ISSUE: Storing child data without parental consent
    if age < 13:
        save_child_preferences(user_profile)
        track_child_behavior(user_id)
    
    # ISSUE: No encryption for sensitive data
    store_user_data(user_profile)
    
    return user_profile

def send_marketing_email(email, location):
    """Send marketing email without consent check"""
    marketing_content = generate_targeted_ads(location)
    send_email(email, marketing_content)

def save_child_preferences(profile):
    """Save child preferences without parental consent"""
    preferences = {
        'favorite_videos': profile.get('videos', []),
        'interests': profile.get('interests', []),
        'watch_time': profile.get('watch_time', 0)
    }
    database.save(preferences)

def track_child_behavior(user_id):
    """Track child behavior for recommendations"""
    analytics.track_user(user_id, {
        'behavioral_data': True,
        'recommendation_engine': True
    })

def store_user_data(data):
    """Store user data without encryption"""
    # Security vulnerability - no encryption
    with open(f"user_{data['id']}.json", 'w') as f:
        json.dump(data, f)
