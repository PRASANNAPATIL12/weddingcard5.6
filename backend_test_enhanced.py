import requests
import sys
import json
from datetime import datetime
import time
import uuid

class EnhancedWeddingTester:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.session_id = None
        self.user_id = None
        self.wedding_id = None
        self.test_username = None
        self.critical_failures = []
        self.minor_issues = []

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None, params=None, validate_response=None):
        """Run a single API test with optional response validation"""
        url = f"{self.base_url}/{endpoint}"
        default_headers = {'Content-Type': 'application/json'}
        
        if headers:
            default_headers.update(headers)

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        if data:
            print(f"   Data: {json.dumps(data, indent=2)}")
        if params:
            print(f"   Params: {params}")
        
        start_time = time.time()
        try:
            if method == 'GET':
                response = requests.get(url, headers=default_headers, params=params, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=default_headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=default_headers, timeout=10)

            response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code} ({response_time:.0f}ms)")
                
                # Check response time (should be < 3000ms as per requirements)
                if response_time > 3000:
                    self.minor_issues.append(f"{name}: Response time {response_time:.0f}ms > 3000ms")
                
                if response.content:
                    try:
                        response_data = response.json()
                        print(f"Response: {json.dumps(response_data, indent=2)}")
                        
                        # Run custom validation if provided
                        if validate_response:
                            validation_result = validate_response(response_data)
                            if not validation_result:
                                self.critical_failures.append(f"{name}: Response validation failed")
                                return False, response_data
                        
                        return True, response_data
                    except:
                        print(f"Response: {response.text[:200]}")
                        return True, {}
                return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code} ({response_time:.0f}ms)")
                try:
                    error_data = response.json()
                    print(f"Error Response: {json.dumps(error_data, indent=2)}")
                    self.critical_failures.append(f"{name}: HTTP {response.status_code} - {error_data.get('detail', 'Unknown error')}")
                except:
                    print(f"Error Response: {response.text[:200]}")
                    self.critical_failures.append(f"{name}: HTTP {response.status_code} - {response.text[:100]}")
                return False, {}

        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            print(f"❌ Failed - Error: {str(e)} ({response_time:.0f}ms)")
            self.critical_failures.append(f"{name}: Connection/Network error - {str(e)}")
            return False, {}

    def test_health_check(self):
        """Test basic health check"""
        def validate_health(response_data):
            return response_data.get('status') == 'ok'
        
        return self.run_test(
            "Health Check", 
            "GET", 
            "api/test", 
            200,
            validate_response=validate_health
        )

    def test_specific_shareable_url(self):
        """Test the specific shareable URL mentioned in the request: 679d5136"""
        def validate_shraddha_deepak(response_data):
            # Should show "Shraddha & Deepak" with "Royal Palace Hotel • Delhi, India"
            is_correct = (
                response_data.get('couple_name_1') == 'Shraddha' and 
                response_data.get('couple_name_2') == 'Deepak' and
                'Royal Palace Hotel' in response_data.get('venue_location', '') and
                'Delhi, India' in response_data.get('venue_location', '')
            )
            
            if not is_correct:
                print(f"❌ CRITICAL: Expected 'Shraddha & Deepak' with 'Royal Palace Hotel • Delhi, India'")
                print(f"   Got: {response_data.get('couple_name_1')} & {response_data.get('couple_name_2')}")
                print(f"   Venue: {response_data.get('venue_location')}")
            
            return is_correct
        
        return self.run_test(
            "🚨 CRITICAL: Shareable URL 679d5136 (Shraddha & Deepak)",
            "GET",
            "api/wedding/share/679d5136",
            200,
            validate_response=validate_shraddha_deepak
        )

    def test_new_user_registration(self):
        """Test registration with a unique username"""
        unique_username = f"testuser_{int(time.time())}"
        test_data = {
            "username": unique_username,
            "password": "password123"
        }
        
        def validate_registration(response_data):
            required_fields = ['session_id', 'user_id', 'username', 'success']
            return all(field in response_data for field in required_fields) and response_data.get('success') is True
        
        success, response = self.run_test(
            "New User Registration",
            "POST",
            "api/auth/register",
            200,
            data=test_data,
            validate_response=validate_registration
        )
        
        if success and response:
            self.session_id = response.get('session_id')
            self.user_id = response.get('user_id')
            self.test_username = unique_username
            print(f"   ✅ Stored session_id: {self.session_id}")
            print(f"   ✅ Stored user_id: {self.user_id}")
                
        return success, response

    def test_wedding_data_save_no_401(self):
        """Test wedding data save - should NOT get 401 error (main fix)"""
        if not self.session_id:
            self.critical_failures.append("Wedding Save: No session_id available")
            return False, {}
            
        updated_data = {
            "session_id": self.session_id,
            "couple_name_1": "TestBride",
            "couple_name_2": "TestGroom",
            "wedding_date": "2025-12-25",
            "venue_name": "Test Wedding Venue",
            "venue_location": "Test Wedding Venue • Test City, Test State",
            "their_story": "This is our test love story to verify the 401 fix is working.",
            "theme": "classic"
        }
        
        def validate_save(response_data):
            return (response_data.get('couple_name_1') == 'TestBride' and
                   response_data.get('couple_name_2') == 'TestGroom' and
                   response_data.get('theme') == 'classic')
        
        success, response = self.run_test(
            "🚨 CRITICAL: Wedding Data Save (No 401 Error)",
            "PUT",
            "api/wedding",
            200,
            data=updated_data,
            validate_response=validate_save
        )
        
        if success and response:
            self.wedding_id = response.get('id')
            print(f"   ✅ Wedding saved successfully, ID: {self.wedding_id}")
            
        return success, response

    def test_session_persistence_simulation(self):
        """Test that session works after being stored in MongoDB"""
        if not self.session_id:
            return False, {}
        
        # Test that we can retrieve wedding data with the session
        def validate_retrieval(response_data):
            return (response_data.get('couple_name_1') == 'TestBride' and
                   response_data.get('couple_name_2') == 'TestGroom')
        
        return self.run_test(
            "Session Persistence (MongoDB Storage)",
            "GET",
            "api/wedding",
            200,
            params={"session_id": self.session_id},
            validate_response=validate_retrieval
        )

    def test_public_wedding_access(self):
        """Test public access to wedding data"""
        if not self.wedding_id:
            return False, {}
        
        def validate_public_access(response_data):
            # Should not contain sensitive data
            has_sensitive = 'user_id' in response_data or '_id' in response_data
            has_correct_data = (response_data.get('couple_name_1') == 'TestBride' and
                              response_data.get('couple_name_2') == 'TestGroom')
            
            if has_sensitive:
                print(f"⚠️ WARNING: Public URL exposing sensitive data")
            
            return not has_sensitive and has_correct_data
        
        return self.run_test(
            "Public Wedding Access (Data Sanitization)",
            "GET",
            f"api/wedding/public/{self.wedding_id}",
            200,
            validate_response=validate_public_access
        )

    def run_enhanced_tests(self):
        """Run enhanced tests focusing on the two critical fixes"""
        print("🚀 Enhanced Wedding Card System v6.0 Testing")
        print("🎯 Focus: 401 Authentication Fix & Shareable Link Personalization")
        print("=" * 80)
        
        tests = [
            ("Health Check", self.test_health_check),
            ("🚨 Shareable URL 679d5136 Test", self.test_specific_shareable_url),
            ("New User Registration", self.test_new_user_registration),
            ("🚨 Wedding Save (No 401 Fix)", self.test_wedding_data_save_no_401),
            ("Session Persistence", self.test_session_persistence_simulation),
            ("Public Wedding Access", self.test_public_wedding_access)
        ]
        
        print(f"\n📋 Running {len(tests)} enhanced test scenarios...")
        
        failed_tests = []
        for test_name, test_func in tests:
            print(f"\n{'='*25} {test_name} {'='*25}")
            try:
                success, response = test_func()
                if not success:
                    print(f"❌ {test_name} FAILED")
                    failed_tests.append(test_name)
                else:
                    print(f"✅ {test_name} PASSED")
            except Exception as e:
                print(f"❌ {test_name} FAILED with exception: {str(e)}")
                failed_tests.append(test_name)
                self.critical_failures.append(f"{test_name}: Exception - {str(e)}")
        
        # Print results
        print("\n" + "=" * 80)
        print(f"📊 ENHANCED TEST RESULTS")
        print(f"   Tests Run: {self.tests_run}")
        print(f"   Tests Passed: {self.tests_passed}")
        print(f"   Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if self.critical_failures:
            print(f"\n🚨 CRITICAL FAILURES ({len(self.critical_failures)}):")
            for failure in self.critical_failures:
                print(f"   ❌ {failure}")
        
        if self.minor_issues:
            print(f"\n⚠️  MINOR ISSUES ({len(self.minor_issues)}):")
            for issue in self.minor_issues:
                print(f"   ⚠️  {issue}")
        
        if failed_tests:
            print(f"\n❌ FAILED TESTS: {', '.join(failed_tests)}")
        
        # Check critical fixes
        auth_fix_working = not any("401" in failure for failure in self.critical_failures)
        shareable_fix_working = not any("679d5136" in failure for failure in self.critical_failures)
        
        if auth_fix_working and shareable_fix_working and len(self.critical_failures) == 0:
            print("\n✅ ALL CRITICAL FIXES VERIFIED!")
            print("✅ 401 Authentication error fix is working")
            print("✅ Shareable link personalization is working")
            return 0
        else:
            print("\n❌ CRITICAL ISSUES DETECTED")
            if not auth_fix_working:
                print("❌ 401 Authentication fix has issues")
            if not shareable_fix_working:
                print("❌ Shareable link personalization has issues")
            return 1

def main():
    """Main test execution"""
    tester = EnhancedWeddingTester()
    return tester.run_enhanced_tests()

if __name__ == "__main__":
    sys.exit(main())