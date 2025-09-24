import requests
import sys
import json
from datetime import datetime
import uuid

class FocusedWeddingAPITester:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url
        self.session_id = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.critical_failures = []
        self.minor_issues = []

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=10)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                    self.critical_failures.append(f"{name}: HTTP {response.status_code} - {error_data.get('detail', 'Unknown error')}")
                except:
                    print(f"   Error: {response.text}")
                    self.critical_failures.append(f"{name}: HTTP {response.status_code} - {response.text[:100]}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.critical_failures.append(f"{name}: Connection error - {str(e)}")
            return False, {}

    def test_known_user_login(self):
        """Test login with known working user: basudev/test123"""
        success, response = self.run_test(
            "Known User Login (basudev)",
            "POST",
            "api/auth/login",
            200,
            data={"username": "basudev", "password": "test123"}
        )
        if success and 'session_id' in response:
            self.session_id = response['session_id']
            self.user_id = response['user_id']
            print(f"   Session ID: {self.session_id}")
            return True
        return False

    def test_known_shareable_url(self):
        """Test the known working shareable URL: ed1173aa"""
        success, response = self.run_test(
            "Known Shareable URL (ed1173aa)",
            "GET",
            "api/wedding/share/ed1173aa",
            200
        )
        
        if success and response:
            couple1 = response.get('couple_name_1', '')
            couple2 = response.get('couple_name_2', '')
            venue = response.get('venue_location', '')
            
            print(f"   Couple: {couple1} & {couple2}")
            print(f"   Venue: {venue}")
            
            if couple1 == "Basu" and couple2 == "Shreya" and "Mumbai, India" in venue:
                print("✅ Correct personalized data found!")
                return True
            else:
                print("❌ Expected 'Basu & Shreya' with Mumbai venue")
                self.critical_failures.append("Known shareable URL not showing correct personalized data")
                return False
        return success

    def test_invalid_shareable_url(self):
        """Test invalid shareable URL (should return default template)"""
        invalid_id = "invalid123"
        success, response = self.run_test(
            f"Invalid Shareable URL ({invalid_id})",
            "GET",
            f"api/wedding/share/{invalid_id}",
            200
        )
        
        if success and response:
            couple1 = response.get('couple_name_1', '')
            couple2 = response.get('couple_name_2', '')
            
            print(f"   Default Couple: {couple1} & {couple2}")
            
            if couple1 == "Sarah" and couple2 == "Michael":
                print("✅ Correct default template returned!")
                return True
            else:
                print("❌ Expected default 'Sarah & Michael' template")
                self.critical_failures.append("Invalid shareable URL not returning default template")
                return False
        return success

    def test_get_wedding_data(self):
        """Test getting wedding data for logged in user"""
        if not self.session_id:
            print("❌ No session ID available")
            self.critical_failures.append("Get Wedding Data: No session available")
            return False, {}
            
        success, response = self.run_test(
            "Get Wedding Data",
            "GET",
            "api/wedding",
            200,
            params={"session_id": self.session_id}
        )
        
        if success and response:
            shareable_id = response.get('shareable_id', 'Not found')
            couple1 = response.get('couple_name_1', '')
            couple2 = response.get('couple_name_2', '')
            print(f"   Shareable ID: {shareable_id}")
            print(f"   Couple: {couple1} & {couple2}")
            
        return success, response

    def test_update_wedding_data(self):
        """Test updating wedding data"""
        if not self.session_id:
            print("❌ No session ID available")
            self.critical_failures.append("Update Wedding Data: No session available")
            return False, {}

        wedding_data = {
            "session_id": self.session_id,
            "couple_name_1": "Basu",
            "couple_name_2": "Shreya",
            "wedding_date": "2025-08-15",
            "venue_name": "Updated Grand Palace",
            "venue_location": "Mumbai, India - Updated",
            "their_story": "Our updated beautiful love story...",
            "theme": "modern"
        }
        
        success, response = self.run_test(
            "Update Wedding Data",
            "PUT",
            "api/wedding",
            200,
            data=wedding_data
        )
        
        if success and response:
            shareable_id = response.get('shareable_id', 'Not found')
            print(f"   Updated Shareable ID: {shareable_id}")
            
        return success, response

    def test_shareable_url_after_update(self, wedding_data):
        """Test shareable URL reflects updates"""
        if not wedding_data or 'shareable_id' not in wedding_data:
            print("❌ No shareable_id found in wedding data")
            self.critical_failures.append("Shareable URL After Update: No shareable_id available")
            return False
            
        shareable_id = wedding_data['shareable_id']
        success, response = self.run_test(
            f"Shareable URL After Update ({shareable_id})",
            "GET",
            f"api/wedding/share/{shareable_id}",
            200
        )
        
        if success and response:
            couple1 = response.get('couple_name_1', '')
            couple2 = response.get('couple_name_2', '')
            venue = response.get('venue_location', '')
            story = response.get('their_story', '')
            
            print(f"   Updated Couple: {couple1} & {couple2}")
            print(f"   Updated Venue: {venue}")
            
            if couple1 == "Basu" and couple2 == "Shreya" and "Updated" in venue:
                print("✅ Updated data correctly reflected in shareable URL!")
                return True
            else:
                print("❌ Updated data not reflected in shareable URL")
                self.critical_failures.append("Shareable URL not reflecting updates")
                return False
        return success

    def test_backend_connectivity(self):
        """Test basic backend connectivity"""
        success, response = self.run_test(
            "Backend Connectivity",
            "GET",
            "api/test",
            200
        )
        return success

def main():
    print("🚀 Starting Focused Wedding Card API Tests...")
    print("🎯 Focus: Shareable URL functionality and user flow")
    print("=" * 60)
    
    tester = FocusedWeddingAPITester()
    
    # Test 1: Backend connectivity
    if not tester.test_backend_connectivity():
        print("\n❌ Backend connectivity failed. Stopping tests.")
        return 1
    
    # Test 2: Known shareable URL (main reported issue)
    print("\n" + "="*50)
    print("🚨 CRITICAL TEST: Known Shareable URL")
    print("="*50)
    tester.test_known_shareable_url()
    
    # Test 3: Invalid shareable URL (should show default)
    tester.test_invalid_shareable_url()
    
    # Test 4: User login with known credentials
    print("\n" + "="*50)
    print("🔑 USER FLOW TESTING")
    print("="*50)
    if not tester.test_known_user_login():
        print("⚠️ Known user login failed, trying to continue with other tests...")
    
    # Test 5: Get wedding data
    success, wedding_data = tester.test_get_wedding_data()
    
    # Test 6: Update wedding data
    success, updated_wedding_data = tester.test_update_wedding_data()
    
    # Test 7: Test shareable URL after update
    if updated_wedding_data:
        tester.test_shareable_url_after_update(updated_wedding_data)
    
    # Print final results
    print("\n" + "=" * 60)
    print(f"📊 FINAL RESULTS:")
    print(f"   Tests Run: {tester.tests_run}")
    print(f"   Tests Passed: {tester.tests_passed}")
    print(f"   Success Rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    
    if tester.critical_failures:
        print(f"\n🚨 CRITICAL FAILURES ({len(tester.critical_failures)}):")
        for failure in tester.critical_failures:
            print(f"   ❌ {failure}")
    
    if tester.minor_issues:
        print(f"\n⚠️ MINOR ISSUES ({len(tester.minor_issues)}):")
        for issue in tester.minor_issues:
            print(f"   ⚠️ {issue}")
    
    # Determine overall result
    shareable_url_working = not any("shareable" in failure.lower() for failure in tester.critical_failures)
    
    if shareable_url_working and len(tester.critical_failures) == 0:
        print("\n✅ ALL CRITICAL TESTS PASSED!")
        print("✅ Shareable URL functionality is working correctly")
        return 0
    elif shareable_url_working:
        print("\n⚠️ SHAREABLE URL WORKING, but some other issues detected")
        return 0
    else:
        print("\n❌ CRITICAL SHAREABLE URL ISSUES DETECTED")
        return 1

if __name__ == "__main__":
    sys.exit(main())