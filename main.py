import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from database import init_db
from handlers import start, admin, content, sections, tests
from handlers import ai_conversation
from utils.scheduler import start_scheduler

# Bot versiya: 2.1.0 - Production Ready (2025-07-29)
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global bot instance for other modules to use
bot = None

async def cleanup_webhook_before_start():
    """Clean up any existing webhook before starting polling"""
    try:
        temp_bot = Bot(token=BOT_TOKEN)
        await temp_bot.delete_webhook(drop_pending_updates=True)
        print("✅ Webhook cleaned up successfully")
        await temp_bot.session.close()
    except Exception as e:
        print(f"⚠️  Webhook cleanup warning: {e}")

async def main():
    global bot
    
    try:
        print("🚀 Starting Korean Language Bot...")
        
        # Clean up webhook first to avoid conflicts
        print("🧹 Cleaning up webhooks...")
        await cleanup_webhook_before_start()
        
        # Initialize database with error handling
        print("📊 Initializing database...")
        await init_db()
        print("✅ Database initialized successfully")
        
        # Initialize bot and dispatcher
        print("🤖 Initializing bot...")
        bot = Bot(
            token=BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        dp = Dispatcher(storage=MemoryStorage())
        print("✅ Bot initialized")
        
        # Include routers
        print("🔗 Registering handlers...")
        dp.include_router(start.router)
        dp.include_router(admin.router)
        dp.include_router(content.router)
        dp.include_router(sections.router)
        dp.include_router(tests.router)
        dp.include_router(ai_conversation.router)
        print("✅ All handlers registered")
        
        # Start scheduler for automated messages
        print("⏰ Starting scheduler...")
        await start_scheduler(bot)
        print("✅ Scheduler started")
        
        # Start polling
        print("🎯 Bot started successfully!")
        logger.info("Bot started")
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"❌ Error starting bot: {e}")
        print(f"❌ Critical error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
