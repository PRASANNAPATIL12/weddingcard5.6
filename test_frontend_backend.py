#!/usr/bin/env python3
"""
Test script to simulate frontend API calls and verify the production URL setup works correctly.
This will test if the frontend can properly reach the backend API.
"""

import requests
import json

def test_api_call(backend_url, custom_url):
    """Test API call to backend"""
    try:
        api_endpoint = f"{backend_url}/api/wedding/public/custom/{custom_url}"
        print(f"🔄 Testing API call: {api_endpoint}")
        
        response = requests.get(api_endpoint, timeout=10)
        print(f"✅ Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Found wedding for: {data['couple_name_1']} & {data['couple_name_2']}")
            print(f"   Venue: {data['venue_name']}")
            print(f"   Date: {data['wedding_date']}")
            print(f"   Custom URL: {data['custom_url']}")
            return True
        else:
            print(f"❌ API call failed with status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"❌ API call timed out - this is the issue!")
        return False
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection error - cannot reach backend")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("🧪 Testing Frontend-Backend API Connection")
    print("=" * 50)
    
    # Test cases
    test_cases = [
        {
            "name": "Local Backend",
            "backend_url": "http://localhost:8001",
            "custom_url": "sridharandsneha"
        },
        {
            "name": "Production Backend (same domain)",
            "backend_url": "https://wedding-share.preview.emergentagent.com",
            "custom_url": "sridharandsneha"
        }
    ]
    
    for test_case in test_cases:
        print(f"\n🔬 Testing: {test_case['name']}")
        print("-" * 30)
        success = test_api_call(test_case['backend_url'], test_case['custom_url'])
        if success:
            print(f"✅ {test_case['name']} - WORKING")
        else:
            print(f"❌ {test_case['name']} - FAILED")
    
    print("\n" + "=" * 50)
    print("🎯 Test Summary:")
    print("If Local Backend works but Production fails, the issue is network/CORS")
    print("If both work, the frontend environment variable needs to be updated")

if __name__ == "__main__":
    main()