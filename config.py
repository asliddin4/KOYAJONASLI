import os

# Bot configuration
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

# Admin configuration
ADMIN_ID = int(os.getenv("ADMIN_ID", "5974022170"))
ADMIN_LINK = "@chang_chi_won"

# Channel and Instagram configuration
CHANNELS = {
    "@koreys_quiz": "Korean Quiz Channel",
    "@korestili_teknkurs": "Korean Tech Course Channel"
}
INSTAGRAM_URL = "https://www.instagram.com/kores_tili_online?igsh=MXN50HZobGZ1NXpleA=="

# Premium subscription configuration
PREMIUM_PRICE_UZS = 50000  # 50,000 som
REFERRAL_THRESHOLD = 10    # 10 referrals for 1 month premium

# Database configuration
DATABASE_PATH = "language_bot.db"

# Scheduler configuration
MOTIVATIONAL_MESSAGE_HOUR = 10  # 10 AM weekly messages
PREMIUM_PROMOTION_DAYS = [1, 15]  # 1st and 15th of each month
