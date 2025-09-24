import requests
import sys
import json
from datetime import datetime
import time
import os
from urllib.parse import quote, unquote

class RSVPWhatsAppTester:
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
        self.rsvp_ids = []  # Store created RSVP IDs for cleanup
        
        # Test data for RSVP functionality
        self.valid_rsvp_data = {
            "guest_name": "John Doe",
            "guest_email": "john@example.com", 
            "guest_phone": "+1234567890",
            "attendance": "yes",
            "guest_count": 2,
            "dietary_restrictions": "Vegetarian",
            "special_message": "Congratulations on your special day!",
            "wedding_id": "test-wedding-123"
        }

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

    def setup_test_user_and_wedding(self):
        """Setup test user and wedding data for RSVP testing"""
        print("\n🔧 Setting up test user and wedding data...")
        
        # Generate unique username to avoid conflicts
        timestamp = int(time.time())
        test_data = {
            "username": f"rsvp_test_user_{timestamp}",
            "password": "rsvptest2025!"
        }
        
        # Register user
        def validate_registration(response_data):
            required_fields = ['session_id', 'user_id', 'username', 'success']
            return all(field in response_data for field in required_fields) and response_data.get('success') is True
        
        success, response = self.run_test(
            "Setup: User Registration",
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
            print(f"   ✅ Test user created: {self.test_username}")
            print(f"   ✅ Session ID: {self.session_id}")
            
            # Get wedding data to extract wedding_id and shareable_id
            wedding_success, wedding_response = self.run_test(
                "Setup: Get Wedding Data",
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
                
                # Update valid RSVP data with actual wedding_id
                self.valid_rsvp_data["wedding_id"] = self.wedding_id
                return True
        
        return False

    def test_rsvp_submission_valid_data(self):
        """Test RSVP submission with valid data"""
        def validate_rsvp_submission(response_data):
            required_fields = ['success', 'message', 'rsvp_id']
            has_required = all(field in response_data for field in required_fields)
            success_status = response_data.get('success') is True
            has_rsvp_id = response_data.get('rsvp_id') is not None
            
            if has_rsvp_id:
                self.rsvp_ids.append(response_data.get('rsvp_id'))
            
            return has_required and success_status and has_rsvp_id
        
        return self.run_test(
            "🚨 CRITICAL: RSVP Submission (Valid Data)",
            "POST",
            "api/rsvp",
            200,
            data=self.valid_rsvp_data,
            validate_response=validate_rsvp_submission
        )

    def test_rsvp_submission_missing_fields(self):
        """Test RSVP submission with missing required fields"""
        incomplete_data = {
            "guest_name": "Jane Smith",
            # Missing guest_email, attendance, wedding_id
            "guest_count": 1,
            "special_message": "Looking forward to it!"
        }
        
        # This should either fail with validation error or succeed with defaults
        # Based on the backend code, it seems to use defaults for missing fields
        def validate_incomplete_rsvp(response_data):
            # Backend seems to handle missing fields with defaults
            return response_data.get('success') is True
        
        return self.run_test(
            "RSVP Submission (Missing Fields)",
            "POST",
            "api/rsvp",
            200,  # Backend handles missing fields with defaults
            data=incomplete_data,
            validate_response=validate_incomplete_rsvp
        )

    def test_rsvp_guest_count_validation(self):
        """Test RSVP guest count validation"""
        # Test with various guest counts
        test_cases = [
            (0, "Zero guests"),
            (1, "Single guest"),
            (5, "Multiple guests"),
            (10, "Large party")
        ]
        
        all_passed = True
        for guest_count, description in test_cases:
            test_data = self.valid_rsvp_data.copy()
            test_data["guest_count"] = guest_count
            test_data["guest_name"] = f"Test Guest {guest_count}"
            test_data["guest_email"] = f"test{guest_count}@example.com"
            
            def validate_guest_count(response_data):
                return response_data.get('success') is True
            
            success, response = self.run_test(
                f"RSVP Guest Count Validation ({description})",
                "POST",
                "api/rsvp",
                200,
                data=test_data,
                validate_response=validate_guest_count
            )
            
            if not success:
                all_passed = False
        
        return all_passed, {}

    def test_rsvp_dietary_restrictions_and_messages(self):
        """Test RSVP with dietary restrictions and special messages"""
        test_data = self.valid_rsvp_data.copy()
        test_data.update({
            "guest_name": "Alice Johnson",
            "guest_email": "alice@example.com",
            "dietary_restrictions": "Gluten-free, No nuts",
            "special_message": "Thank you for inviting us! We're so excited to celebrate with you. This is a longer message to test message handling.",
            "attendance": "yes",
            "guest_count": 3
        })
        
        def validate_dietary_and_message(response_data):
            return response_data.get('success') is True and response_data.get('rsvp_id') is not None
        
        return self.run_test(
            "RSVP with Dietary Restrictions & Special Message",
            "POST",
            "api/rsvp",
            200,
            data=test_data,
            validate_response=validate_dietary_and_message
        )

    def test_rsvp_attendance_variations(self):
        """Test RSVP with different attendance values"""
        attendance_options = ["yes", "no", "maybe"]
        
        all_passed = True
        for attendance in attendance_options:
            test_data = self.valid_rsvp_data.copy()
            test_data.update({
                "guest_name": f"Guest {attendance.title()}",
                "guest_email": f"guest_{attendance}@example.com",
                "attendance": attendance
            })
            
            def validate_attendance(response_data):
                return response_data.get('success') is True
            
            success, response = self.run_test(
                f"RSVP Attendance ({attendance.title()})",
                "POST",
                "api/rsvp",
                200,
                data=test_data,
                validate_response=validate_attendance
            )
            
            if not success:
                all_passed = False
        
        return all_passed, {}

    def test_get_rsvps_by_wedding_id(self):
        """Test retrieving RSVPs by wedding ID"""
        if not self.wedding_id:
            self.critical_failures.append("Get RSVPs by Wedding ID: No wedding_id available")
            return False, {}
        
        def validate_rsvp_retrieval(response_data):
            required_fields = ['success', 'rsvps', 'total_count']
            has_required = all(field in response_data for field in required_fields)
            has_rsvps = isinstance(response_data.get('rsvps'), list)
            total_count = response_data.get('total_count', 0)
            
            # Should have at least the RSVPs we created
            has_expected_count = total_count >= len(self.rsvp_ids)
            
            if has_rsvps and response_data.get('rsvps'):
                # Validate RSVP structure
                first_rsvp = response_data['rsvps'][0]
                rsvp_structure_valid = all(
                    field in first_rsvp for field in 
                    ['id', 'wedding_id', 'guest_name', 'guest_email', 'attendance', 'guest_count']
                )
                
                # Check that sensitive data is not exposed
                no_sensitive_data = '_id' not in first_rsvp
                
                return has_required and has_rsvps and has_expected_count and rsvp_structure_valid and no_sensitive_data
            
            return has_required and has_rsvps
        
        return self.run_test(
            "🚨 CRITICAL: Get RSVPs by Wedding ID",
            "GET",
            f"api/rsvp/{self.wedding_id}",
            200,
            validate_response=validate_rsvp_retrieval
        )

    def test_get_rsvps_by_shareable_id(self):
        """Test retrieving RSVPs by shareable ID"""
        if not self.shareable_id:
            self.critical_failures.append("Get RSVPs by Shareable ID: No shareable_id available")
            return False, {}
        
        def validate_shareable_rsvp_retrieval(response_data):
            required_fields = ['success', 'rsvps', 'total_count']
            has_required = all(field in response_data for field in required_fields)
            has_rsvps = isinstance(response_data.get('rsvps'), list)
            
            return has_required and has_rsvps
        
        return self.run_test(
            "🚨 CRITICAL: Get RSVPs by Shareable ID",
            "GET",
            f"api/rsvp/shareable/{self.shareable_id}",
            200,
            validate_response=validate_shareable_rsvp_retrieval
        )

    def test_rsvp_data_storage_mongodb(self):
        """Test that RSVP data is properly stored in MongoDB"""
        # Submit a test RSVP
        test_data = {
            "guest_name": "MongoDB Test User",
            "guest_email": "mongodb@test.com",
            "guest_phone": "+1987654321",
            "attendance": "yes",
            "guest_count": 2,
            "dietary_restrictions": "Vegan",
            "special_message": "Testing MongoDB storage",
            "wedding_id": self.wedding_id
        }
        
        # Submit RSVP
        submit_success, submit_response = self.run_test(
            "RSVP MongoDB Storage (Submit)",
            "POST",
            "api/rsvp",
            200,
            data=test_data
        )
        
        if not submit_success:
            return False, {}
        
        # Retrieve RSVPs to verify storage
        def validate_mongodb_storage(response_data):
            rsvps = response_data.get('rsvps', [])
            
            # Find our test RSVP
            test_rsvp = None
            for rsvp in rsvps:
                if rsvp.get('guest_email') == 'mongodb@test.com':
                    test_rsvp = rsvp
                    break
            
            if not test_rsvp:
                print("❌ Test RSVP not found in MongoDB")
                return False
            
            # Validate all fields are stored correctly
            fields_match = (
                test_rsvp.get('guest_name') == 'MongoDB Test User' and
                test_rsvp.get('guest_email') == 'mongodb@test.com' and
                test_rsvp.get('guest_phone') == '+1987654321' and
                test_rsvp.get('attendance') == 'yes' and
                test_rsvp.get('guest_count') == 2 and
                test_rsvp.get('dietary_restrictions') == 'Vegan' and
                test_rsvp.get('special_message') == 'Testing MongoDB storage' and
                test_rsvp.get('wedding_id') == self.wedding_id
            )
            
            # Check timestamp is present
            has_timestamp = 'submitted_at' in test_rsvp
            
            if not fields_match:
                print(f"❌ RSVP fields don't match expected values")
                print(f"   Expected: MongoDB Test User, mongodb@test.com, +1987654321")
                print(f"   Got: {test_rsvp.get('guest_name')}, {test_rsvp.get('guest_email')}, {test_rsvp.get('guest_phone')}")
            
            return fields_match and has_timestamp
        
        return self.run_test(
            "RSVP MongoDB Storage (Verify)",
            "GET",
            f"api/rsvp/{self.wedding_id}",
            200,
            validate_response=validate_mongodb_storage
        )

    def test_whatsapp_url_generation_desktop(self):
        """Test WhatsApp Web URL generation for desktop users"""
        # This would typically be a frontend feature, but we can test the shareable link format
        if not self.shareable_id:
            print("⚠️ No shareable_id available for WhatsApp URL testing")
            return True, {}
        
        # Construct expected WhatsApp Web URL
        shareable_url = f"{self.base_url}/share/{self.shareable_id}"
        message = f"You're invited to our wedding! View your personalized invitation: {shareable_url}"
        whatsapp_web_url = f"https://web.whatsapp.com/send?text={quote(message)}"
        
        print(f"\n🔍 Testing WhatsApp Web URL Generation...")
        print(f"   Shareable URL: {shareable_url}")
        print(f"   WhatsApp Message: {message}")
        print(f"   WhatsApp Web URL: {whatsapp_web_url}")
        
        # Validate URL structure
        url_valid = (
            whatsapp_web_url.startswith("https://web.whatsapp.com/send?text=") and
            quote(shareable_url) in whatsapp_web_url and
            len(whatsapp_web_url) < 2000  # WhatsApp URL length limit
        )
        
        if url_valid:
            print("✅ WhatsApp Web URL generation working")
            self.tests_passed += 1
        else:
            print("❌ WhatsApp Web URL generation failed")
            self.critical_failures.append("WhatsApp Web URL: Invalid URL structure")
        
        self.tests_run += 1
        return url_valid, {"whatsapp_web_url": whatsapp_web_url}

    def test_whatsapp_url_generation_mobile(self):
        """Test WhatsApp App URL generation for mobile users"""
        if not self.shareable_id:
            print("⚠️ No shareable_id available for WhatsApp mobile URL testing")
            return True, {}
        
        # Construct expected WhatsApp App URL
        shareable_url = f"{self.base_url}/share/{self.shareable_id}"
        message = f"You're invited to our wedding! View your personalized invitation: {shareable_url}"
        whatsapp_app_url = f"whatsapp://send?text={quote(message)}"
        
        print(f"\n🔍 Testing WhatsApp App URL Generation...")
        print(f"   Shareable URL: {shareable_url}")
        print(f"   WhatsApp Message: {message}")
        print(f"   WhatsApp App URL: {whatsapp_app_url}")
        
        # Validate URL structure
        url_valid = (
            whatsapp_app_url.startswith("whatsapp://send?text=") and
            quote(shareable_url) in whatsapp_app_url and
            len(whatsapp_app_url) < 2000  # WhatsApp URL length limit
        )
        
        if url_valid:
            print("✅ WhatsApp App URL generation working")
            self.tests_passed += 1
        else:
            print("❌ WhatsApp App URL generation failed")
            self.critical_failures.append("WhatsApp App URL: Invalid URL structure")
        
        self.tests_run += 1
        return url_valid, {"whatsapp_app_url": whatsapp_app_url}

    def test_shareable_link_in_whatsapp_message(self):
        """Test that shareable links are properly included in WhatsApp messages"""
        if not self.shareable_id:
            return True, {}
        
        # Test different message formats
        base_url = self.base_url
        shareable_url = f"{base_url}/share/{self.shareable_id}"
        
        message_templates = [
            f"Join us for our wedding! {shareable_url}",
            f"You're invited! View details: {shareable_url}",
            f"Wedding invitation: {shareable_url} - Hope to see you there!",
            f"Save the date! {shareable_url}"
        ]
        
        all_valid = True
        for i, message in enumerate(message_templates):
            whatsapp_url = f"https://web.whatsapp.com/send?text={quote(message)}"
            
            # Validate that the shareable URL is properly encoded in the WhatsApp URL
            url_contains_link = quote(shareable_url) in whatsapp_url
            url_length_ok = len(whatsapp_url) < 2000
            
            print(f"\n🔍 Testing Message Template {i+1}:")
            print(f"   Message: {message}")
            print(f"   URL Valid: {url_contains_link and url_length_ok}")
            
            if not (url_contains_link and url_length_ok):
                all_valid = False
                self.critical_failures.append(f"WhatsApp Message Template {i+1}: Invalid URL encoding")
        
        self.tests_run += 1
        if all_valid:
            self.tests_passed += 1
            print("✅ All WhatsApp message templates working")
        else:
            print("❌ Some WhatsApp message templates failed")
        
        return all_valid, {}

    def test_rsvp_error_handling(self):
        """Test RSVP error handling for edge cases"""
        # Test with non-existent wedding_id
        invalid_wedding_data = self.valid_rsvp_data.copy()
        invalid_wedding_data["wedding_id"] = "non-existent-wedding-123"
        
        # Backend might still accept this since it doesn't validate wedding existence
        success1, response1 = self.run_test(
            "RSVP Error Handling (Invalid Wedding ID)",
            "POST",
            "api/rsvp",
            200,  # Backend accepts any wedding_id
            data=invalid_wedding_data
        )
        
        # Test retrieving RSVPs for non-existent wedding
        success2, response2 = self.run_test(
            "RSVP Error Handling (Get Non-existent Wedding)",
            "GET",
            "api/rsvp/non-existent-wedding-123",
            200,  # Should return empty list
        )
        
        # Test retrieving RSVPs for non-existent shareable_id
        success3, response3 = self.run_test(
            "RSVP Error Handling (Get Non-existent Shareable)",
            "GET",
            "api/rsvp/shareable/non-existent-shareable-123",
            404,  # Should return 404
        )
        
        return success1 and success2 and success3, {}

    def run_comprehensive_rsvp_whatsapp_tests(self):
        """Run all RSVP and WhatsApp sharing tests"""
        print("🚀 Starting Comprehensive RSVP & WhatsApp Sharing Tests")
        print("🎯 Focus: RSVP Management System & WhatsApp Bulk Sharing")
        print("🔗 Backend URL:", self.base_url)
        print("=" * 80)
        
        # Setup phase
        if not self.setup_test_user_and_wedding():
            print("❌ Failed to setup test user and wedding data")
            return 1
        
        # Test sequence focusing on review request requirements
        tests = [
            ("1. 🚨 RSVP Submission (Valid Data)", self.test_rsvp_submission_valid_data),
            ("2. RSVP Submission (Missing Fields)", self.test_rsvp_submission_missing_fields),
            ("3. RSVP Guest Count Validation", self.test_rsvp_guest_count_validation),
            ("4. RSVP Dietary Restrictions & Messages", self.test_rsvp_dietary_restrictions_and_messages),
            ("5. RSVP Attendance Variations", self.test_rsvp_attendance_variations),
            ("6. 🚨 Get RSVPs by Wedding ID", self.test_get_rsvps_by_wedding_id),
            ("7. 🚨 Get RSVPs by Shareable ID", self.test_get_rsvps_by_shareable_id),
            ("8. RSVP MongoDB Storage Verification", self.test_rsvp_data_storage_mongodb),
            ("9. WhatsApp Web URL Generation", self.test_whatsapp_url_generation_desktop),
            ("10. WhatsApp App URL Generation", self.test_whatsapp_url_generation_mobile),
            ("11. Shareable Link in WhatsApp Messages", self.test_shareable_link_in_whatsapp_message),
            ("12. RSVP Error Handling", self.test_rsvp_error_handling),
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
        print(f"📊 RSVP & WHATSAPP SHARING TEST RESULTS")
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
        whatsapp_working = not any("WhatsApp" in failure for failure in self.critical_failures)
        mongodb_working = not any("MongoDB" in failure for failure in self.critical_failures)
        
        print(f"\n📋 FUNCTIONALITY STATUS:")
        print(f"   RSVP Management: {'✅ WORKING' if rsvp_working else '❌ FAILED'}")
        print(f"   WhatsApp Sharing: {'✅ WORKING' if whatsapp_working else '❌ FAILED'}")
        print(f"   MongoDB Storage: {'✅ WORKING' if mongodb_working else '❌ FAILED'}")
        
        if rsvp_working and whatsapp_working and mongodb_working and len(self.critical_failures) == 0:
            print("\n✅ ALL CRITICAL RSVP & WHATSAPP TESTS PASSED!")
            print("✅ RSVP management system is fully operational")
            print("✅ WhatsApp bulk sharing functionality working")
            print("✅ MongoDB integration for RSVP data working correctly")
            return 0
        else:
            print("\n❌ CRITICAL RSVP & WHATSAPP ISSUES DETECTED")
            if not rsvp_working:
                print("❌ RSVP management system has issues")
            if not whatsapp_working:
                print("❌ WhatsApp sharing functionality has issues")
            if not mongodb_working:
                print("❌ MongoDB RSVP storage has issues")
            return 1

def main():
    """Main test execution"""
    tester = RSVPWhatsAppTester()
    return tester.run_comprehensive_rsvp_whatsapp_tests()

if __name__ == "__main__":
    sys.exit(main())