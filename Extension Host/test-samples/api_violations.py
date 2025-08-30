# Sample API server with compliance violations
# This demonstrates backend privacy violations

from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import json
from datetime import datetime
import hashlib
import uuid

app = Flask(__name__)
CORS(app)  # VIOLATION: Enabling CORS without proper configuration

# VIOLATION: Global database connection without proper security
db_connection = sqlite3.connect('user_data.db', check_same_thread=False)

class UserDataAPI:
    def __init__(self):
        self.setup_database()

    # VIOLATION: Storing sensitive data in plain text
    def setup_database(self):
        cursor = db_connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT,
                email TEXT,
                password TEXT,  -- VIOLATION: Storing passwords in plain text
                age INTEGER,
                location TEXT,
                ip_address TEXT,
                device_fingerprint TEXT,
                created_at TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_behavior (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                action TEXT,
                data TEXT,
                timestamp TIMESTAMP
            )
        ''')
        db_connection.commit()

    # VIOLATION: Collecting user data without consent
    def register_user(self, user_data):
        cursor = db_connection.cursor()

        # VIOLATION: No input validation or sanitization
        user_id = str(uuid.uuid4())

        cursor.execute('''
            INSERT INTO users (name, email, password, age, location, ip_address, device_fingerprint, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_data.get('name'),
            user_data.get('email'),
            user_data.get('password'),  # VIOLATION: Plain text password
            user_data.get('age'),
            user_data.get('location'),
            request.remote_addr,  # VIOLATION: Storing IP without consent
            self.generate_device_fingerprint(request.headers),
            datetime.now()
        ))

        db_connection.commit()
        return user_id

    # VIOLATION: Device fingerprinting without consent
    def generate_device_fingerprint(self, headers):
        fingerprint_data = [
            headers.get('User-Agent', ''),
            headers.get('Accept-Language', ''),
            request.remote_addr,
            str(datetime.now())
        ]

        # VIOLATION: Creating unique identifiers
        fingerprint = hashlib.md5('|'.join(fingerprint_data).encode()).hexdigest()
        return fingerprint

    # VIOLATION: Tracking user behavior without consent
    def track_user_action(self, user_id, action, data=None):
        cursor = db_connection.cursor()

        cursor.execute('''
            INSERT INTO user_behavior (user_id, action, data, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (
            user_id,
            action,
            json.dumps(data) if data else None,
            datetime.now()
        ))

        db_connection.commit()

        # VIOLATION: Sharing behavior data with third parties
        self.share_behavior_with_partners(user_id, action, data)

    # VIOLATION: Sharing data with advertising partners
    def share_behavior_with_partners(self, user_id, action, data):
        partners = [
            'analytics.example.com',
            'ads.example.com',
            'tracking.example.com'
        ]

        for partner in partners:
            try:
                # VIOLATION: Making external API calls without user consent
                import requests
                requests.post(f'https://{partner}/track', json={
                    'user_id': user_id,
                    'action': action,
                    'data': data,
                    'timestamp': datetime.now().isoformat()
                })
            except:
                pass  # VIOLATION: Silent failures

    # VIOLATION: Exporting user data without proper authorization
    def export_user_data(self, user_id):
        cursor = db_connection.cursor()

        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user_row = cursor.fetchone()

        cursor.execute('SELECT * FROM user_behavior WHERE user_id = ?', (user_id,))
        behavior_rows = cursor.fetchall()

        # VIOLATION: Including sensitive data in export
        export_data = {
            'user_profile': dict(zip([desc[0] for desc in cursor.description], user_row)),
            'behavior_history': [dict(zip([desc[0] for desc in cursor.description], row)) for row in behavior_rows],
            'internal_analysis': self.generate_internal_analysis(user_id),
            'marketing_profile': self.create_marketing_profile(user_id)
        }

        return export_data

    # VIOLATION: Age verification issues
    def process_age_restricted_content(self, user_id, content_type):
        cursor = db_connection.cursor()
        cursor.execute('SELECT age FROM users WHERE id = ?', (user_id,))
        result = cursor.fetchone()

        if result:
            age = result[0]

            if age < 13:
                # VIOLATION: Processing children's data without parental consent
                self.process_child_content(user_id, content_type)
            elif age < 16:
                # VIOLATION: Insufficient restrictions for teens
                self.process_teen_content(user_id, content_type)
            else:
                # VIOLATION: No consent checks for adults
                self.process_adult_content(user_id, content_type)

    # VIOLATION: Collecting additional data on children
    def process_child_content(self, user_id, content_type):
        child_data = {
            'user_id': user_id,
            'content_type': content_type,
            'school_info': self.get_school_info(user_id),
            'parent_info': self.get_parent_info(user_id),
            'friends_list': self.get_friends_list(user_id),
            'activity_log': self.get_activity_log(user_id)
        }

        # VIOLATION: Storing children's data
        self.store_child_data(child_data)

    # VIOLATION: Location tracking
    def update_user_location(self, user_id, location_data):
        cursor = db_connection.cursor()

        # VIOLATION: Storing location without consent
        cursor.execute('''
            UPDATE users SET location = ? WHERE id = ?
        ''', (json.dumps(location_data), user_id))

        db_connection.commit()

        # VIOLATION: Sharing location with partners
        self.share_location_with_partners(user_id, location_data)

    # VIOLATION: Sharing location data
    def share_location_with_partners(self, user_id, location_data):
        partners = ['maps.example.com', 'ads.example.com', 'analytics.example.com']

        for partner in partners:
            try:
                import requests
                requests.post(f'https://{partner}/location-update', json={
                    'user_id': user_id,
                    'location': location_data,
                    'consent': False
                })
            except:
                pass

    # Helper methods with violations
    def get_school_info(self, user_id):
        # VIOLATION: Accessing external systems without authorization
        return {'school': 'Example School', 'grade': '6th'}

    def get_parent_info(self, user_id):
        # VIOLATION: Storing parent information
        return {'parent_name': 'Example Parent', 'contact': 'parent@example.com'}

    def get_friends_list(self, user_id):
        # VIOLATION: Collecting social graph data
        return [1, 2, 3, 4, 5]

    def get_activity_log(self, user_id):
        # VIOLATION: Comprehensive activity tracking
        return ['login', 'view_content', 'share', 'comment']

    def store_child_data(self, data):
        # VIOLATION: Storing children's data without proper safeguards
        with open(f'child_data_{data["user_id"]}.json', 'w') as f:
            json.dump(data, f)

    def generate_internal_analysis(self, user_id):
        return {
            'risk_score': 75,
            'engagement_level': 'high',
            'monetization_potential': 85
        }

    def create_marketing_profile(self, user_id):
        return {
            'segments': ['high_value', 'active_user'],
            'interests': ['gaming', 'social', 'entertainment'],
            'lifetime_value': 150.00
        }

# Global API instance
user_api = UserDataAPI()

# Flask routes with violations

@app.route('/api/register', methods=['POST'])
def register():
    # VIOLATION: No input validation
    user_data = request.get_json()

    # VIOLATION: Processing registration without consent
    user_id = user_api.register_user(user_data)

    # VIOLATION: Tracking registration event
    user_api.track_user_action(user_id, 'registration', user_data)

    return jsonify({'user_id': user_id, 'status': 'success'})

@app.route('/api/track', methods=['POST'])
def track_action():
    data = request.get_json()

    # VIOLATION: Tracking without consent verification
    user_api.track_user_action(
        data.get('user_id'),
        data.get('action'),
        data.get('data')
    )

    return jsonify({'status': 'tracked'})

@app.route('/api/export/<user_id>', methods=['GET'])
def export_data(user_id):
    # VIOLATION: No authorization checks
    export_data = user_api.export_user_data(user_id)

    return jsonify(export_data)

@app.route('/api/content/<user_id>/<content_type>', methods=['POST'])
def access_content(user_id, content_type):
    # VIOLATION: Processing age-restricted content
    user_api.process_age_restricted_content(user_id, content_type)

    return jsonify({'status': 'processed'})

@app.route('/api/location/<user_id>', methods=['POST'])
def update_location(user_id):
    location_data = request.get_json()

    # VIOLATION: Updating location without consent
    user_api.update_user_location(user_id, location_data)

    return jsonify({'status': 'updated'})

if __name__ == '__main__':
    # VIOLATION: Running in debug mode with sensitive data
    app.run(debug=True, host='0.0.0.0', port=5000)
