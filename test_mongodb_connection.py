#!/usr/bin/env python3

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
from pathlib import Path

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / 'backend' / '.env')

MONGO_URL = os.getenv("MONGO_URL")
DB_NAME = os.getenv("DB_NAME", "weddingcard")

async def test_mongodb_connection():
    """Test MongoDB connection and display existing data"""
    try:
        print(f"🔄 Connecting to MongoDB: {MONGO_URL}")
        
        # Connect to MongoDB
        client = AsyncIOMotorClient(MONGO_URL)
        database = client[DB_NAME]
        
        # Test connection
        await database.command("ping")
        print(f"✅ Connected to MongoDB database: {DB_NAME}")
        
        # Check collections
        collections = await database.list_collection_names()
        print(f"📋 Available collections: {collections}")
        
        # Check users collection
        if "users" in collections:
            users_collection = database.users
            users_count = await users_collection.count_documents({})
            print(f"👥 Users collection: {users_count} documents")
            
            # List all users
            async for user in users_collection.find({}, {"password": 0}):  # Exclude password for security
                print(f"   User: {user}")
        
        # Check weddings collection
        if "weddings" in collections:
            weddings_collection = database.weddings
            weddings_count = await weddings_collection.count_documents({})
            print(f"💒 Weddings collection: {weddings_count} documents")
            
            # List all weddings
            async for wedding in weddings_collection.find({}):
                print(f"   Wedding: custom_url='{wedding.get('custom_url')}', couple='{wedding.get('couple_name_1')} & {wedding.get('couple_name_2')}'")
        
        # Close connection
        client.close()
        print("✅ MongoDB connection test completed successfully")
        
    except Exception as e:
        print(f"❌ Error connecting to MongoDB: {e}")

if __name__ == "__main__":
    asyncio.run(test_mongodb_connection())