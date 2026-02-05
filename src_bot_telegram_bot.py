import asyncio
import logging
from datetime import datetime
from telegram import Bot
from telegram.error import TelegramError

from src.config import Config
from src.config.constants import TELEGRAM_MAX_MESSAGE_LENGTH, POST_TEMPLATES

logger = logging.getLogger(__name__)

class SmartStudyBot:
    def __init__(self, token: str, channel_id: str, db_manager):
        self.bot = Bot(token=token)
        self.channel_id = channel_id
        self.db_manager = db_manager
        self.config = Config()
        self.post_count = 0
        
        logger.info(f"🤖 Bot initialized for {channel_id}")
    
    async def send_post(self, content: str) -> bool:
        try:
            if len(content) > TELEGRAM_MAX_MESSAGE_LENGTH:
                return await self.send_split_post(content)
            
            await self.bot.send_message(
                chat_id=self.channel_id,
                text=content,
                parse_mode="Markdown",
                disable_web_page_preview=True
            )
            
            self.post_count += 1
            logger.info(f"✅ Post sent to {self.channel_id}")
            return True
            
        except TelegramError as e:
            logger.error(f"❌ Telegram error: {str(e)}")
            return False
    
    async def send_split_post(self, content: str) -> bool:
        try:
            chunks = []
            current_chunk = ""
            
            lines = content.split('\n')
            for line in lines:
                if len(current_chunk) + len(line) + 1 < TELEGRAM_MAX_MESSAGE_LENGTH:
                    current_chunk += line + '\n'
                else:
                    chunks.append(current_chunk)
                    current_chunk = line + '\n'
            
            if current_chunk:
                chunks.append(current_chunk)
            
            success_count = 0
            for i, chunk in enumerate(chunks):
                try:
                    if i == 0:
                        await self.bot.send_message(
                            chat_id=self.channel_id,
                            text=chunk,
                            parse_mode="Markdown"
                        )
                    else:
                        await self.bot.send_message(
                            chat_id=self.channel_id,
                            text=f"*(Continued...)*\n\n{chunk}",
                            parse_mode="Markdown"
                        )
                    
                    success_count += 1
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    logger.error(f"❌ Error sending chunk {i+1}: {str(e)}")
            
            return success_count > 0
            
        except Exception as e:
            logger.error(f"❌ Error in split post: {str(e)}")
            return False
    
    def get_time_based_greeting(self):
        hour = datetime.now().hour
        
        if 5 <= hour < 12:
            return POST_TEMPLATES["morning"]
        elif 12 <= hour < 17:
            return POST_TEMPLATES["afternoon"]
        elif 17 <= hour < 20:
            return POST_TEMPLATES["evening"]
        else:
            return POST_TEMPLATES["night"]
    
    async def generate_daily_content(self):
        try:
            greeting = self.get_time_based_greeting()
            date_str = datetime.now().strftime("%d %B, %Y")
            
            content = f"{greeting}"
            content += f"📅 *তারিখ:* {date_str}\n"
            content += f"⏰ *সময়:* {datetime.now().strftime('%I:%M %p')}\n"
            content += "="*30 + "\n\n"
            
            all_classes = self.config.CLASSES.keys()
            
            for class_key in all_classes:
                class_name = self.config.get_class_name(class_key)
                content += f"🎓 *{class_name.upper()}*\n"
                content += "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
                
                subjects = self.config.SUBJECTS.get(class_key, [])
                
                for subject_key in subjects:
                    questions = await self.db_manager.get_unique_questions(
                        class_key=class_key,
                        subject_key=subject_key,
                        limit=self.config.MAX_QUESTIONS_PER_POST
                    )
                    
                    if questions:
                        subject_name = self.config.get_subject_name(subject_key, "bn")
                        content += f"📖 *{subject_name}:*\n"
                        
                        for idx, question in enumerate(questions, 1):
                            q_text = question.get('question', '')
                            importance = question.get('importance', 'medium')
                            marks = question.get('marks', 5)
                            chapter = question.get('chapter', '')
                            
                            content += f"   {idx}. {q_text}\n"
                            
                            if chapter:
                                content += f"      📚 অধ্যায়: {chapter}\n"
                            if marks:
                                content += f"      📝 নম্বর: {marks}\n"
                            
                            if importance == 'very_high':
                                content += "      🔥 *১০০% পরীক্ষায় আসবে*\n"
                            elif importance == 'high':
                                content += "      ⭐ *খুবই গুরুত্বপূর্ণ*\n"
                        
                        suggestion = await self.db_manager.get_suggestion(
                            class_key=class_key,
                            subject_key=subject_key
                        )
                        
                        if suggestion:
                            content += f"      💡 *পরামর্শ:* {suggestion}\n"
                        
                        content += "\n"
                
                content += "\n"
            
            # Footer
            content += "="*30 + "\n"
            content += "🤖 *বটের বিশেষত্ব:*\n"
            content += "• স্বয়ংক্রিয় প্রশ্ন পোস্টিং\n"
            content += "• ১০০% পরীক্ষার জন্য গুরুত্বপূর্ণ\n"
            content += "• দৈনিক ৭ বার আপডেট\n\n"
            content += "📌 *চ্যানেলে যুক্ত হন:* @smartstudynotes11\n"
            content += "🤖 *বট:* @smartstudy11bot\n"
            
            return content
                
        except Exception as e:
            logger.error(f"❌ Error generating content: {str(e)}")
            return "⚠️ Error generating content"
    
    async def post_daily_content(self) -> bool:
        try:
            logger.info("🔄 Generating daily content...")
            
            content = await self.generate_daily_content()
            
            if not content:
                logger.error("❌ No content generated")
                return False
            
            success = await self.send_post(content)
            
            if success:
                await self.db_manager.update_posted_questions()
                logger.info("📝 Database updated")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Error in post_daily_content: {str(e)}")
            return False
    
    async def test_connection(self) -> bool:
        try:
            me = await self.bot.get_me()
            logger.info(f"✅ Bot connected: @{me.username}")
            return True
        except Exception as e:
            logger.error(f"❌ Bot connection failed: {str(e)}")
            return False