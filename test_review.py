"""
Test script to submit a review
"""

import requests

# Test data
review_data = {
    'college_id': 1,
    'student_name': 'Test Student',
    'student_email': 'test@example.com',
    'review_text': 'This is a test review. Great college!',
    'rating': 5
}

# Since we can't easily upload a file via requests without a real file,
# let's modify the backend temporarily to make id_card optional for testing
# But for now, let's check if the endpoint accepts the request

url = 'http://127.0.0.1:5000/api/reviews'

# For testing without file, we can comment out the file requirement in backend
# But let's see what happens

print("Testing review submission endpoint...")
try:
    response = requests.post(url, data=review_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")