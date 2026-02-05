#!/usr/bin/env python3
"""
Smart Study Bot - Main Application
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.config import Config
from src.bot.telegram_bot import SmartStudyBot
from src.scheduler.post_scheduler import PostScheduler
from src.database.database import DatabaseManager
from src.utils.logger import setup_logger

class SmartStudyBotApp:
    def __init__(self):
        self.config = Config()
        self.logger = setup_logger(__name__)
        self.db_manager = None
        self.bot = None
        self.scheduler = None
        
    async def initialize(self):
        try:
            self.logger.info("🚀 Initializing Smart Study Bot...")
            
            # Initialize database
            self.db_manager = DatabaseManager()
            await self.db_manager.initialize()
            
            # Initialize Telegram bot
            self.bot = SmartStudyBot(
                token=self.config.BOT_TOKEN,
                channel_id=self.config.CHANNEL_ID,
                db_manager=self.db_manager
            )
            
            # Initialize scheduler
            self.scheduler = PostScheduler(
                bot=self.bot,
                db_manager=self.db_manager,
                schedule_times=self.config.POST_SCHEDULE
            )
            
            self.logger.info("✅ All components initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Initialization failed: {str(e)}")
            return False
    
    async def run(self):
        try:
            # Start scheduler
            await self.scheduler.start()
            
            self.logger.info("🤖 Smart Study Bot is running!")
            self.logger.info(f"⏰ Schedule: {self.scheduler.get_next_run()}")
            
            # Keep running
            while True:
                await asyncio.sleep(60)
                
        except KeyboardInterrupt:
            self.logger.info("🛑 Shutting down...")
        finally:
            await self.shutdown()
    
    async def shutdown(self):
        try:
            if self.scheduler:
                await self.scheduler.stop()
            if self.db_manager:
                await self.db_manager.close()
        except Exception as e:
            self.logger.error(f"❌ Shutdown error: {str(e)}")

def main():
    app = SmartStudyBotApp()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        init_success = loop.run_until_complete(app.initialize())
        if init_success:
            loop.run_until_complete(app.run())
        else:
            sys.exit(1)
    except Exception as e:
        app.logger.error(f"❌ Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()