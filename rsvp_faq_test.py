import requests
import sys
import json
from datetime import datetime
import time
import os

class RSVPFAQTester:
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
        self.shareable_id = None
        self.test_username = None
        self.critical_failures = []
        self.minor_issues = []
        self.rsvp_ids = []
        
        # Test data for RSVP functionality
        self.test_rsvp_data_attending = {
            "guest_name": "Arjun Sharma",
            "guest_email": "arjun.sharma@email.com",
            "guest_phone": "+91-9876543210",
            "attendance": "yes",
            "guest_count": 2,
            "dietary_restrictions": "Vegetarian only",
            "special_message": "So excited to celebrate with you both! Can't wait for the big day."
        }
        
        self.test_rsvp_data_declining = {
            "guest_name": "Priya Patel",
            "guest_email": "priya.patel@email.com", 
            "guest_phone": "+91-9876543211",
            "attendance": "no",
            "guest_count": 1,
            "dietary_restrictions": "",
            "special_message": "Unfortunately cannot make it due to prior commitments. Wishing you both all the happiness!"
        }
        
        # Test FAQ data
        self.test_faq_data = [
            {
                "question": "What is the dress code for the wedding?",
                "answer": "We recommend cocktail attire. Ladies, please consider comfortable shoes for outdoor surfaces."
            },
            {
                "question": "Will vegetarian food be available?",
                "answer": "Yes, we will have a full vegetarian menu available alongside non-vegetarian options."
            },
            {
                "question": "Is there parking available at the venue?",
                "answer": "Yes, complimentary valet parking is available at the venue entrance."
            },
            {
                "question": "Can I bring children to the wedding?",
                "answer": "This is an adults-only celebration. We appreciate your understanding."
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

    def test_api_health_check(self):
        """Test basic API connectivity"""
        def validate_health(response_data):
            return response_data.get('status') == 'ok'
        
        return self.run_test(
            "API Health Check", 
            "GET", 
            "api/test", 
            200,
            validate_response=validate_health
        )

    def setup_test_user_and_wedding(self):
        """Setup test user and wedding data for RSVP/FAQ testing"""
        # Generate unique username to avoid conflicts
        timestamp = int(time.time())
        test_data = {
            "username": f"rsvp_test_user_{timestamp}",
            "password": "wedding2025!"
        }
        
        def validate_registration(response_data):
            required_fields = ['session_id', 'user_id', 'username', 'success']
            return all(field in response_data for field in required_fields) and response_data.get('success') is True
        
        success, response = self.run_test(
            "Test User Registration",
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
            
            # Get wedding data to extract wedding_id and shareable_id
            wedding_success, wedding_response = self.run_test(
                "Get Wedding Data for Testing",
                "GET",
                "api/wedding",
                200,
                params={"session_id": self.session_id}
            )
            
            if wedding_success and wedding_response:
                self.wedding_id = wedding_response.get('id')
                self.shareable_id = wedding_response.get('shareable_id')
                print(f"   ✅ Wedding ID: {self.wedding_id}")
                print(f"   ✅ Shareable ID: {self.shareable_id}")
                
        return success, response

    def test_rsvp_submission_attending(self):
        """Test RSVP submission for attending guest"""
        if not self.wedding_id:
            self.critical_failures.append("RSVP Submission: No wedding_id available")
            return False, {}
        
        rsvp_data = self.test_rsvp_data_attending.copy()
        rsvp_data["wedding_id"] = self.wedding_id
        
        def validate_rsvp_submission(response_data):
            return (response_data.get('success') is True and 
                   'rsvp_id' in response_data and
                   response_data.get('message') == 'RSVP submitted successfully')
        
        success, response = self.run_test(
            "RSVP Submission - Attending Guest",
            "POST",
            "api/rsvp",
            200,
            data=rsvp_data,
            validate_response=validate_rsvp_submission
        )
        
        if success and response:
            rsvp_id = response.get('rsvp_id')
            self.rsvp_ids.append(rsvp_id)
            print(f"   ✅ RSVP ID: {rsvp_id}")
            
        return success, response

    def test_rsvp_submission_declining(self):
        """Test RSVP submission for declining guest"""
        if not self.wedding_id:
            self.critical_failures.append("RSVP Submission: No wedding_id available")
            return False, {}
        
        rsvp_data = self.test_rsvp_data_declining.copy()
        rsvp_data["wedding_id"] = self.wedding_id
        
        def validate_rsvp_submission(response_data):
            return (response_data.get('success') is True and 
                   'rsvp_id' in response_data and
                   response_data.get('message') == 'RSVP submitted successfully')
        
        success, response = self.run_test(
            "RSVP Submission - Declining Guest",
            "POST",
            "api/rsvp",
            200,
            data=rsvp_data,
            validate_response=validate_rsvp_submission
        )
        
        if success and response:
            rsvp_id = response.get('rsvp_id')
            self.rsvp_ids.append(rsvp_id)
            print(f"   ✅ RSVP ID: {rsvp_id}")
            
        return success, response

    def test_rsvp_retrieval_by_wedding_id(self):
        """Test RSVP retrieval by wedding ID"""
        if not self.wedding_id:
            self.critical_failures.append("RSVP Retrieval: No wedding_id available")
            return False, {}
        
        def validate_rsvp_retrieval(response_data):
            rsvps = response_data.get('rsvps', [])
            total_count = response_data.get('total_count', 0)
            
            # Should have at least 2 RSVPs (attending and declining)
            has_rsvps = len(rsvps) >= 2 and total_count >= 2
            
            # Check RSVP data structure
            if rsvps:
                first_rsvp = rsvps[0]
                required_fields = ['id', 'wedding_id', 'guest_name', 'guest_email', 'attendance', 'guest_count', 'submitted_at']
                has_required_fields = all(field in first_rsvp for field in required_fields)
                
                # Check for both attending and declining responses
                attendances = [rsvp.get('attendance') for rsvp in rsvps]
                has_both_responses = 'yes' in attendances and 'no' in attendances
                
                if not has_required_fields:
                    print(f"❌ Missing required RSVP fields. Found: {list(first_rsvp.keys())}")
                if not has_both_responses:
                    print(f"❌ Missing both yes/no responses. Found: {attendances}")
                
                return has_rsvps and has_required_fields and has_both_responses
            
            return has_rsvps
        
        success, response = self.run_test(
            "RSVP Retrieval by Wedding ID",
            "GET",
            f"api/rsvp/{self.wedding_id}",
            200,
            validate_response=validate_rsvp_retrieval
        )
        
        if success and response:
            rsvps = response.get('rsvps', [])
            print(f"   ✅ Retrieved {len(rsvps)} RSVPs")
            for rsvp in rsvps:
                print(f"   ✅ RSVP: {rsvp.get('guest_name')} - {rsvp.get('attendance')}")
            
        return success, response

    def test_rsvp_retrieval_by_shareable_id(self):
        """Test RSVP retrieval by shareable ID"""
        if not self.shareable_id:
            self.critical_failures.append("RSVP Retrieval: No shareable_id available")
            return False, {}
        
        def validate_rsvp_retrieval_shareable(response_data):
            rsvps = response_data.get('rsvps', [])
            total_count = response_data.get('total_count', 0)
            
            # Should have the same RSVPs as wedding ID retrieval
            has_rsvps = len(rsvps) >= 2 and total_count >= 2
            
            if rsvps:
                # Verify RSVP data structure and content
                guest_names = [rsvp.get('guest_name') for rsvp in rsvps]
                expected_names = ['Arjun Sharma', 'Priya Patel']
                has_expected_guests = all(name in guest_names for name in expected_names)
                
                if not has_expected_guests:
                    print(f"❌ Missing expected guests. Found: {guest_names}")
                
                return has_rsvps and has_expected_guests
            
            return has_rsvps
        
        success, response = self.run_test(
            "RSVP Retrieval by Shareable ID",
            "GET",
            f"api/rsvp/shareable/{self.shareable_id}",
            200,
            validate_response=validate_rsvp_retrieval_shareable
        )
        
        if success and response:
            rsvps = response.get('rsvps', [])
            print(f"   ✅ Retrieved {len(rsvps)} RSVPs via shareable ID")
            
        return success, response

    def test_rsvp_data_structure_validation(self):
        """Test RSVP data structure includes all required fields"""
        if not self.wedding_id:
            return False, {}
        
        def validate_rsvp_structure(response_data):
            rsvps = response_data.get('rsvps', [])
            if not rsvps:
                return False
            
            # Check first RSVP for all required fields
            rsvp = rsvps[0]
            required_fields = [
                'id', 'wedding_id', 'guest_name', 'guest_email', 'guest_phone',
                'attendance', 'guest_count', 'dietary_restrictions', 'special_message', 'submitted_at'
            ]
            
            missing_fields = [field for field in required_fields if field not in rsvp]
            if missing_fields:
                print(f"❌ Missing RSVP fields: {missing_fields}")
                return False
            
            # Validate data types and values
            valid_attendance = rsvp.get('attendance') in ['yes', 'no']
            valid_guest_count = isinstance(rsvp.get('guest_count'), int) and rsvp.get('guest_count') > 0
            valid_email = '@' in rsvp.get('guest_email', '')
            
            if not valid_attendance:
                print(f"❌ Invalid attendance value: {rsvp.get('attendance')}")
            if not valid_guest_count:
                print(f"❌ Invalid guest count: {rsvp.get('guest_count')}")
            if not valid_email:
                print(f"❌ Invalid email format: {rsvp.get('guest_email')}")
            
            return valid_attendance and valid_guest_count and valid_email
        
        return self.run_test(
            "RSVP Data Structure Validation",
            "GET",
            f"api/rsvp/{self.wedding_id}",
            200,
            validate_response=validate_rsvp_structure
        )

    def test_faq_update(self):
        """Test FAQ update functionality"""
        if not self.session_id:
            self.critical_failures.append("FAQ Update: No session_id available")
            return False, {}
        
        faq_update_data = {
            "session_id": self.session_id,
            "faqs": self.test_faq_data
        }
        
        def validate_faq_update(response_data):
            wedding_data = response_data.get('wedding_data', {})
            faqs = wedding_data.get('faqs', [])
            
            # Should have 4 FAQ items
            has_correct_count = len(faqs) == 4
            
            # Check FAQ structure
            if faqs:
                first_faq = faqs[0]
                has_required_fields = 'question' in first_faq and 'answer' in first_faq
                
                # Check specific FAQ content
                questions = [faq.get('question') for faq in faqs]
                expected_question = "What is the dress code for the wedding?"
                has_expected_content = expected_question in questions
                
                if not has_required_fields:
                    print(f"❌ FAQ missing required fields. Found: {list(first_faq.keys())}")
                if not has_expected_content:
                    print(f"❌ Missing expected FAQ content. Found questions: {questions}")
                
                return has_correct_count and has_required_fields and has_expected_content
            
            return has_correct_count
        
        success, response = self.run_test(
            "FAQ Update",
            "PUT",
            "api/wedding/faq",
            200,
            data=faq_update_data,
            validate_response=validate_faq_update
        )
        
        if success and response:
            wedding_data = response.get('wedding_data', {})
            faqs = wedding_data.get('faqs', [])
            print(f"   ✅ Updated {len(faqs)} FAQ items")
            
        return success, response

    def test_faq_retrieval_and_persistence(self):
        """Test FAQ data retrieval and persistence"""
        if not self.session_id:
            self.critical_failures.append("FAQ Retrieval: No session_id available")
            return False, {}
        
        def validate_faq_persistence(response_data):
            faqs = response_data.get('faqs', [])
            
            # Should have the 4 FAQs we just added
            has_correct_count = len(faqs) == 4
            
            # Check for specific FAQ content
            questions = [faq.get('question') for faq in faqs]
            expected_questions = [
                "What is the dress code for the wedding?",
                "Will vegetarian food be available?",
                "Is there parking available at the venue?",
                "Can I bring children to the wedding?"
            ]
            
            has_all_questions = all(q in questions for q in expected_questions)
            
            if not has_all_questions:
                print(f"❌ Missing expected FAQ questions. Found: {questions}")
            
            return has_correct_count and has_all_questions
        
        success, response = self.run_test(
            "FAQ Data Persistence",
            "GET",
            "api/wedding",
            200,
            params={"session_id": self.session_id},
            validate_response=validate_faq_persistence
        )
        
        if success and response:
            faqs = response.get('faqs', [])
            print(f"   ✅ FAQ persistence verified: {len(faqs)} items")
            
        return success, response

    def test_mongodb_data_persistence(self):
        """Test that all data is properly stored in MongoDB"""
        if not self.session_id:
            return False, {}
        
        def validate_mongodb_persistence(response_data):
            # Check that wedding data includes both RSVP and FAQ updates
            faqs = response_data.get('faqs', [])
            has_faqs = len(faqs) >= 4
            
            # Verify wedding data structure
            required_fields = ['id', 'user_id', 'couple_name_1', 'couple_name_2', 'faqs']
            has_required_fields = all(field in response_data for field in required_fields)
            
            # Check timestamps
            has_timestamps = 'created_at' in response_data and 'updated_at' in response_data
            
            return has_faqs and has_required_fields and has_timestamps
        
        return self.run_test(
            "MongoDB Data Persistence",
            "GET",
            "api/wedding",
            200,
            params={"session_id": self.session_id},
            validate_response=validate_mongodb_persistence
        )

    def test_error_handling(self):
        """Test error handling for invalid requests"""
        # Test RSVP submission without wedding_id
        invalid_rsvp_test = self.run_test(
            "RSVP Error Handling - Missing Wedding ID",
            "POST",
            "api/rsvp",
            200,  # API might still accept it but with empty wedding_id
            data={"guest_name": "Test Guest", "attendance": "yes"}
        )
        
        # Test FAQ update without session_id
        invalid_faq_test = self.run_test(
            "FAQ Error Handling - Missing Session ID",
            "PUT",
            "api/wedding/faq",
            400,
            data={"faqs": [{"question": "Test?", "answer": "Test answer"}]}
        )
        
        # Test RSVP retrieval with invalid shareable_id
        invalid_shareable_test = self.run_test(
            "RSVP Error Handling - Invalid Shareable ID",
            "GET",
            "api/rsvp/shareable/invalid-id-12345",
            404
        )
        
        return True, {}  # Error handling tests are informational

    def run_comprehensive_rsvp_faq_tests(self):
        """Run all RSVP and FAQ functionality tests"""
        print("🚀 Starting Comprehensive RSVP and FAQ Backend API Tests")
        print("🎯 Focus: Enhanced RSVP System & FAQ Management")
        print("🔗 Backend URL:", self.base_url)
        print("=" * 80)
        
        # Test sequence focusing on review request requirements
        tests = [
            ("1. API Health Check (GET /api/test)", self.test_api_health_check),
            ("2. Setup Test User and Wedding", self.setup_test_user_and_wedding),
            ("3. 🚨 RSVP Submission - Attending (POST /api/rsvp)", self.test_rsvp_submission_attending),
            ("4. 🚨 RSVP Submission - Declining (POST /api/rsvp)", self.test_rsvp_submission_declining),
            ("5. 🚨 RSVP Retrieval by Wedding ID (GET /api/rsvp/{wedding_id})", self.test_rsvp_retrieval_by_wedding_id),
            ("6. 🚨 RSVP Retrieval by Shareable ID (GET /api/rsvp/shareable/{shareable_id})", self.test_rsvp_retrieval_by_shareable_id),
            ("7. RSVP Data Structure Validation", self.test_rsvp_data_structure_validation),
            ("8. 🚨 FAQ Update (PUT /api/wedding/faq)", self.test_faq_update),
            ("9. FAQ Data Persistence", self.test_faq_retrieval_and_persistence),
            ("10. MongoDB Data Persistence", self.test_mongodb_data_persistence),
            ("11. Error Handling Tests", self.test_error_handling),
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
        print(f"📊 RSVP & FAQ BACKEND API TEST RESULTS")
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
        rsvp_working = not any("RSVP" in failure for failure in self.critical_failures)
        faq_working = not any("FAQ" in failure for failure in self.critical_failures)
        mongodb_working = not any("MongoDB" in failure for failure in self.critical_failures)
        
        print(f"\n📋 FUNCTIONALITY STATUS:")
        print(f"   RSVP System: {'✅ WORKING' if rsvp_working else '❌ FAILED'}")
        print(f"   FAQ Management: {'✅ WORKING' if faq_working else '❌ FAILED'}")
        print(f"   MongoDB Persistence: {'✅ WORKING' if mongodb_working else '❌ FAILED'}")
        
        if rsvp_working and faq_working and mongodb_working and len(self.critical_failures) == 0:
            print("\n✅ ALL CRITICAL RSVP & FAQ TESTS PASSED!")
            print("✅ RSVP submission and retrieval working correctly")
            print("✅ FAQ management functionality operational")
            print("✅ MongoDB data persistence working")
            return 0
        else:
            print("\n❌ CRITICAL RSVP & FAQ ISSUES DETECTED")
            if not rsvp_working:
                print("❌ RSVP system has issues")
            if not faq_working:
                print("❌ FAQ management has issues")
            if not mongodb_working:
                print("❌ MongoDB persistence has issues")
            return 1

def main():
    """Main test execution"""
    tester = RSVPFAQTester()
    return tester.run_comprehensive_rsvp_faq_tests()

if __name__ == "__main__":
    sys.exit(main())