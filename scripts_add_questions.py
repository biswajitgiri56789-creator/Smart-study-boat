#!/usr/bin/env python3
"""
Add questions to database
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.database.database import DatabaseManager
import asyncio

async def main():
    db_manager = DatabaseManager()
    await db_manager.initialize()
    
    questions = [
        {
            "class": "college_year_1",
            "subject": "calculus",
            "question": "Limit and continuity এর সংজ্ঞা দাও",
            "importance": "high",
            "marks": 10,
            "chapter": "Introduction"
        },
        {
            "class": "college_year_2",
            "subject": "data_structures",
            "question": "Linked List এবং Array এর মধ্যে পার্থক্য লিখ",
            "importance": "very_high",
            "marks": 15,
            "chapter": "Basic Data Structures"
        }
    ]
    
    for q in questions:
        success = await db_manager.add_question(
            class_key=q["class"],
            subject_key=q["subject"],
            question=q["question"],
            importance=q["importance"],
            marks=q["marks"],
            chapter=q["chapter"]
        )
        
        if success:
            print(f"✅ Added: {q['question'][:50]}...")
        else:
            print(f"❌ Failed: {q['question'][:50]}...")
    
    await db_manager.close()

if __name__ == "__main__":
    asyncio.run(main())