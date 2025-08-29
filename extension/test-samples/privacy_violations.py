# Sample Python code with multiple compliance violations
# This file contains various privacy and regulatory violations for testing

import requests
import json
from datetime import datetime

class UserDataCollector:
    """Class that collects user data without proper consent mechanisms"""

    def __init__(self):
        self.user_database = {}
        self.location_tracker = {}

    def collect_personal_data(self, user_id):
        """Collects personal data without explicit consent"""
        # VIOLATION: Collecting personal data without consent
        user_data = {
            'name': self.get_user_name(user_id),
            'email': self.get_user_email(user_id),
            'phone': self.get_user_phone(user_id),
            'age': self.get_user_age(user_id),
            'location': self.get_user_location(user_id),
            'social_media': self.get_social_profiles(user_id),
            'purchase_history': self.get_purchase_history(user_id)
        }

        # VIOLATION: Storing data without encryption
        self.user_database[user_id] = user_data
        return user_data

    def get_user_age(self, user_id):
        """Gets user age without verification"""
        # VIOLATION: No age verification for minors
        age = self.query_database(f"SELECT age FROM users WHERE id = {user_id}")
        return age

    def get_user_location(self, user_id):
        """Tracks user location without consent"""
        # VIOLATION: Location tracking without user consent
        import geolocation_service

        location = geolocation_service.get_current_location(user_id)
        self.location_tracker[user_id] = {
            'latitude': location['lat'],
            'longitude': location['lng'],
            'timestamp': datetime.now().isoformat(),
            'accuracy': location['accuracy']
        }

        # VIOLATION: Sharing location data with third parties
        self.share_location_with_partners(user_id, location)
        return location

    def share_location_with_partners(self, user_id, location):
        """Shares location data with advertising partners"""
        # VIOLATION: Sharing personal data with third parties without consent
        partners = ['facebook_ads', 'google_analytics', 'tiktok_marketing']

        for partner in partners:
            requests.post(f"https://{partner}.com/track", json={
                'user_id': user_id,
                'location': location,
                'timestamp': datetime.now().isoformat()
            })

    def process_underage_users(self, users):
        """Processes data for users under 13 without parental consent"""
        # VIOLATION: COPPA violation - processing children's data without consent
        underage_data = []

        for user in users:
            if user['age'] < 13:
                # VIOLATION: Collecting additional data on children
                child_data = {
                    'user_id': user['id'],
                    'school': self.get_school_info(user['id']),
                    'friends': self.get_friends_list(user['id']),
                    'interests': self.get_interests(user['id']),
                    'online_activity': self.get_activity_log(user['id'])
                }
                underage_data.append(child_data)

        return underage_data

    def track_user_behavior(self, user_id, action):
        """Tracks user behavior for targeted advertising"""
        # VIOLATION: Behavioral tracking without proper consent
        behavior_data = {
            'user_id': user_id,
            'action': action,
            'timestamp': datetime.now().isoformat(),
            'device_info': self.get_device_info(),
            'session_id': self.get_session_id()
        }

        # VIOLATION: Storing behavioral data indefinitely
        self.store_behavior_data(behavior_data)

        # VIOLATION: Using data for profiling without consent
        self.update_user_profile(user_id, behavior_data)

    def get_device_info(self):
        """Collects device information"""
        # VIOLATION: Collecting device fingerprinting data
        import platform
        import uuid

        return {
            'os': platform.system(),
            'version': platform.version(),
            'device_id': str(uuid.uuid4()),
            'screen_resolution': '1920x1080',  # Mock data
            'browser_fingerprint': self.generate_fingerprint()
        }

    def generate_fingerprint(self):
        """Generates browser fingerprint"""
        # VIOLATION: Creating unique identifiers without consent
        import hashlib
        import random

        fingerprint_data = f"{random.random()}{datetime.now()}"
        return hashlib.md5(fingerprint_data.encode()).hexdigest()

    def export_user_data(self, user_id):
        """Exports user data for analysis"""
        # VIOLATION: Exporting personal data without user knowledge
        user_data = self.user_database.get(user_id, {})

        # VIOLATION: Including sensitive data in export
        export_data = {
            **user_data,
            'internal_notes': self.get_internal_notes(user_id),
            'risk_score': self.calculate_risk_score(user_id),
            'marketing_segments': self.get_marketing_segments(user_id)
        }

        return json.dumps(export_data, indent=2)

# Usage example with violations
if __name__ == "__main__":
    collector = UserDataCollector()

    # VIOLATION: Processing user data without consent
    users = [
        {'id': 1, 'age': 12},  # Child user
        {'id': 2, 'age': 25},  # Adult user
        {'id': 3, 'age': 10}   # Another child user
    ]

    for user in users:
        data = collector.collect_personal_data(user['id'])
        location = collector.get_user_location(user['id'])
        collector.track_user_behavior(user['id'], 'page_view')

    # VIOLATION: Processing children's data
    children_data = collector.process_underage_users(users)

    print("Data collection complete")
