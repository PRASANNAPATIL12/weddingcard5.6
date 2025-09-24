#!/usr/bin/env python3

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
from pathlib import Path
import uuid
from datetime import datetime

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / 'backend' / '.env')

MONGO_URL = os.getenv("MONGO_URL")
DB_NAME = os.getenv("DB_NAME", "weddingcard")

async def create_sample_wedding():
    """Create a sample wedding with the URL format the user was trying to access"""
    try:
        print(f"🔄 Connecting to MongoDB...")
        
        # Connect to MongoDB
        client = AsyncIOMotorClient(MONGO_URL)
        database = client[DB_NAME]
        
        # Get collections
        users_collection = database.users
        weddings_collection = database.weddings
        
        # Create a test user
        user_id = str(uuid.uuid4())
        user_data = {
            "id": user_id,
            "username": "demo_user_test",
            "password": "password123",
            "created_at": datetime.utcnow()
        }
        
        print(f"👤 Creating user: {user_data['username']}")
        await users_collection.insert_one(user_data)
        
        # Create wedding data with the user's desired URL format
        wedding_id = str(uuid.uuid4())
        custom_url = "user_1758131859703_iozejw5l0"  # The URL the user was trying to access
        
        wedding_data = {
            "id": wedding_id,
            "user_id": user_id,
            "couple_name_1": "John",
            "couple_name_2": "Emily",
            "wedding_date": "2025-08-20",
            "venue_name": "Emerald Palace Resort",
            "venue_location": "Emerald Palace Resort • Mumbai, India",
            "their_story": "A beautiful love story that began in college and blossomed into a lifetime commitment. Join us as we celebrate our union surrounded by family and friends.",
            "custom_url": custom_url,
            "story_timeline": [
                {
                    "year": "2020",
                    "title": "First Meeting",
                    "description": "We met during our final year of college at the university library.",
                    "image": "https://images.unsplash.com/photo-1511285560929-80b456fea0bc?w=600&h=400&fit=crop"
                },
                {
                    "year": "2022",
                    "title": "The Proposal",
                    "description": "John proposed to Emily at the beach during sunset, the most magical moment of our lives.",
                    "image": "https://images.unsplash.com/photo-1519741497674-611481863552?w=600&h=400&fit=crop"
                }
            ],
            "schedule_events": [
                {
                    "time": "4:00 PM",
                    "title": "Welcome Ceremony",
                    "description": "Join us for welcome drinks and meet the families.",
                    "location": "Emerald Palace Resort - Garden Area",
                    "icon": "Users",
                    "duration": "1 hour",
                    "highlight": False
                },
                {
                    "time": "6:00 PM",
                    "title": "Wedding Ceremony",
                    "description": "The main wedding ceremony with exchange of vows.",
                    "location": "Emerald Palace Resort - Main Hall",
                    "icon": "Heart",
                    "duration": "1.5 hours",
                    "highlight": True
                },
                {
                    "time": "8:00 PM",
                    "title": "Reception Dinner",
                    "description": "Celebration dinner with music and dancing.",
                    "location": "Emerald Palace Resort - Banquet Hall",
                    "icon": "Utensils",
                    "duration": "3 hours",
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
                    "name": "Sarah",
                    "role": "Maid of Honor",
                    "description": "Emily's sister and best friend",
                    "photo": {
                        "url": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=300&h=300&fit=crop&crop=face"
                    }
                }
            ],
            "groom_party": [
                {
                    "name": "Michael",
                    "role": "Best Man",
                    "description": "John's college roommate and lifelong friend",
                    "photo": {
                        "url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300&h=300&fit=crop&crop=face"
                    }
                }
            ],
            "registry_items": [
                {
                    "name": "Dinner Set",
                    "price": 15000,
                    "image": "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=400&h=300&fit=crop",
                    "description": "Beautiful ceramic dinner set for 8 people",
                    "purchased": False
                }
            ],
            "honeymoon_fund": {
                "target_amount": 100000,
                "current_amount": 25000,
                "description": "Help us create beautiful memories on our honeymoon to Switzerland!"
            },
            "faqs": [
                {
                    "question": "What is the dress code for the wedding?",
                    "answer": "We request semi-formal attire. For men: suit or formal shirt with trousers. For women: dress or elegant outfit in any color except white."
                },
                {
                    "question": "Is there parking available?",
                    "answer": "Yes, Emerald Palace Resort provides complimentary parking for all wedding guests."
                }
            ],
            "theme": "classic",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        print(f"💒 Creating wedding with custom URL: {custom_url}")
        await weddings_collection.insert_one(wedding_data)
        
        print(f"✅ Successfully created wedding!")
        print(f"🔗 Your wedding URL: http://localhost:3000/{custom_url}")
        print(f"👥 Couple: {wedding_data['couple_name_1']} & {wedding_data['couple_name_2']}")
        print(f"📅 Date: {wedding_data['wedding_date']}")
        print(f"📍 Venue: {wedding_data['venue_location']}")
        
        # Close connection
        client.close()
        
    except Exception as e:
        print(f"❌ Error creating wedding: {e}")

if __name__ == "__main__":
    asyncio.run(create_sample_wedding())