#!/usr/bin/env python3
"""
Backend API Testing for AI Email Reply Assistant
Tests all API endpoints using the public URL
"""

import requests
import json
import sys
from datetime import datetime
import time

class EmailReplyAPITester:
    def __init__(self, base_url="https://9b277e5b-c37b-4d0a-8c83-4617d52bead6.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.session_id = None

    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
        
        if details:
            print(f"   Details: {details}")
        print()

    def test_health_check(self):
        """Test health check endpoint"""
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                details = f"Status: {data.get('status')}, Service: {data.get('service')}"
            else:
                details = f"Status code: {response.status_code}"
                
            self.log_test("Health Check", success, details)
            return success
            
        except Exception as e:
            self.log_test("Health Check", False, str(e))
            return False

    def test_get_email_types(self):
        """Test get email types endpoint"""
        try:
            response = requests.get(f"{self.base_url}/api/email-types", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                email_types = data.get('email_types', [])
                details = f"Found {len(email_types)} email types: {[t['value'] for t in email_types[:3]]}..."
            else:
                details = f"Status code: {response.status_code}"
                
            self.log_test("Get Email Types", success, details)
            return success
            
        except Exception as e:
            self.log_test("Get Email Types", False, str(e))
            return False

    def test_get_tones(self):
        """Test get tones endpoint"""
        try:
            response = requests.get(f"{self.base_url}/api/tones", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                tones = data.get('tones', [])
                details = f"Found {len(tones)} tones: {[t['value'] for t in tones]}"
            else:
                details = f"Status code: {response.status_code}"
                
            self.log_test("Get Tones", success, details)
            return success
            
        except Exception as e:
            self.log_test("Get Tones", False, str(e))
            return False

    def test_generate_multiple_replies(self):
        """Test generate multiple replies endpoint"""
        sample_email = """Subject: Interview Invitation - Software Engineer Position

Dear John,

Thank you for your interest in the Software Engineer position at TechCorp. We were impressed with your application and would like to invite you for an interview.

We have availability for next Tuesday, March 12th at 2:00 PM or Wednesday, March 13th at 10:00 AM. The interview will be conducted via video call and should take approximately 45 minutes.

Please let me know which time works best for you.

Best regards,
Sarah Johnson
HR Manager, TechCorp"""

        try:
            payload = {
                "original_email": sample_email,
                "context": "This is a test interview invitation email",
                "user_name": "Test User"
            }
            
            response = requests.post(
                f"{self.base_url}/api/generate-replies",
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            success = response.status_code == 200
            
            if success:
                data = response.json()
                self.session_id = data.get('session_id')
                replies = data.get('replies', [])
                email_type = data.get('email_type')
                details = f"Generated {len(replies)} replies, Email type: {email_type}, Session ID: {self.session_id[:8]}..."
            else:
                try:
                    error_data = response.json()
                    details = f"Status: {response.status_code}, Error: {error_data.get('detail', 'Unknown error')}"
                except:
                    details = f"Status: {response.status_code}, Response: {response.text[:100]}..."
                
            self.log_test("Generate Multiple Replies", success, details)
            return success
            
        except Exception as e:
            self.log_test("Generate Multiple Replies", False, str(e))
            return False

    def test_generate_single_reply(self):
        """Test generate single reply endpoint"""
        sample_email = """Subject: Job Offer - Marketing Manager Position

Dear Jane,

We are pleased to offer you the position of Marketing Manager at Innovation Inc. After careful consideration, we believe you would be a great fit for our team.

The position comes with a competitive salary of $85,000 per year, full benefits package, and opportunities for professional development.

Please review the attached offer letter and let us know if you would like to accept this position.

Best regards,
Mike Thompson
Director of Marketing, Innovation Inc."""

        try:
            payload = {
                "original_email": sample_email,
                "context": "This is a test job offer email",
                "user_name": "Test User",
                "email_type": "job_offer",
                "tone": "enthusiastic"
            }
            
            response = requests.post(
                f"{self.base_url}/api/generate-single-reply",
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            success = response.status_code == 200
            
            if success:
                data = response.json()
                reply_id = data.get('reply_id')
                email_type = data.get('email_type')
                tone = data.get('tone')
                reply_length = len(data.get('reply_content', ''))
                details = f"Reply ID: {reply_id[:8]}..., Type: {email_type}, Tone: {tone}, Length: {reply_length} chars"
            else:
                try:
                    error_data = response.json()
                    details = f"Status: {response.status_code}, Error: {error_data.get('detail', 'Unknown error')}"
                except:
                    details = f"Status: {response.status_code}, Response: {response.text[:100]}..."
                
            self.log_test("Generate Single Reply", success, details)
            return success
            
        except Exception as e:
            self.log_test("Generate Single Reply", False, str(e))
            return False

    def test_get_session(self):
        """Test get session endpoint"""
        if not self.session_id:
            self.log_test("Get Session", False, "No session ID available from previous test")
            return False
            
        try:
            response = requests.get(f"{self.base_url}/api/session/{self.session_id}", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                replies_count = len(data.get('replies', []))
                email_type = data.get('email_type')
                details = f"Session found with {replies_count} replies, Type: {email_type}"
            else:
                details = f"Status code: {response.status_code}"
                
            self.log_test("Get Session", success, details)
            return success
            
        except Exception as e:
            self.log_test("Get Session", False, str(e))
            return False

    def test_error_handling(self):
        """Test error handling with invalid inputs"""
        try:
            # Test empty email
            payload = {
                "original_email": "",
                "context": "",
                "user_name": ""
            }
            
            response = requests.post(
                f"{self.base_url}/api/generate-replies",
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=15
            )
            
            # Should handle empty email gracefully
            success = response.status_code in [400, 422, 500]  # Any error status is acceptable
            details = f"Empty email handled with status: {response.status_code}"
                
            self.log_test("Error Handling (Empty Email)", success, details)
            return success
            
        except Exception as e:
            self.log_test("Error Handling (Empty Email)", False, str(e))
            return False

    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting AI Email Reply Assistant API Tests")
        print(f"📍 Testing against: {self.base_url}")
        print("=" * 60)
        
        # Basic endpoint tests
        self.test_health_check()
        self.test_get_email_types()
        self.test_get_tones()
        
        # Core functionality tests
        self.test_generate_multiple_replies()
        self.test_generate_single_reply()
        self.test_get_session()
        
        # Error handling tests
        self.test_error_handling()
        
        # Print summary
        print("=" * 60)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed!")
            return 0
        else:
            print(f"⚠️  {self.tests_run - self.tests_passed} tests failed")
            return 1

def main():
    """Main test runner"""
    tester = EmailReplyAPITester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())