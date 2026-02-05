#!/usr/bin/env python3
"""
Initialize database
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.database.database import DatabaseManager
import asyncio

async def main():
    db_manager = DatabaseManager()
    
    print("📊 Initializing database...")
    success = await db_manager.initialize()
    
    if success:
        stats = await db_manager.get_statistics()
        print(f"✅ Database initialized")
        print(f"📝 Total questions: {stats.get('total_questions', 0)}")
    else:
        print("❌ Database initialization failed")
    
    await db_manager.close()

if __name__ == "__main__":
    asyncio.run(main())