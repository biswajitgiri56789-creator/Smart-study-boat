import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    def __init__(self):
        self.BASE_DIR = Path(__file__).parent.parent.parent
        
        # Telegram
        self.BOT_TOKEN = os.getenv("BOT_TOKEN", "")
        self.CHANNEL_ID = os.getenv("CHANNEL_ID", "@smartstudynotes11")
        
        # Database
        self.DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/studybots.db")
        
        # Posting Schedule (Bangladesh Time)
        self.POST_SCHEDULE = [
            "08:00", "10:00", "12:00", 
            "15:00", "17:00", "19:00", "21:00"
        ]
        
        # Classes
        self.CLASSES = {
            "class_11": "Class 11",
            "class_12": "Class 12",
            "college_year_1": "College Year 1",
            "college_year_2": "College Year 2",
            "college_year_3": "College Year 3"
        }
        
        # Subjects
        self.SUBJECTS = {
            "class_11": ["physics", "chemistry", "mathematics", "biology"],
            "class_12": ["physics", "chemistry", "mathematics", "biology"],
            "college_year_1": ["calculus", "physics", "chemistry", "programming"],
            "college_year_2": ["data_structures", "algorithms", "statistics", "economics"],
            "college_year_3": ["database", "networking", "machine_learning", "finance"]
        }
        
        # Subject Names
        self.SUBJECT_NAMES = {
            "physics": {"en": "Physics", "bn": "পদার্থবিজ্ঞান"},
            "chemistry": {"en": "Chemistry", "bn": "রসায়ন"},
            "mathematics": {"en": "Mathematics", "bn": "গণিত"},
            "biology": {"en": "Biology", "bn": "জীববিজ্ঞান"},
            "english": {"en": "English", "bn": "ইংরেজি"},
            "bangla": {"en": "Bangla", "bn": "বাংলা"},
            "calculus": {"en": "Calculus", "bn": "ক্যালকুলাস"},
            "programming": {"en": "Programming", "bn": "প্রোগ্রামিং"},
            "data_structures": {"en": "Data Structures", "bn": "ডেটা স্ট্রাকচার"},
            "algorithms": {"en": "Algorithms", "bn": "অ্যালগরিদম"},
            "database": {"en": "Database", "bn": "ডেটাবেস"},
            "networking": {"en": "Networking", "bn": "নেটওয়ার্কিং"},
            "machine_learning": {"en": "Machine Learning", "bn": "মেশিন লার্নিং"}
        }
        
        # Settings
        self.MAX_QUESTIONS_PER_POST = 3
        self.MIN_DAYS_BETWEEN_REPOSTS = 30
        
        # Validation
        self.validate()
    
    def validate(self):
        if not self.BOT_TOKEN:
            raise ValueError("BOT_TOKEN is required")
        if not self.CHANNEL_ID:
            raise ValueError("CHANNEL_ID is required")
    
    def get_subject_name(self, subject_key, language="bn"):
        return self.SUBJECT_NAMES.get(subject_key, {}).get(language, subject_key)
    
    def get_class_name(self, class_key):
        return self.CLASSES.get(class_key, class_key)