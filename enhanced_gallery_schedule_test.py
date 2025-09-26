import requests
import sys
import json
from datetime import datetime
import time
import os
import uuid

class EnhancedGalleryScheduleTester:
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
        self.critical_failures = []
        self.minor_issues = []
        
        # Test user credentials as specified in review request
        self.test_username = "gallerytester2025"
        self.test_password = "test123456"
        
        # Enhanced gallery test data
        self.test_gallery_photos = [
            {
                "id": str(uuid.uuid4()),
                "url": "https://images.unsplash.com/photo-1606216794074-735e91aa2c92?w=500",
                "title": "Engagement Photoshoot",
                "description": "Our beautiful engagement photos at the beach during sunset",
                "category": "engagement",
                "eventMessage": "The moment we knew we were meant to be together forever"
            },
            {
                "id": str(uuid.uuid4()),
                "url": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=500",
                "title": "Mountain Adventure",
                "description": "Hiking together in the beautiful mountains",
                "category": "travels",
                "eventMessage": "Adventures are better when shared with your best friend"
            },
            {
                "id": str(uuid.uuid4()),
                "url": "https://images.unsplash.com/photo-1511895426328-dc8714191300?w=500",
                "title": "Family Gathering",
                "description": "Celebrating with our families during the holidays",
                "category": "family",
                "eventMessage": "Family is where love begins and never ends"
            },
            {
                "id": str(uuid.uuid4()),
                "url": "https://images.unsplash.com/photo-1515934751635-c81c6bc9a2d8?w=500",
                "title": "Friends Night Out",
                "description": "Fun times with our closest friends",
                "category": "friends",
                "eventMessage": "Good friends make the best memories"
            }
        ]
        
        # Enhanced schedule test data
        self.test_schedule_events = [
            {
                "id": str(uuid.uuid4()),
                "time": "2:00 PM",
                "title": "Wedding Ceremony",
                "description": "Join us as we exchange vows in the beautiful garden pavilion",
                "location": "Garden Pavilion at Sunset Estate",
                "duration": "45 minutes",
                "date": "2025-06-15",
                "highlight": True
            },
            {
                "id": str(uuid.uuid4()),
                "time": "3:00 PM",
                "title": "Cocktail Hour",
                "description": "Celebrate with drinks and appetizers on the terrace",
                "location": "Sunset Terrace",
                "duration": "60 minutes",
                "date": "2025-06-15",
                "highlight": False
            },
            {
                "id": str(uuid.uuid4()),
                "time": "4:30 PM",
                "title": "Reception Dinner",
                "description": "Dinner, dancing, and celebration in the grand ballroom",
                "location": "Grand Ballroom",
                "duration": "4 hours",
                "date": "2025-06-15",
                "highlight": True
            }
        ]
        
        # Important info test data
        self.test_important_info = {
            "dress_code": {
                "title": "Dress Code",
                "description": "Formal attire requested. Ladies, please consider comfortable shoes for outdoor ceremony.",
                "enabled": True
            },
            "parking": {
                "title": "Parking Information",
                "description": "Complimentary valet parking available at the main entrance.",
                "enabled": True
            },
            "accommodations": {
                "title": "Hotel Accommodations",
                "description": "We have reserved blocks at nearby hotels. Please see our website for details.",
                "enabled": True
            }
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

    def test_user_registration(self):
        """Test user registration with specified test credentials"""
        test_data = {
            "username": self.test_username,
            "password": self.test_password
        }
        
        def validate_registration(response_data):
            required_fields = ['session_id', 'user_id', 'username', 'success']
            return all(field in response_data for field in required_fields) and response_data.get('success') is True
        
        success, response = self.run_test(
            "User Registration (gallerytester2025)",
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
                
        return success, response

    def test_user_login(self):
        """Test user login with specified test credentials"""
        test_data = {
            "username": self.test_username,
            "password": self.test_password
        }
        
        def validate_login(response_data):
            return (response_data.get('username') == self.test_username and 
                   response_data.get('success') is True and
                   'session_id' in response_data)
        
        success, response = self.run_test(
            "User Login (gallerytester2025)",
            "POST",
            "api/auth/login",
            200,
            data=test_data,
            validate_response=validate_login
        )
        
        if success and response:
            self.session_id = response.get('session_id')
            self.user_id = response.get('user_id')
            print(f"   ✅ Updated session_id: {self.session_id}")
            print(f"   ✅ Updated user_id: {self.user_id}")
                
        return success, response

    def test_wedding_data_retrieval(self):
        """Test wedding data retrieval for authenticated user"""
        if not self.session_id:
            self.critical_failures.append("Wedding Retrieval: No session_id available")
            return False, {}
            
        def validate_retrieval(response_data):
            # Should have default data initially
            required_fields = ['couple_name_1', 'couple_name_2', 'venue_name', 'gallery_photos', 'schedule_events']
            return all(field in response_data for field in required_fields)
        
        success, response = self.run_test(
            "Wedding Data Retrieval",
            "GET",
            "api/wedding",
            200,
            params={"session_id": self.session_id},
            validate_response=validate_retrieval
        )
        
        if success and response:
            self.wedding_id = response.get('id')
            print(f"   ✅ Wedding ID: {self.wedding_id}")
            print(f"   ✅ Current gallery_photos: {len(response.get('gallery_photos', []))}")
            print(f"   ✅ Current schedule_events: {len(response.get('schedule_events', []))}")
            
        return success, response

    def test_enhanced_gallery_photos_save(self):
        """Test saving enhanced gallery photos with new structure"""
        if not self.session_id:
            self.critical_failures.append("Gallery Photos Save: No session_id available")
            return False, {}
            
        updated_data = {
            "session_id": self.session_id,
            "couple_name_1": "Gallery",
            "couple_name_2": "Tester",
            "wedding_date": "2025-06-15",
            "venue_name": "Test Venue",
            "venue_location": "Test Location",
            "their_story": "Our test story",
            "gallery_photos": self.test_gallery_photos
        }
        
        def validate_gallery_save(response_data):
            gallery_photos = response_data.get('gallery_photos', [])
            
            # Validate structure and content
            if len(gallery_photos) != 4:
                print(f"❌ Expected 4 gallery photos, got {len(gallery_photos)}")
                return False
            
            # Check each photo has required fields
            required_fields = ['id', 'url', 'title', 'description', 'category', 'eventMessage']
            for i, photo in enumerate(gallery_photos):
                missing_fields = [field for field in required_fields if field not in photo]
                if missing_fields:
                    print(f"❌ Photo {i+1} missing fields: {missing_fields}")
                    return False
            
            # Check categories are correct
            categories = [photo.get('category') for photo in gallery_photos]
            expected_categories = ['engagement', 'travels', 'family', 'friends']
            if not all(cat in expected_categories for cat in categories):
                print(f"❌ Invalid categories found: {categories}")
                return False
            
            print(f"✅ Gallery photos structure validated: {len(gallery_photos)} photos")
            print(f"✅ Categories: {categories}")
            return True
        
        success, response = self.run_test(
            "🚨 CRITICAL: Enhanced Gallery Photos Save",
            "PUT",
            "api/wedding",
            200,
            data=updated_data,
            validate_response=validate_gallery_save
        )
        
        if success and response:
            print(f"   ✅ Gallery photos saved successfully")
            for i, photo in enumerate(response.get('gallery_photos', [])):
                print(f"   ✅ Photo {i+1}: {photo.get('title')} ({photo.get('category')})")
            
        return success, response

    def test_enhanced_schedule_events_save(self):
        """Test saving enhanced schedule events with new structure"""
        if not self.session_id:
            self.critical_failures.append("Schedule Events Save: No session_id available")
            return False, {}
            
        updated_data = {
            "session_id": self.session_id,
            "couple_name_1": "Gallery",
            "couple_name_2": "Tester",
            "wedding_date": "2025-06-15",
            "venue_name": "Test Venue",
            "venue_location": "Test Location",
            "their_story": "Our test story",
            "schedule_events": self.test_schedule_events,
            "important_info": self.test_important_info
        }
        
        def validate_schedule_save(response_data):
            schedule_events = response_data.get('schedule_events', [])
            important_info = response_data.get('important_info', {})
            
            # Validate schedule events structure
            if len(schedule_events) != 3:
                print(f"❌ Expected 3 schedule events, got {len(schedule_events)}")
                return False
            
            # Check each event has required fields
            required_fields = ['id', 'time', 'title', 'description', 'location', 'duration', 'date', 'highlight']
            for i, event in enumerate(schedule_events):
                missing_fields = [field for field in required_fields if field not in event]
                if missing_fields:
                    print(f"❌ Event {i+1} missing fields: {missing_fields}")
                    return False
                
                # Validate date format
                if event.get('date') != '2025-06-15':
                    print(f"❌ Event {i+1} has incorrect date: {event.get('date')}")
                    return False
                
                # Validate highlight field is boolean
                if not isinstance(event.get('highlight'), bool):
                    print(f"❌ Event {i+1} highlight field is not boolean: {event.get('highlight')}")
                    return False
            
            # Validate important_info structure
            if not important_info:
                print(f"❌ Important info is missing or empty")
                return False
            
            expected_info_keys = ['dress_code', 'parking', 'accommodations']
            for key in expected_info_keys:
                if key not in important_info:
                    print(f"❌ Important info missing key: {key}")
                    return False
                
                info_item = important_info[key]
                if not all(field in info_item for field in ['title', 'description', 'enabled']):
                    print(f"❌ Important info {key} missing required fields")
                    return False
            
            print(f"✅ Schedule events structure validated: {len(schedule_events)} events")
            print(f"✅ Important info validated: {len(important_info)} items")
            return True
        
        success, response = self.run_test(
            "🚨 CRITICAL: Enhanced Schedule Events Save",
            "PUT",
            "api/wedding",
            200,
            data=updated_data,
            validate_response=validate_schedule_save
        )
        
        if success and response:
            print(f"   ✅ Schedule events saved successfully")
            for i, event in enumerate(response.get('schedule_events', [])):
                print(f"   ✅ Event {i+1}: {event.get('title')} at {event.get('time')} (Highlight: {event.get('highlight')})")
            
            print(f"   ✅ Important info saved successfully")
            for key, info in response.get('important_info', {}).items():
                print(f"   ✅ Info: {info.get('title')} (Enabled: {info.get('enabled')})")
            
        return success, response

    def test_data_persistence(self):
        """Test that enhanced gallery and schedule data persists correctly"""
        if not self.session_id:
            self.critical_failures.append("Data Persistence: No session_id available")
            return False, {}
            
        def validate_persistence(response_data):
            gallery_photos = response_data.get('gallery_photos', [])
            schedule_events = response_data.get('schedule_events', [])
            important_info = response_data.get('important_info', {})
            
            # Validate gallery persistence
            gallery_valid = (
                len(gallery_photos) == 4 and
                any(photo.get('category') == 'engagement' for photo in gallery_photos) and
                any(photo.get('category') == 'travels' for photo in gallery_photos) and
                any(photo.get('category') == 'family' for photo in gallery_photos) and
                any(photo.get('category') == 'friends' for photo in gallery_photos) and
                all('eventMessage' in photo for photo in gallery_photos)
            )
            
            # Validate schedule persistence
            schedule_valid = (
                len(schedule_events) == 3 and
                any(event.get('highlight') is True for event in schedule_events) and
                all('date' in event for event in schedule_events) and
                all(event.get('date') == '2025-06-15' for event in schedule_events)
            )
            
            # Validate important info persistence
            info_valid = (
                len(important_info) == 3 and
                'dress_code' in important_info and
                'parking' in important_info and
                'accommodations' in important_info
            )
            
            if not gallery_valid:
                print(f"❌ Gallery persistence failed")
            if not schedule_valid:
                print(f"❌ Schedule persistence failed")
            if not info_valid:
                print(f"❌ Important info persistence failed")
            
            return gallery_valid and schedule_valid and info_valid
        
        success, response = self.run_test(
            "Enhanced Data Persistence Check",
            "GET",
            "api/wedding",
            200,
            params={"session_id": self.session_id},
            validate_response=validate_persistence
        )
        
        if success:
            print(f"   ✅ Gallery photos persisted: {len(response.get('gallery_photos', []))} photos")
            print(f"   ✅ Schedule events persisted: {len(response.get('schedule_events', []))} events")
            print(f"   ✅ Important info persisted: {len(response.get('important_info', {}))} items")
            
        return success, response

    def test_mongodb_integration(self):
        """Test MongoDB integration is working correctly"""
        def validate_health(response_data):
            return response_data.get('status') == 'ok'
        
        return self.run_test(
            "MongoDB Integration Health Check", 
            "GET", 
            "api/test", 
            200,
            validate_response=validate_health
        )

    def test_public_access_enhanced_data(self):
        """Test that enhanced data is accessible via public URL"""
        if not self.wedding_id:
            self.critical_failures.append("Public Access: No wedding_id available")
            return False, {}
        
        def validate_public_access(response_data):
            gallery_photos = response_data.get('gallery_photos', [])
            schedule_events = response_data.get('schedule_events', [])
            important_info = response_data.get('important_info', {})
            
            # Verify public access includes enhanced data
            public_data_valid = (
                len(gallery_photos) == 4 and
                len(schedule_events) == 3 and
                len(important_info) == 3 and
                response_data.get('couple_name_1') == 'Gallery' and
                response_data.get('couple_name_2') == 'Tester'
            )
            
            # Ensure no sensitive data is exposed
            no_sensitive_data = 'user_id' not in response_data and '_id' not in response_data
            
            return public_data_valid and no_sensitive_data
        
        success, response = self.run_test(
            "Enhanced Data Public URL Access",
            "GET",
            f"api/wedding/public/{self.wedding_id}",
            200,
            validate_response=validate_public_access
        )
        
        if success:
            print(f"   ✅ Public enhanced data access working")
            print(f"   ✅ Gallery photos accessible: {len(response.get('gallery_photos', []))}")
            print(f"   ✅ Schedule events accessible: {len(response.get('schedule_events', []))}")
            print(f"   ✅ Important info accessible: {len(response.get('important_info', {}))}")
            
        return success, response

    def run_comprehensive_tests(self):
        """Run all enhanced gallery and schedule tests"""
        print("🚀 Starting Enhanced Gallery and Schedule Backend Tests")
        print("🎯 Focus: Enhanced Gallery Photos & Schedule Events with MongoDB")
        print("👤 Test User: gallerytester2025 / test123456")
        print("=" * 80)
        
        # Test sequence focusing on review request requirements
        tests = [
            ("1. MongoDB Integration Check", self.test_mongodb_integration),
            ("2. User Registration", self.test_user_registration),
            ("3. User Login", self.test_user_login),
            ("4. Wedding Data Retrieval", self.test_wedding_data_retrieval),
            ("5. 🚨 Enhanced Gallery Photos Save", self.test_enhanced_gallery_photos_save),
            ("6. 🚨 Enhanced Schedule Events Save", self.test_enhanced_schedule_events_save),
            ("7. Data Persistence Check", self.test_data_persistence),
            ("8. Public Access Enhanced Data", self.test_public_access_enhanced_data),
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
        print(f"📊 ENHANCED GALLERY & SCHEDULE TEST RESULTS")
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
        gallery_working = not any("Gallery" in failure for failure in self.critical_failures)
        schedule_working = not any("Schedule" in failure for failure in self.critical_failures)
        mongodb_working = not any("MongoDB" in failure for failure in self.critical_failures)
        auth_working = not any("Registration" in failure or "Login" in failure for failure in self.critical_failures)
        
        print(f"\n📋 FUNCTIONALITY STATUS:")
        print(f"   MongoDB Integration: {'✅ WORKING' if mongodb_working else '❌ FAILED'}")
        print(f"   User Authentication: {'✅ WORKING' if auth_working else '❌ FAILED'}")
        print(f"   Enhanced Gallery: {'✅ WORKING' if gallery_working else '❌ FAILED'}")
        print(f"   Enhanced Schedule: {'✅ WORKING' if schedule_working else '❌ FAILED'}")
        
        if gallery_working and schedule_working and mongodb_working and auth_working and len(self.critical_failures) == 0:
            print("\n✅ ALL ENHANCED GALLERY & SCHEDULE TESTS PASSED!")
            print("✅ MongoDB integration is working correctly")
            print("✅ Enhanced gallery functionality is fully operational")
            print("✅ Enhanced schedule functionality is fully operational")
            print("✅ Authentication and session management working")
            return 0
        else:
            print("\n❌ CRITICAL ENHANCED FUNCTIONALITY ISSUES DETECTED")
            if not gallery_working:
                print("❌ Enhanced gallery functionality has issues")
            if not schedule_working:
                print("❌ Enhanced schedule functionality has issues")
            if not mongodb_working:
                print("❌ MongoDB integration has issues")
            if not auth_working:
                print("❌ Authentication system has issues")
            return 1

def main():
    """Main test execution"""
    tester = EnhancedGalleryScheduleTester()
    return tester.run_comprehensive_tests()

if __name__ == "__main__":
    sys.exit(main())