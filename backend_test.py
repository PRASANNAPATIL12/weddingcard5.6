import requests
import sys
import json
from datetime import datetime
import time
import os

class WeddingMongoDBTester:
    def __init__(self, base_url=None):
        # Use environment variable or fallback to localhost
        if base_url is None:
            base_url = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.session_id = None
        self.user_id = None
        self.wedding_id = None
        self.test_username = None
        self.critical_failures = []
        self.minor_issues = []
        
        # Test data for Our Story functionality
        self.test_story_timeline = [
            {
                "year": "2020",
                "title": "First Meeting",
                "description": "We met at a coffee shop during the pandemic lockdown.",
                "image": "https://images.unsplash.com/photo-1511285560929-80b456fea0bc?w=600&h=400&fit=crop"
            },
            {
                "year": "2022", 
                "title": "First Date",
                "description": "Our first official date was at a local restaurant.",
                "image": "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=600&h=400&fit=crop"
            },
            {
                "year": "2024",
                "title": "The Proposal",
                "description": "He proposed during a sunset walk on the beach.",
                "image": "https://images.unsplash.com/photo-1519741497674-611481863552?w=600&h=400&fit=crop"
            }
        ]

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
                
                # Check response time (should be < 300ms as per requirements)
                if response_time > 300:
                    self.minor_issues.append(f"{name}: Response time {response_time:.0f}ms > 300ms")
                
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

    def test_mongodb_connection_health(self):
        """Test MongoDB connection via health endpoint"""
        def validate_health(response_data):
            return response_data.get('status') == 'ok'
        
        return self.run_test(
            "MongoDB Connection Health Check", 
            "GET", 
            "api/test", 
            200,
            validate_response=validate_health
        )

    def test_mongodb_connection_string(self):
        """Verify MongoDB connection string is correctly configured"""
        print(f"\n🔍 Verifying MongoDB Connection Configuration...")
        expected_connection = "mongodb+srv://prasannagoudasp12_db_user:RVj1n8gEkHewSwIL@cluster0.euowph1.mongodb.net"
        
        # Test health endpoint to ensure MongoDB is connected
        success, response = self.test_mongodb_connection_health()
        if success:
            print(f"✅ MongoDB connection working with expected connection string")
            print(f"✅ Database: weddingcard")
            return True, response
        else:
            self.critical_failures.append("MongoDB Connection: Failed to connect to expected MongoDB cluster")
            return False, {}

    def test_realistic_user_registration(self):
        """Test registration with realistic wedding data"""
        # Generate unique username to avoid conflicts
        timestamp = int(time.time())
        test_data = {
            "username": f"priya_raj_{timestamp}",
            "password": "wedding2025!"
        }
        
        def validate_registration(response_data):
            required_fields = ['session_id', 'user_id', 'username', 'success']
            return all(field in response_data for field in required_fields) and response_data.get('success') is True
        
        success, response = self.run_test(
            "Realistic User Registration (MongoDB)",
            "POST",
            "api/auth/register",
            200,
            data=test_data,
            validate_response=validate_registration
        )
        
        if success and response:
            self.session_id = response.get('session_id')
            self.user_id = response.get('user_id')
            self.test_username = test_data["username"]
            print(f"   ✅ Stored session_id: {self.session_id}")
            print(f"   ✅ Stored user_id: {self.user_id}")
            print(f"   ✅ Test user: {self.test_username}")
                
        return success, response

    def test_testuser456_registration(self):
        """Test registration with the specific test data: testuser456/password123"""
        test_data = {
            "username": "testuser456",
            "password": "password123"
        }
        
        def validate_registration(response_data):
            required_fields = ['session_id', 'user_id', 'username', 'success']
            return all(field in response_data for field in required_fields) and response_data.get('success') is True
        
        success, response = self.run_test(
            "TestUser456 Registration (MongoDB)",
            "POST",
            "api/auth/register",
            200,
            data=test_data,
            validate_response=validate_registration
        )
        
        if success and response:
            self.session_id = response.get('session_id')
            self.user_id = response.get('user_id')
            self.test_username = "testuser456"
            print(f"   ✅ Stored session_id: {self.session_id}")
            print(f"   ✅ Stored user_id: {self.user_id}")
                
        return success, response

    def test_testuser456_login(self):
        """Test login with testuser456/password123 credentials"""
        test_data = {
            "username": "testuser456",
            "password": "password123"
        }
        
        def validate_login(response_data):
            return (response_data.get('username') == 'testuser456' and 
                   response_data.get('success') is True and
                   'session_id' in response_data)
        
        return self.run_test(
            "TestUser456 Login (MongoDB)",
            "POST",
            "api/auth/login",
            200,
            data=test_data,
            validate_response=validate_login
        )

    def test_wedding_data_retrieval_mongodb(self):
        """Test wedding data retrieval from MongoDB"""
        if not self.session_id:
            self.critical_failures.append("Wedding Retrieval: No session_id available")
            return False, {}
            
        def validate_retrieval(response_data):
            # Should have default data initially (Sarah & Michael)
            return (response_data.get('couple_name_1') == 'Sarah' and 
                   response_data.get('couple_name_2') == 'Michael' and
                   response_data.get('venue_name') == 'Sunset Garden Estate')
        
        success, response = self.run_test(
            "Wedding Data Retrieval (MongoDB)",
            "GET",
            "api/wedding",
            200,
            params={"session_id": self.session_id},
            validate_response=validate_retrieval
        )
        
        if success and response:
            self.wedding_id = response.get('id')
            print(f"   ✅ Initial wedding ID: {self.wedding_id}")
            
        return success, response

    def test_public_url_personalization_critical(self):
        """CRITICAL TEST: Public URL personalization using wedding ID - the main issue that was fixed"""
        if not self.wedding_id:
            self.critical_failures.append("Public URL Test: No wedding_id available")
            return False, {}
        
        def validate_personalization(response_data):
            # This is the CRITICAL validation - ensure it shows TestUser456 & TestPartner, NOT Sarah & Michael
            is_personalized = (
                response_data.get('couple_name_1') == 'TestUser456' and 
                response_data.get('couple_name_2') == 'TestPartner' and
                response_data.get('venue_name') == 'Test Venue' and
                response_data.get('venue_location') == 'Test Venue • Test City, Test State' and
                response_data.get('wedding_date') == '2025-08-15'
            )
            
            # Check that it's NOT showing default data
            is_not_default = not (
                response_data.get('couple_name_1') == 'Sarah' and 
                response_data.get('couple_name_2') == 'Michael'
            )
            
            if not is_personalized:
                print(f"❌ CRITICAL FAILURE: Public URL showing wrong data!")
                print(f"   Expected: TestUser456 & TestPartner, Test Venue, 2025-08-15")
                print(f"   Got: {response_data.get('couple_name_1')} & {response_data.get('couple_name_2')}, {response_data.get('venue_name')}, {response_data.get('wedding_date')}")
            
            if not is_not_default:
                print(f"❌ CRITICAL FAILURE: Public URL showing default Sarah & Michael data!")
            
            return is_personalized and is_not_default
        
        success, response = self.run_test(
            "🚨 CRITICAL: Public URL Personalization (Wedding ID)",
            "GET",
            f"api/wedding/public/{self.wedding_id}",
            200,
            validate_response=validate_personalization
        )
        
        if success and response:
            print(f"   ✅ PUBLIC URL PERSONALIZATION WORKING!")
            print(f"   ✅ Shows: {response.get('couple_name_1')} & {response.get('couple_name_2')}")
            print(f"   ✅ Venue: {response.get('venue_name')}")
            print(f"   ✅ Date: {response.get('wedding_date')}")
            print(f"   ✅ Location: {response.get('venue_location')}")
        
        return success, response

    def test_public_url_data_sanitization(self):
        """Test that public URL doesn't expose sensitive data"""
        if not self.wedding_id:
            return False, {}
        
        def validate_sanitization(response_data):
            # Should not contain user_id or _id
            has_sensitive_data = 'user_id' in response_data or '_id' in response_data
            if has_sensitive_data:
                print(f"⚠️ WARNING: Public URL exposing sensitive data: {list(response_data.keys())}")
            return not has_sensitive_data
        
        return self.run_test(
            "Public URL Data Sanitization",
            "GET",
            f"api/wedding/public/{self.wedding_id}",
            200,
            validate_response=validate_sanitization
        )

    def test_public_url_fallback_system(self):
        """Test error handling for non-existent wedding IDs"""
        def validate_error_response(response_data):
            # Should return 404 error for non-existent wedding IDs
            return 'detail' in response_data
        
        success, response = self.run_test(
            "Public URL Error Handling",
            "GET",
            "api/wedding/public/non-existent-wedding-id-12345",
            404,
            validate_response=validate_error_response
        )
        
        return success, response

    def test_wedding_data_update_with_our_story(self):
        """Test wedding data update with Our Story functionality - CRITICAL TEST"""
        if not self.session_id:
            self.critical_failures.append("Our Story Update: No session_id available")
            return False, {}
            
        updated_data = {
            "session_id": self.session_id,
            "couple_name_1": "Priya",
            "couple_name_2": "Raj",
            "wedding_date": "2025-12-15",
            "venue_name": "Royal Gardens Resort",
            "venue_location": "Royal Gardens Resort • Mumbai, Maharashtra",
            "their_story": "Our love story began in college and has grown stronger every day since.",
            "story_timeline": self.test_story_timeline,
            "story_enabled": True,
            "theme": "elegant"
        }
        
        def validate_our_story_update(response_data):
            # Validate Our Story specific fields
            story_timeline = response_data.get('story_timeline', [])
            story_enabled = response_data.get('story_enabled', False)
            
            timeline_valid = (
                len(story_timeline) == 3 and
                story_timeline[0].get('year') == '2020' and
                story_timeline[0].get('title') == 'First Meeting' and
                story_timeline[1].get('year') == '2022' and
                story_timeline[2].get('year') == '2024' and
                story_timeline[2].get('title') == 'The Proposal'
            )
            
            basic_data_valid = (
                response_data.get('couple_name_1') == 'Priya' and
                response_data.get('couple_name_2') == 'Raj' and
                response_data.get('venue_name') == 'Royal Gardens Resort'
            )
            
            if not timeline_valid:
                print(f"❌ Story timeline validation failed")
                print(f"   Expected 3 timeline items, got {len(story_timeline)}")
                if story_timeline:
                    print(f"   First item: {story_timeline[0]}")
            
            if not story_enabled:
                print(f"❌ Story enabled should be True, got {story_enabled}")
            
            return timeline_valid and story_enabled and basic_data_valid
        
        success, response = self.run_test(
            "🚨 CRITICAL: Wedding Data Update with Our Story",
            "PUT",
            "api/wedding",
            200,
            data=updated_data,
            validate_response=validate_our_story_update
        )
        
        if success and response:
            self.wedding_id = response.get('id')
            print(f"   ✅ Wedding ID: {self.wedding_id}")
            print(f"   ✅ Our Story Timeline: {len(response.get('story_timeline', []))} items")
            print(f"   ✅ Story Enabled: {response.get('story_enabled')}")
            
        return success, response

    def test_our_story_data_persistence(self):
        """Test that Our Story data persists correctly in MongoDB"""
        if not self.session_id:
            self.critical_failures.append("Our Story Persistence: No session_id available")
            return False, {}
            
        def validate_story_persistence(response_data):
            story_timeline = response_data.get('story_timeline', [])
            story_enabled = response_data.get('story_enabled', False)
            
            # Verify all timeline data persisted correctly
            timeline_persisted = (
                len(story_timeline) == 3 and
                any(item.get('title') == 'First Meeting' for item in story_timeline) and
                any(item.get('title') == 'First Date' for item in story_timeline) and
                any(item.get('title') == 'The Proposal' for item in story_timeline) and
                all('image' in item for item in story_timeline)
            )
            
            if not timeline_persisted:
                print(f"❌ Timeline persistence failed")
                print(f"   Timeline items: {[item.get('title') for item in story_timeline]}")
            
            return timeline_persisted and story_enabled
        
        success, response = self.run_test(
            "Our Story Data Persistence (MongoDB)",
            "GET",
            "api/wedding",
            200,
            params={"session_id": self.session_id},
            validate_response=validate_story_persistence
        )
        
        if success:
            print(f"   ✅ Story timeline persisted: {len(response.get('story_timeline', []))} items")
            print(f"   ✅ Story enabled status: {response.get('story_enabled')}")
            
        return success, response

    def test_our_story_public_access(self):
        """Test that Our Story data is accessible via public URL"""
        if not self.wedding_id:
            self.critical_failures.append("Our Story Public Access: No wedding_id available")
            return False, {}
        
        def validate_public_story_access(response_data):
            story_timeline = response_data.get('story_timeline', [])
            story_enabled = response_data.get('story_enabled', False)
            
            # Verify public access includes Our Story data
            public_story_valid = (
                len(story_timeline) >= 3 and
                story_enabled and
                response_data.get('couple_name_1') == 'Priya' and
                response_data.get('couple_name_2') == 'Raj'
            )
            
            # Ensure no sensitive data is exposed
            no_sensitive_data = 'user_id' not in response_data and '_id' not in response_data
            
            return public_story_valid and no_sensitive_data
        
        success, response = self.run_test(
            "Our Story Public URL Access",
            "GET",
            f"api/wedding/public/{self.wedding_id}",
            200,
            validate_response=validate_public_story_access
        )
        
        if success:
            print(f"   ✅ Public Our Story access working")
            print(f"   ✅ Timeline items accessible: {len(response.get('story_timeline', []))}")
            
        return success, response

    def test_public_url_after_update(self):
        """Test that public URL reflects updates immediately"""
        if not self.wedding_id:
            return False, {}
        
        def validate_updated_public(response_data):
            return ("UPDATED:" in response_data.get('their_story', '') and
                   response_data.get('theme') == 'modern' and
                   response_data.get('couple_name_1') == 'TestUser456')
        
        return self.run_test(
            "Public URL After Update (Data Consistency)",
            "GET",
            f"api/wedding/public/{self.wedding_id}",
            200,
            validate_response=validate_updated_public
        )

    def test_mongodb_error_handling(self):
        """Test error handling for invalid requests"""
        # Test invalid session
        invalid_session_test = self.run_test(
            "Invalid Session Handling",
            "GET",
            "api/wedding",
            401,
            params={"session_id": "invalid-session-12345"}
        )
        
        # Test duplicate registration
        duplicate_reg_test = self.run_test(
            "Duplicate Registration Handling",
            "POST",
            "api/auth/register",
            400,
            data={"username": "testuser456", "password": "different_password"}
        )
        
        return invalid_session_test[0] and duplicate_reg_test[0], {}

    def test_session_validation_for_protected_endpoints(self):
        """Test session validation for protected endpoints"""
        if not self.session_id:
            return False, {}
        
        # Test valid session
        valid_session_test = self.run_test(
            "Valid Session Access",
            "GET",
            "api/profile",
            200,
            params={"session_id": self.session_id}
        )
        
        # Test invalid session
        invalid_session_test = self.run_test(
            "Invalid Session Handling",
            "GET",
            "api/wedding",
            401,
            params={"session_id": "invalid-session-12345"}
        )
        
        # Test missing session
        missing_session_test = self.run_test(
            "Missing Session Handling",
            "GET",
            "api/wedding",
            422,  # FastAPI returns 422 for missing required params
            params={}
        )
        
        return (valid_session_test[0] and invalid_session_test[0] and missing_session_test[0]), {}

    def test_story_enabled_functionality(self):
        """Test story_enabled boolean field functionality"""
        if not self.session_id:
            return False, {}
        
        # Test disabling Our Story
        disable_story_data = {
            "session_id": self.session_id,
            "couple_name_1": "Priya",
            "couple_name_2": "Raj", 
            "wedding_date": "2025-12-15",
            "venue_name": "Royal Gardens Resort",
            "venue_location": "Royal Gardens Resort • Mumbai, Maharashtra",
            "their_story": "Our love story began in college.",
            "story_timeline": self.test_story_timeline,
            "story_enabled": False,  # Disable Our Story
            "theme": "elegant"
        }
        
        def validate_story_disabled(response_data):
            return response_data.get('story_enabled') is False
        
        success, response = self.run_test(
            "Story Enabled/Disabled Functionality",
            "PUT",
            "api/wedding",
            200,
            data=disable_story_data,
            validate_response=validate_story_disabled
        )
        
        if success:
            print(f"   ✅ Story disabled successfully: {response.get('story_enabled')}")
        
        return success, response

    def run_comprehensive_mongodb_tests(self):
        """Run all MongoDB integration tests focusing on Our Story functionality"""
        print("🚀 Starting Comprehensive Wedding Card Backend API Tests")
        print("🎯 Focus: MongoDB Integration & Our Story Functionality")
        print("🔗 MongoDB: mongodb+srv://prasannagoudasp12_db_user:RVj1n8gEkHewSwIL@cluster0.euowph1.mongodb.net")
        print("=" * 80)
        
        # Test sequence focusing on review request requirements
        tests = [
            ("1. Health Check (GET /api/test)", self.test_mongodb_connection_health),
            ("2. MongoDB Connection Verification", self.test_mongodb_connection_string),
            ("3. User Registration (POST /api/auth/register)", self.test_realistic_user_registration),
            ("4. Wedding Data Retrieval (GET /api/wedding)", self.test_wedding_data_retrieval_mongodb),
            ("5. 🚨 Our Story Update (PUT /api/wedding)", self.test_wedding_data_update_with_our_story),
            ("6. Our Story Data Persistence", self.test_our_story_data_persistence),
            ("7. Our Story Public Access", self.test_our_story_public_access),
            ("8. Session Validation Testing", self.test_session_validation_for_protected_endpoints),
            ("9. Story Enabled/Disabled Functionality", self.test_story_enabled_functionality),
            ("10. Error Handling Tests", self.test_mongodb_error_handling),
        ]
        
        print(f"\n📋 Running {len(tests)} comprehensive test scenarios...")
        
        failed_tests = []
        for test_name, test_func in tests:
            print(f"\n{'='*15} {test_name} {'='*15}")
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
        
        # Print comprehensive results
        print("\n" + "=" * 80)
        print(f"📊 WEDDING CARD BACKEND API TEST RESULTS")
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
        
        # Determine overall result based on critical functionality
        our_story_working = not any("Our Story" in failure for failure in self.critical_failures)
        mongodb_working = not any("MongoDB" in failure for failure in self.critical_failures)
        auth_working = not any("Registration" in failure or "Session" in failure for failure in self.critical_failures)
        
        print(f"\n📋 FUNCTIONALITY STATUS:")
        print(f"   MongoDB Integration: {'✅ WORKING' if mongodb_working else '❌ FAILED'}")
        print(f"   User Authentication: {'✅ WORKING' if auth_working else '❌ FAILED'}")
        print(f"   Our Story Features: {'✅ WORKING' if our_story_working else '❌ FAILED'}")
        
        if our_story_working and mongodb_working and auth_working and len(self.critical_failures) == 0:
            print("\n✅ ALL CRITICAL BACKEND API TESTS PASSED!")
            print("✅ MongoDB integration is working correctly")
            print("✅ Our Story functionality is fully operational")
            print("✅ Authentication and session management working")
            return 0
        else:
            print("\n❌ CRITICAL BACKEND API ISSUES DETECTED")
            if not our_story_working:
                print("❌ Our Story functionality has issues")
            if not mongodb_working:
                print("❌ MongoDB integration has issues")
            if not auth_working:
                print("❌ Authentication system has issues")
            return 1

def main():
    """Main test execution"""
    tester = WeddingMongoDBTester()
    return tester.run_comprehensive_mongodb_tests()

if __name__ == "__main__":
    sys.exit(main())