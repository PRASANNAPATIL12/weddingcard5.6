#!/usr/bin/env python3
"""
Script to add sample wedding data to MongoDB for testing the public URL personalization fix.
This will ensure that when users visit https://wedding-share.preview.emergentagent.com/sridharandsneha,
they see "Sridhar & Sneha" wedding data instead of the default "Sarah & Michael" data.
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import uuid
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

MONGO_URL = os.getenv("MONGO_URL")
DB_NAME = os.getenv("DB_NAME", "weddingcard")

async def add_sample_data():
    try:
        print(f"🔄 Connecting to MongoDB: {MONGO_URL}")
        client = AsyncIOMotorClient(MONGO_URL)
        database = client[DB_NAME]
        
        # Test connection
        await database.command("ping")
        print(f"✅ Connected to MongoDB database: {DB_NAME}")
        
        # Get collections
        users_collection = database.users
        weddings_collection = database.weddings
        
        # Sample user data
        user_id = str(uuid.uuid4())
        user_data = {
            "id": user_id,
            "username": "sridhar_sneha",
            "password": "password123",
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Check if user already exists
        existing_user = await users_collection.find_one({"username": "sridhar_sneha"})
        if existing_user:
            print("User 'sridhar_sneha' already exists, using existing user")
            user_id = existing_user["id"]
        else:
            await users_collection.insert_one(user_data)
            print(f"✅ Created user: sridhar_sneha with ID: {user_id}")
        
        # Sample wedding data for Sridhar & Sneha
        wedding_data = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "couple_name_1": "Sridhar",
            "couple_name_2": "Sneha",
            "wedding_date": "2025-06-15",
            "venue_name": "Garden Paradise Resort",
            "venue_location": "Garden Paradise Resort • Bangalore, India",
            "their_story": "We met during college days and have been together for over 8 years. Join us as we celebrate our love story with family and friends in the beautiful Garden Paradise Resort.",
            "custom_url": "sridharandsneha",
            "story_timeline": [
                {
                    "year": "2016",
                    "title": "First Meeting",
                    "description": "We met during our engineering college days in Bangalore. It was in the college library where our eyes first met.",
                    "image": "https://images.unsplash.com/photo-1511285560929-80b456fea0bc?w=600&h=400&fit=crop"
                },
                {
                    "year": "2018",
                    "title": "First Date",
                    "description": "Our first official date was at a cozy cafe in Koramangala. We talked for hours about our dreams and aspirations.",
                    "image": "https://images.unsplash.com/photo-1511632765486-a01980e01a18?w=600&h=400&fit=crop"
                },
                {
                    "year": "2023",
                    "title": "The Proposal",
                    "description": "Sridhar proposed to Sneha at the same place where they first met - the college library. It was magical!",
                    "image": "https://images.unsplash.com/photo-1519741497674-611481863552?w=600&h=400&fit=crop"
                }
            ],
            "schedule_events": [
                {
                    "time": "10:00 AM",
                    "title": "Welcome & Registration",
                    "description": "Guest arrival and registration. Welcome drinks and light snacks will be served.",
                    "location": "Garden Paradise Resort - Main Entrance",
                    "icon": "Users",
                    "duration": "1 hour",
                    "highlight": False
                },
                {
                    "time": "11:00 AM",
                    "title": "Traditional Ceremonies",
                    "description": "Traditional Indian wedding ceremonies including Ganesh Puja, Kalyana Mandapa setup.",
                    "location": "Garden Paradise Resort - Main Hall",
                    "icon": "Heart",
                    "duration": "2 hours",
                    "highlight": True
                },
                {
                    "time": "1:00 PM",
                    "title": "Wedding Ceremony",
                    "description": "The main wedding ceremony with exchange of vows and rings.",
                    "location": "Garden Paradise Resort - Garden Area",
                    "icon": "Heart",
                    "duration": "1.5 hours",
                    "highlight": True
                },
                {
                    "time": "3:00 PM",
                    "title": "Lunch & Reception",
                    "description": "Wedding feast with traditional South Indian cuisine and reception.",
                    "location": "Garden Paradise Resort - Banquet Hall",
                    "icon": "Utensils",
                    "duration": "2 hours",
                    "highlight": False
                }
            ],
            "gallery_photos": [
                {
                    "url": "https://images.unsplash.com/photo-1519741497674-611481863552?w=600&h=400&fit=crop",
                    "caption": "Our engagement photo"
                },
                {
                    "url": "https://images.unsplash.com/photo-1511632765486-a01980e01a18?w=600&h=400&fit=crop",
                    "caption": "Together at the beach"
                }
            ],
            "bridal_party": [
                {
                    "name": "Priya",
                    "role": "Maid of Honor",
                    "description": "Sneha's best friend since childhood",
                    "photo": {
                        "url": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=300&h=300&fit=crop&crop=face"
                    }
                },
                {
                    "name": "Kavya",
                    "role": "Bridesmaid",
                    "description": "College roommate and dear friend",
                    "photo": {
                        "url": "https://images.unsplash.com/photo-1557804506-669a67965ba0?w=300&h=300&fit=crop&crop=face"
                    }
                }
            ],
            "groom_party": [
                {
                    "name": "Arjun",
                    "role": "Best Man",
                    "description": "Sridhar's brother and best friend",
                    "photo": {
                        "url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300&h=300&fit=crop&crop=face"
                    }
                },
                {
                    "name": "Karthik",
                    "role": "Groomsman",
                    "description": "College buddy and workout partner",
                    "photo": {
                        "url": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=300&h=300&fit=crop&crop=face"
                    }
                }
            ],
            "registry_items": [
                {
                    "name": "Dining Table Set",
                    "price": 25000,
                    "image": "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=400&h=300&fit=crop",
                    "description": "6-seater wooden dining table set",
                    "purchased": False
                },
                {
                    "name": "Kitchen Appliance Set",
                    "price": 35000,
                    "image": "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=400&h=300&fit=crop",
                    "description": "Complete kitchen appliance package",
                    "purchased": False
                }
            ],
            "honeymoon_fund": {
                "target_amount": 150000,
                "current_amount": 45000,
                "description": "Help us create magical memories on our honeymoon to Europe!"
            },
            "faqs": [
                {
                    "question": "What should I wear to the wedding?",
                    "answer": "We recommend traditional Indian attire. For men: kurta or shirt with dhoti/pants. For women: saree, lehenga, or salwar kameez in bright colors."
                },
                {
                    "question": "Is parking available at the venue?",
                    "answer": "Yes, Garden Paradise Resort has ample parking space for all guests. Valet parking service is also available."
                },
                {
                    "question": "Will there be vegetarian food options?",
                    "answer": "Absolutely! We have a wide variety of vegetarian dishes including South Indian, North Indian, and Indo-Chinese cuisine."
                },
                {
                    "question": "Can I bring my children?",
                    "answer": "Of course! We love having children at our celebration. There will be a dedicated kids' area with activities and child-friendly food options."
                }
            ],
            "theme": "classic",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        # Check if wedding data already exists for this custom URL
        existing_wedding = await weddings_collection.find_one({"custom_url": "sridharandsneha"})
        if existing_wedding:
            # Update existing wedding data
            await weddings_collection.update_one(
                {"custom_url": "sridharandsneha"},
                {"$set": wedding_data}
            )
            print("✅ Updated existing wedding data for 'sridharandsneha'")
        else:
            # Insert new wedding data
            await weddings_collection.insert_one(wedding_data)
            print("✅ Created new wedding data for 'sridharandsneha'")
        
        # Verify the data was inserted
        verification = await weddings_collection.find_one({"custom_url": "sridharandsneha"})
        if verification:
            print(f"✅ Verification successful: Found wedding for {verification['couple_name_1']} & {verification['couple_name_2']}")
            print(f"   Custom URL: {verification['custom_url']}")
            print(f"   Venue: {verification['venue_name']}")
            print(f"   Date: {verification['wedding_date']}")
        else:
            print("❌ Verification failed: Wedding data not found")
        
        # Close connection
        client.close()
        print("🎉 Sample data setup completed successfully!")
        print("\n🌐 Now when users visit https://wedding-share.preview.emergentagent.com/sridharandsneha")
        print("   they will see personalized 'Sridhar & Sneha' wedding data instead of default 'Sarah & Michael'")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if client:
            client.close()

if __name__ == "__main__":
    asyncio.run(add_sample_data())