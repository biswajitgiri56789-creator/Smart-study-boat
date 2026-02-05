import asyncio
import logging
from datetime import datetime
from typing import List
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from src.config import Config

logger = logging.getLogger(__name__)

class PostScheduler:
    def __init__(self, bot, db_manager, schedule_times: List[str] = None):
        self.bot = bot
        self.db_manager = db_manager
        self.config = Config()
        self.schedule_times = schedule_times or self.config.POST_SCHEDULE
        self.scheduler = AsyncIOScheduler()
        self.is_running = False
        
        logger.info(f"⏰ Scheduler initialized with {len(self.schedule_times)} time slots")
    
    def convert_to_utc(self, bd_time: str) -> str:
        try:
            bd_hour, bd_minute = map(int, bd_time.split(':'))
            utc_hour = (bd_hour - 6) % 24
            return f"{utc_hour:02d}:{bd_minute:02d}"
        except Exception as e:
            logger.error(f"❌ Time conversion error: {str(e)}")
            return bd_time
    
    async def scheduled_post_job(self):
        current_time = datetime.now().strftime("%H:%M")
        logger.info(f"⏰ Running scheduled job at {current_time}")
        
        try:
            success = await self.bot.post_daily_content()
            
            if success:
                logger.info(f"✅ Job completed at {current_time}")
            else:
                logger.error(f"❌ Job failed at {current_time}")
                
        except Exception as e:
            logger.error(f"❌ Error in scheduled job: {str(e)}")
    
    async def start(self):
        try:
            if self.is_running:
                return
            
            logger.info("🚀 Starting post scheduler...")
            
            for bd_time in self.schedule_times:
                utc_time = self.convert_to_utc(bd_time)
                hour, minute = map(int, utc_time.split(':'))
                
                self.scheduler.add_job(
                    self.scheduled_post_job,
                    trigger=CronTrigger(hour=hour, minute=minute),
                    id=f"post_{bd_time.replace(':', '')}",
                    name=f"Daily post at {bd_time}",
                    replace_existing=True
                )
                
                logger.info(f"✅ Scheduled post at {bd_time}")
            
            self.scheduler.start()
            self.is_running = True
            
            logger.info(f"✅ Scheduler started")
            
        except Exception as e:
            logger.error(f"❌ Error starting scheduler: {str(e)}")
    
    async def stop(self):
        try:
            if self.scheduler.running:
                self.scheduler.shutdown()
                self.is_running = False
                logger.info("✅ Scheduler stopped")
        except Exception as e:
            logger.error(f"❌ Error stopping scheduler: {str(e)}")
    
    def get_next_run(self) -> str:
        try:
            if self.scheduler.running:
                next_run = self.scheduler.get_jobs()[0].next_run_time
                if next_run:
                    bd_time = (next_run.hour + 6) % 24
                    return f"{bd_time:02d}:{next_run.minute:02d}"
            return "Not scheduled"
        except:
            return "Not available"