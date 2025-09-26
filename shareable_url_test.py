import requests
import sys
import json
from datetime import datetime
import time
import uuid

class ShareableURLTester:
    def __init__(self, base_url="http://localhost:8001"):
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

    def test_new_user_registration(self):
        """Test registration with a unique username"""
        # Generate unique username to avoid conflicts
        unique_id = str(uuid.uuid4())[:8]
        self.test_username = f"sharetest_{unique_id}"
        
        test_data = {
            "username": self.test_username,
            "password": "testpass123"
        }
        
        def validate_registration(response_data):
            required_fields = ['session_id', 'user_id', 'username', 'success']
            return all(field in response_data for field in required_fields) and response_data.get('success') is True
        
        success, response = self.run_test(
            "New User Registration for Shareable URL Test",
            "POST",
            "api/auth/register",
            200,
            data=test_data,
            validate_response=validate_registration
        )
        
        if success and response:
            self.session_id = response.get('session_id')
            self.user_id = response.get('user_id')
            print(f"   ✅ Stored session_id: {self.session_id}")
            print(f"   ✅ Stored user_id: {self.user_id}")
            print(f"   ✅ Test username: {self.test_username}")
                
        return success, response

    def test_get_default_wedding_data(self):
        """Test getting default wedding data (should have shareable_id)"""
        if not self.session_id:
            self.critical_failures.append("Wedding Retrieval: No session_id available")
            return False, {}
            
        def validate_default_data(response_data):
            # Should have default data and a shareable_id
            has_shareable_id = 'shareable_id' in response_data
            has_default_data = (response_data.get('couple_name_1') == 'Sarah' and 
                               response_data.get('couple_name_2') == 'Michael')
            
            if not has_shareable_id:
                print(f"❌ Missing shareable_id in response")
            if not has_default_data:
                print(f"❌ Missing default wedding data")
                
            return has_shareable_id and has_default_data
        
        success, response = self.run_test(
            "Get Default Wedding Data (with shareable_id)",
            "GET",
            "api/wedding",
            200,
            params={"session_id": self.session_id},
            validate_response=validate_default_data
        )
        
        if success and response:
            self.wedding_id = response.get('id')
            self.shareable_id = response.get('shareable_id')
            print(f"   ✅ Wedding ID: {self.wedding_id}")
            print(f"   ✅ Shareable ID: {self.shareable_id}")
            print(f"   ✅ Shareable ID Length: {len(self.shareable_id) if self.shareable_id else 'None'}")
            
        return success, response

    def test_8_character_shareable_id_system(self):
        """CRITICAL TEST: Verify 8-character shareable ID system"""
        if not self.shareable_id:
            self.critical_failures.append("8-Character ID Test: No shareable_id available")
            return False, {}
        
        def validate_8_char_system(response_data):
            # Verify shareable_id is exactly 8 characters
            shareable_id = response_data.get('shareable_id')
            if not shareable_id:
                print(f"❌ No shareable_id in response")
                return False
            
            if len(shareable_id) != 8:
                print(f"❌ Shareable ID length is {len(shareable_id)}, expected 8")
                return False
            
            # Verify no custom_url field exists (legacy system removed)
            if 'custom_url' in response_data:
                print(f"❌ Legacy custom_url field still present")
                return False
                
            print(f"✅ Shareable ID is exactly 8 characters: {shareable_id}")
            return True
        
        return self.run_test(
            "🚨 CRITICAL: 8-Character Shareable ID System",
            "GET",
            "api/wedding",
            200,
            params={"session_id": self.session_id},
            validate_response=validate_8_char_system
        )

    def test_shareable_url_endpoint_default_data(self):
        """Test shareable URL endpoint with default data"""
        if not self.shareable_id:
            self.critical_failures.append("Shareable URL Test: No shareable_id available")
            return False, {}
        
        def validate_shareable_endpoint(response_data):
            # Should return the same data as the wedding endpoint but without sensitive fields
            has_couple_data = (response_data.get('couple_name_1') == 'Sarah' and 
                              response_data.get('couple_name_2') == 'Michael')
            has_venue_data = response_data.get('venue_name') == 'Sunset Garden Estate'
            no_sensitive_data = 'user_id' not in response_data and '_id' not in response_data
            
            if not has_couple_data:
                print(f"❌ Missing or incorrect couple data")
            if not has_venue_data:
                print(f"❌ Missing or incorrect venue data")
            if not no_sensitive_data:
                print(f"❌ Sensitive data exposed in public endpoint")
                
            return has_couple_data and has_venue_data and no_sensitive_data
        
        return self.run_test(
            "Shareable URL Endpoint (/api/wedding/share/{shareable_id}) - Default Data",
            "GET",
            f"api/wedding/share/{self.shareable_id}",
            200,
            validate_response=validate_shareable_endpoint
        )

    def test_update_wedding_with_personalized_data(self):
        """Update wedding data with personalized information"""
        if not self.session_id:
            return False, {}
            
        updated_data = {
            "session_id": self.session_id,
            "couple_name_1": "Alice",
            "couple_name_2": "Bob",
            "wedding_date": "2025-12-25",
            "venue_name": "Mountain View Resort",
            "venue_location": "Mountain View Resort • Colorado Springs, Colorado",
            "their_story": "Alice and Bob met at a coding bootcamp and fell in love over debugging sessions. Their wedding will be a celebration of love, technology, and endless possibilities.",
            "theme": "modern"
        }
        
        def validate_update(response_data):
            return (response_data.get('couple_name_1') == 'Alice' and
                   response_data.get('couple_name_2') == 'Bob' and
                   response_data.get('venue_name') == 'Mountain View Resort' and
                   response_data.get('theme') == 'modern')
        
        success, response = self.run_test(
            "Update Wedding with Personalized Data",
            "PUT",
            "api/wedding",
            200,
            data=updated_data,
            validate_response=validate_update
        )
        
        return success, response

    def test_shareable_url_personalized_data(self):
        """CRITICAL TEST: Verify shareable URL shows personalized data (not fallback)"""
        if not self.shareable_id:
            self.critical_failures.append("Personalized Shareable URL Test: No shareable_id available")
            return False, {}
        
        def validate_personalized_data(response_data):
            # Should show Alice & Bob, NOT Sarah & Michael (fallback data)
            is_personalized = (response_data.get('couple_name_1') == 'Alice' and 
                              response_data.get('couple_name_2') == 'Bob' and
                              response_data.get('venue_name') == 'Mountain View Resort')
            
            is_not_fallback = not (response_data.get('couple_name_1') == 'Sarah' and 
                                  response_data.get('couple_name_2') == 'Michael')
            
            if not is_personalized:
                print(f"❌ CRITICAL FAILURE: Shareable URL not showing personalized data!")
                print(f"   Expected: Alice & Bob, Mountain View Resort")
                print(f"   Got: {response_data.get('couple_name_1')} & {response_data.get('couple_name_2')}, {response_data.get('venue_name')}")
            
            if not is_not_fallback:
                print(f"❌ CRITICAL FAILURE: Shareable URL showing fallback Sarah & Michael data!")
            
            return is_personalized and is_not_fallback
        
        success, response = self.run_test(
            "🚨 CRITICAL: Shareable URL Shows Personalized Data (NOT Fallback)",
            "GET",
            f"api/wedding/share/{self.shareable_id}",
            200,
            validate_response=validate_personalized_data
        )
        
        if success and response:
            print(f"   ✅ PERSONALIZED SHAREABLE URL WORKING!")
            print(f"   ✅ Shows: {response.get('couple_name_1')} & {response.get('couple_name_2')}")
            print(f"   ✅ Venue: {response.get('venue_name')}")
            print(f"   ✅ Date: {response.get('wedding_date')}")
        
        return success, response

    def test_invalid_shareable_id_fallback(self):
        """Test that invalid shareable IDs return fallback data"""
        invalid_id = "invalid1"  # 8 characters but doesn't exist
        
        def validate_fallback_data(response_data):
            # Should return enhanced default data for invalid IDs
            is_fallback = (response_data.get('couple_name_1') == 'Sarah' and 
                          response_data.get('couple_name_2') == 'Michael' and
                          response_data.get('venue_name') == 'Sunset Garden Estate')
            
            has_requested_id = response_data.get('shareable_id') == invalid_id
            
            if not is_fallback:
                print(f"❌ Invalid ID should return fallback data")
            if not has_requested_id:
                print(f"❌ Response should include the requested shareable_id")
                
            return is_fallback and has_requested_id
        
        return self.run_test(
            "Invalid Shareable ID Returns Fallback Data",
            "GET",
            f"api/wedding/share/{invalid_id}",
            200,
            validate_response=validate_fallback_data
        )

    def test_legacy_custom_url_removed(self):
        """Test that legacy custom_url system is completely removed"""
        # Try to access with a custom URL format (should not work)
        legacy_url = "alice-bob-wedding"
        
        # This should return fallback data since custom_url system is removed
        def validate_legacy_removed(response_data):
            # Should return fallback data, not personalized data
            is_fallback = (response_data.get('couple_name_1') == 'Sarah' and 
                          response_data.get('couple_name_2') == 'Michael')
            return is_fallback
        
        return self.run_test(
            "Legacy custom_url System Removed",
            "GET",
            f"api/wedding/share/{legacy_url}",
            200,
            validate_response=validate_legacy_removed
        )

    def run_shareable_url_tests(self):
        """Run comprehensive shareable URL system tests"""
        print("🚀 Starting Shareable URL System Tests")
        print("🎯 Focus: 8-Character Shareable ID System & Personalization")
        print("=" * 80)
        
        # Test sequence focusing on shareable URL functionality
        tests = [
            ("New User Registration", self.test_new_user_registration),
            ("Get Default Wedding Data", self.test_get_default_wedding_data),
            ("🚨 8-Character Shareable ID System", self.test_8_character_shareable_id_system),
            ("Shareable URL Endpoint - Default Data", self.test_shareable_url_endpoint_default_data),
            ("Update Wedding with Personalized Data", self.test_update_wedding_with_personalized_data),
            ("🚨 Shareable URL Personalization", self.test_shareable_url_personalized_data),
            ("Invalid Shareable ID Fallback", self.test_invalid_shareable_id_fallback),
            ("Legacy custom_url System Removed", self.test_legacy_custom_url_removed)
        ]
        
        print(f"\n📋 Running {len(tests)} shareable URL test scenarios...")
        
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
        
        # Print comprehensive results
        print("\n" + "=" * 80)
        print(f"📊 SHAREABLE URL SYSTEM TEST RESULTS")
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
        
        # Determine overall result
        critical_tests_passed = not any("Shareable URL Personalization" in failure for failure in self.critical_failures)
        shareable_id_system_working = not any("8-Character" in failure for failure in self.critical_failures)
        
        if critical_tests_passed and shareable_id_system_working and len(self.critical_failures) == 0:
            print("\n✅ ALL CRITICAL SHAREABLE URL TESTS PASSED!")
            print("✅ 8-character shareable ID system is working correctly")
            print("✅ Shareable URL personalization is working correctly")
            print("✅ Legacy custom_url system has been removed")
            return 0
        else:
            print("\n❌ CRITICAL SHAREABLE URL SYSTEM ISSUES DETECTED")
            if not critical_tests_passed:
                print("❌ Shareable URL personalization has issues")
            if not shareable_id_system_working:
                print("❌ 8-character shareable ID system has issues")
            return 1

def main():
    """Main test execution"""
    tester = ShareableURLTester()
    return tester.run_shareable_url_tests()

if __name__ == "__main__":
    sys.exit(main())