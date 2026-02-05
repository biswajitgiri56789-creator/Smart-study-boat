import sqlite3
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

from src.config import Config
from src.config.constants import DB_QUESTION_TABLE, DB_POSTED_TABLE

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path: str = None):
        self.config = Config()
        self.db_path = db_path or "data/studybots.db"
        self.conn = None
        self.cursor = None
        
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"📊 Database path: {self.db_path}")
    
    async def initialize(self):
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            
            self.cursor.execute("PRAGMA foreign_keys = ON")
            await self.create_tables()
            await self.populate_initial_data()
            
            logger.info("✅ Database initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {str(e)}")
            return False
    
    async def create_tables(self):
        # Questions table
        self.cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {DB_QUESTION_TABLE} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                class TEXT NOT NULL,
                subject TEXT NOT NULL,
                question TEXT NOT NULL,
                importance TEXT DEFAULT 'medium',
                marks INTEGER DEFAULT 5,
                chapter TEXT,
                posted_count INTEGER DEFAULT 0,
                last_posted DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(class, subject, question)
            )
        """)
        
        # Posted history table
        self.cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {DB_POSTED_TABLE} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_id INTEGER NOT NULL,
                post_date DATE NOT NULL,
                post_time TIME NOT NULL,
                FOREIGN KEY (question_id) REFERENCES {DB_QUESTION_TABLE}(id)
            )
        """)
        
        self.conn.commit()
        logger.info("✅ Database tables created")
    
    async def populate_initial_data(self):
        try:
            self.cursor.execute(f"SELECT COUNT(*) FROM {DB_QUESTION_TABLE}")
            count = self.cursor.fetchone()[0]
            
            if count == 0:
                logger.info("📥 Populating database with initial questions...")
                
                # Sample questions
                sample_questions = [
                    ("class_11", "physics", "নিউটনের গতির সূত্রগুলো বর্ণনা করুন", "very_high", 10, "বল ও গতি"),
                    ("class_11", "chemistry", "আবেশী ও অনাবেশী যৌগের পার্থক্য লিখ", "high", 8, "রাসায়নিক বন্ধন"),
                    ("class_12", "physics", "তড়িৎ ক্ষেত্র ও চুম্বক ক্ষেত্রের সম্পর্ক ব্যাখ্যা কর", "very_high", 15, "তড়িৎচুম্বকত্ব"),
                    ("college_year_1", "calculus", "Limit and continuity এর সংজ্ঞা দাও", "high", 10, "Introduction"),
                ]
                
                for q in sample_questions:
                    await self.add_question(*q)
                
                logger.info("✅ Inserted sample questions")
            
            self.conn.commit()
            
        except Exception as e:
            logger.error(f"❌ Error populating data: {str(e)}")
    
    async def add_question(self, class_key: str, subject_key: str, question: str, 
                          importance: str = "medium", marks: int = 5, chapter: str = "") -> bool:
        try:
            self.cursor.execute(f"""
                INSERT OR IGNORE INTO {DB_QUESTION_TABLE} 
                (class, subject, question, importance, marks, chapter)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (class_key, subject_key, question, importance, marks, chapter))
            
            self.conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"❌ Error adding question: {str(e)}")
            return False
    
    async def get_unique_questions(self, class_key: str, subject_key: str, limit: int = 3):
        try:
            threshold_date = (datetime.now() - timedelta(days=self.config.MIN_DAYS_BETWEEN_REPOSTS)).strftime('%Y-%m-%d')
            
            query = f"""
                SELECT q.id, q.question, q.importance, q.marks, q.chapter
                FROM {DB_QUESTION_TABLE} q
                LEFT JOIN {DB_POSTED_TABLE} ph ON q.id = ph.question_id 
                    AND ph.post_date > ?
                WHERE q.class = ? 
                    AND q.subject = ?
                    AND ph.id IS NULL
                ORDER BY 
                    CASE q.importance 
                        WHEN 'very_high' THEN 1
                        WHEN 'high' THEN 2
                        ELSE 3
                    END,
                    RANDOM()
                LIMIT ?
            """
            
            self.cursor.execute(query, (threshold_date, class_key, subject_key, limit))
            rows = self.cursor.fetchall()
            
            questions = []
            for row in rows:
                questions.append({
                    'id': row[0],
                    'question': row[1],
                    'importance': row[2],
                    'marks': row[3],
                    'chapter': row[4]
                })
            
            return questions
            
        except Exception as e:
            logger.error(f"❌ Error getting questions: {str(e)}")
            return []
    
    async def get_suggestion(self, class_key: str, subject_key: str) -> str:
        default_suggestions = {
            "physics": "গাণিতিক সমস্যা বেশি প্র্যাকটিস করুন",
            "chemistry": "রাসায়নিক সূত্র ও বিক্রিয়া মুখস্থ করুন",
            "mathematics": "প্রতিটি অধ্যায়ের সূত্র ভালো করে শিখুন",
            "biology": "ডায়াগ্রাম ও লেবেলিং এ গুরুত্ব দিন",
            "english": "গ্রামার ও ভোকাবুলারি শক্ত করুন",
            "calculus": "প্র্যাকটিস সমস্যা বেশি বেশি করুন",
            "programming": "কোডিং প্র্যাকটিস নিয়মিত করুন"
        }
        
        return default_suggestions.get(subject_key, "নিয়মিত পড়াশোনা ও প্র্যাকটিস করুন")
    
    async def update_posted_questions(self):
        try:
            # Get questions that were in today's post
            # This is simplified - in real implementation, track question IDs
            logger.info("📝 Updating posted questions...")
            
        except Exception as e:
            logger.error(f"❌ Error updating posted questions: {str(e)}")
    
    async def get_statistics(self):
        try:
            stats = {}
            self.cursor.execute(f"SELECT COUNT(*) FROM {DB_QUESTION_TABLE}")
            stats['total_questions'] = self.cursor.fetchone()[0]
            return stats
        except Exception as e:
            logger.error(f"❌ Error getting statistics: {str(e)}")
            return {}
    
    async def close(self):
        try:
            if self.conn:
                self.conn.close()
        except Exception as e:
            logger.error(f"❌ Error closing database: {str(e)}")