#!/usr/bin/env python3
"""Test the JSON output cleanliness"""

import sys
import os
import subprocess
import json

extension_python_dir = os.path.join(os.path.dirname(__file__), 'extension', 'src', 'python')

test_code = '''
def register_user(user_data):
    password = user_data.get('password')
    # No consent check
    return {"status": "registered"}
'''

# Format as JSON input expected by the script
test_input = {
    "features": [
        {
            "id": "test_001",
            "feature_name": "register_user",
            "description": "User registration function",
            "code": test_code
        }
    ]
}

print("🧪 Testing Clean JSON Output")
print("=" * 50)

try:
    # Test the Python script output
    cmd = [
        'C:\\Users\\58dya\\AppData\\Local\\Programs\\Python\\Python312\\python.exe',
        'compliance_analyzer.py',
        'test.py'
    ]
    
    result = subprocess.run(
        cmd,
        input=json.dumps(test_input),
        capture_output=True,
        text=True,
        cwd=extension_python_dir
    )
    
    print(f"Return code: {result.returncode}")
    print(f"Stderr length: {len(result.stderr)} chars")
    print(f"Stdout length: {len(result.stdout)} chars")
    
    if result.stderr:
        print(f"\nStderr (informational messages):")
        print(result.stderr[:200] + "..." if len(result.stderr) > 200 else result.stderr)
    
    if result.stdout:
        print(f"\nStdout (should be clean JSON):")
        print("First 100 chars:", repr(result.stdout[:100]))
        
        # Try to parse as JSON
        import json
        try:
            data = json.loads(result.stdout)
            print("✅ JSON parsing successful!")
            print(f"✅ Found {len(data.get('detailed_results', []))} analysis results")
            print(f"✅ Found {len(data.get('recommendations', []))} recommendations")
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing failed: {e}")
    
except Exception as e:
    print(f"❌ Error: {e}")

print("=" * 50)
