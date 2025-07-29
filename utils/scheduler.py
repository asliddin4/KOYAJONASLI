import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
import aiosqlite
from aiogram import Bot

from config import DATABASE_PATH, MOTIVATIONAL_MESSAGE_HOUR, PREMIUM_PROMOTION_DAYS
from messages import MOTIVATIONAL_MESSAGES, PREMIUM_PROMOTION_MESSAGES
from utils.rating_system import calculate_weekly_bonus
import random

scheduler = AsyncIOScheduler()

async def send_weekly_motivational_messages(bot: Bot):
    """Send personalized weekly motivational messages based on user activity and progress"""
    try:
        # Get users with different activity levels for personalized messages
        async with aiosqlite.connect(DATABASE_PATH) as db:
            cursor = await db.execute("""
                SELECT user_id, first_name, rating_score, words_learned, quiz_score_total, 
                       total_sessions, last_activity
                FROM users 
                WHERE last_activity > date('now', '-7 days') AND total_sessions >= 1
                ORDER BY rating_score DESC, last_activity DESC
                LIMIT 500
            """)
            active_users = await cursor.fetchall()
        
        print(f"Database query returned {len(active_users)} users")
        if not active_users:
            print("No active users found, exiting function")
            return
        
        sent_count = 0
        print(f"Found {len(active_users)} active users to send messages to")
        
        for user_id, first_name, rating, words, quiz_score, sessions, last_activity in active_users:
            try:
                name = first_name or "Do'stim"
                print(f"Attempting to send message to user {user_id} ({name})")
                
                # Personalized message based on user progress
                if rating >= 100:  # High achievers - motivate to continue
                    message = f"""
🏆 <b>Mukammal natijalar, {name}!</b>

Siz haqiqatan ham ajoyib o'rganyapsiz! 

📊 Sizning yutuqlaringiz:
• Reyting: {rating:.1f} ball (TOP darajada!)
• O'rganilgan so'zlar: {words or 0} ta
• Test natijalari: {quiz_score or 0} ball
• Sessiyalar: {sessions} ta

🌟 Siz professional darajaga yaqin turibsiz!

💎 <b>Premium bilan yanada tezroq rivojlaning:</b>
• Maxsus professional darslar
• AI bilan amaliy suhbat
• Batafsil grammatika tushuntirishlari
• Individual o'quv rejasi

/premium - batafsil ma'lumot olish

Davom eting - muvaffaqiyat sizni kutmoqda! 🚀
                    """
                elif rating >= 50:  # Medium achievers - encourage and promote premium
                    message = f"""
⭐ <b>Ajoyib natijalar, {name}!</b>

Siz yaxshi yo'lda ketyapsiz!

📈 Hozirgi yutuqlaringiz:
• Reyting: {rating:.1f} ball
• So'zlar: {words or 0} ta
• Testlar: {quiz_score or 0} ball
• Sessiyalar: {sessions} ta

🎯 <b>Top darajaga chiqish uchun:</b>

💎 Premium obuna bilan 2x tezroq o'rganing:
• Video darsliklar (Recipe, SOULT seriyalari)
• AI bilan koreys/yapon tilida suhbat
• Grammar AI - har qanday savolga javob
• Reklama yo'q tajriba

💰 Faqat 50,000 so'm/oy
👥 Yoki 10 ta do'st taklif qiling = 1 oy BEPUL!

/premium buyrug'ini yuboring!

Bu hafta yangi cho'qqilarga chiqaylik! 📚
                    """
                else:  # Beginners - basic motivation with gentle premium hint
                    message = f"""
🚀 <b>Ajoyib boshlanish, {name}!</b>

Til o'rganish sayohatingiz boshlanmoqda!

📊 Hozirgi natijalar:
• Sessiyalar: {sessions} ta
• Reyting: {rating or 0} ball
• So'zlar: {words or 0} ta

💡 <b>Tezroq o'rganish uchun maslahatlar:</b>
• Har kuni 15-20 daqiqa vaqt ajrating
• Testlarni muntazam yechib turing
• Yangi so'zlarni takrorlang
• Video darslarni ko'ring

🌟 Premium bilan yanada samarali o'rganing:
• Professional video darslar
• AI bilan amaliy mashqlar
• Batafsil tushuntirishlar

/premium - batafsil ma'lumot

Kichik qadamlar katta natijalarga olib keladi! 📖
                    """
                
                await bot.send_message(user_id, message.strip())
                print(f"✅ Message sent successfully to user {user_id}")
                sent_count += 1
                
                # Small delay to avoid hitting rate limits
                await asyncio.sleep(0.15)
                
            except Exception as e:
                # User might have blocked the bot
                print(f"❌ Failed to send message to user {user_id}: {e}")
                continue
        
        print(f"Sent personalized weekly motivational messages to {sent_count} users")
        
    except Exception as e:
        print(f"Error sending motivational messages: {e}")

async def send_premium_promotion_messages(bot: Bot):
    """Send personalized premium promotion based on user engagement and progress"""
    try:
        # Get active non-premium users with their progress data
        async with aiosqlite.connect(DATABASE_PATH) as db:
            cursor = await db.execute("""
                SELECT user_id, first_name, rating_score, words_learned, quiz_score_total, 
                       total_sessions, COALESCE(referral_count, 0) as referral_count
                FROM users 
                WHERE (is_premium = FALSE OR premium_expires_at < CURRENT_TIMESTAMP)
                AND last_activity > date('now', '-14 days')
                AND total_sessions >= 3
                ORDER BY rating_score DESC, total_sessions DESC
                LIMIT 300
            """)
            non_premium_users = await cursor.fetchall()
        
        if not non_premium_users:
            return
            
        sent_count = 0
        for user_id, first_name, rating, words, quiz_score, sessions, referrals in non_premium_users:
            try:
                name = first_name or "Do'stim"
                remaining_referrals = max(0, 10 - (referrals or 0))
                
                # Personalized premium promotion based on user engagement  
                if rating >= 80 and sessions >= 15:  # High engagement users - special offers
                    message = f"""
💎 <b>TOP foydalanuvchi uchun maxsus taklif!</b>

{name}, siz bizning eng faol o'quvchimiz!

🏆 Ajoyib natijalaringiz:
• Reyting: {rating:.1f} ball (TOP!)
• Sessiyalar: {sessions} ta  
• So'zlar: {words or 0} ta
• Testlar: {quiz_score or 0} ball

🚀 <b>Premium bilan professional darajaga:</b>

🎥 Recipe va SOULT koreys darslik seriyalari
🤖 AI Conversation - koreys/yapon tilida real suhbat
📚 Grammar AI - har qanday grammatika savoliga javob
🎯 Maxsus testlar va individual rejalar
🔥 Reklama yo'q, toza tajriba

💸 <b>Sizga maxsus:</b>
💰 50,000 so'm/oy (odatiy narx)
🎁 Yoki {remaining_referrals} ta do'st = 1 oy BEPUL!

Sizning darajangizda Premium zarur! /premium
                    """
                elif sessions >= 8:  # Medium engagement - convince with benefits
                    message = f"""
🌟 <b>Natijalaringizni 2x oshiring!</b>

{name}, siz yaxshi yo'ldasiz!

📊 Hozirgi holatingiz:
• {sessions} ta sessiya
• {rating:.1f} ball reyting  
• {words or 0} ta yangi so'z

🎯 <b>Premium bilan nima o'zgaradi:</b>

📹 Professional video darslar (Recipe, SOULT)
🗣️ AI bilan koreys/yapon tilida suhbat
🧠 Grammar AI - grammatika bo'yicha maslahat
⚡ 2x tezroq o'rganish tizimi
🚫 Reklama yo'q

💡 <b>2 ta variant:</b>
💰 50,000 so'm/oy
👥 {remaining_referrals} ta referral = BEPUL oy!

Bugun boshlang: /premium
                    """
                else:  # New/less active users - basic introduction
                    message = f"""
🚀 <b>Imkoniyatlaringizni oshiring!</b>

{name}, ajoyib boshlanish!

Premium bilan nima olasiz:
🎯 Barcha premium bo'limlar
📚 Maxsus darslik va materiallar
🧠 Qo'shimcha testlar
🤖 AI yordamchi va grammatika
📊 Shaxsiy progress tahlili

💎 Tanlov sizniki:
• 50,000 so'm/oy to'lov
• 10 ta do'st taklif = bepul oy!

Sizning referral hisobingiz: {referrals or 0}/10

Bugun boshlang! /premium
                    """
                
                await bot.send_message(user_id, message.strip())
                sent_count += 1
                
                # Delay to avoid rate limits
                await asyncio.sleep(0.2)
                
            except Exception as e:
                continue
        
        print(f"Sent premium promotion messages to {sent_count} users")
        
    except Exception as e:
        print(f"Error sending premium promotion messages: {e}")

async def award_weekly_bonuses(bot: Bot):
    """Award weekly activity bonuses to users"""
    try:
        awarded_users = await calculate_weekly_bonus()
        print(f"Awarded weekly bonuses to {awarded_users} users")
        
        # Optionally notify top performers
        if awarded_users > 0:
            async with aiosqlite.connect(DATABASE_PATH) as db:
                cursor = await db.execute("""
                    SELECT user_id, first_name, rating_score
                    FROM users 
                    WHERE rating_score > 0
                    ORDER BY rating_score DESC
                    LIMIT 3
                """)
                top_users = await cursor.fetchall()
                
                for user_id, first_name, rating_score in top_users:
                    try:
                        bonus_message = f"""
🏆 <b>Haftalik bonus!</b>

Salom {first_name}! 🎉

Siz bu hafta juda faol bo'ldingiz va haftalik faollik bonusi oldingiz!

📊 Joriy reytingingiz: {rating_score:.1f}
🎯 Davom eting va eng yaxshilar orasida bo'ling!

Ko'proq o'rganing, ko'proq ball to'plang! 💪
                        """
                        await bot.send_message(user_id, bonus_message)
                        await asyncio.sleep(0.2)
                    except:
                        continue
        
    except Exception as e:
        print(f"Error awarding weekly bonuses: {e}")

async def cleanup_expired_premiums(bot: Bot):
    """Clean up expired premium subscriptions"""
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            # Get users whose premium just expired
            cursor = await db.execute("""
                SELECT user_id, first_name 
                FROM users 
                WHERE is_premium = TRUE 
                AND premium_expires_at < CURRENT_TIMESTAMP
            """)
            expired_users = await cursor.fetchall()
            
            # Update their status
            await db.execute("""
                UPDATE users 
                SET is_premium = FALSE 
                WHERE is_premium = TRUE 
                AND premium_expires_at < CURRENT_TIMESTAMP
            """)
            await db.commit()
            
            # Notify users about expiration
            for user_id, first_name in expired_users:
                try:
                    expiry_message = f"""
⏰ <b>Premium obuna tugadi!</b>

Salom {first_name}!

Sizning premium obunangiz tugadi. Premium imkoniyatlardan foydalanishni davom ettirish uchun:

💰 50,000 so'm to'lang
👥 10 ta do'stni taklif qiling

Premium obuna uchun: /premium

Rahmat! 🙏
                    """
                    await bot.send_message(user_id, expiry_message)
                    await asyncio.sleep(0.1)
                except:
                    continue
            
            print(f"Cleaned up {len(expired_users)} expired premium subscriptions")
        
    except Exception as e:
        print(f"Error cleaning up expired premiums: {e}")

async def send_engagement_reminders(bot: Bot):
    """Send reminders to inactive users"""
    try:
        # Get users inactive for 3-7 days
        three_days_ago = datetime.now() - timedelta(days=3)
        seven_days_ago = datetime.now() - timedelta(days=7)
        
        async with aiosqlite.connect(DATABASE_PATH) as db:
            cursor = await db.execute("""
                SELECT user_id, first_name, last_activity
                FROM users 
                WHERE last_activity BETWEEN ? AND ?
                AND total_sessions >= 2
                ORDER BY rating_score DESC
                LIMIT 200
            """, (seven_days_ago.isoformat(), three_days_ago.isoformat()))
            inactive_users = await cursor.fetchall()
        
        reminder_messages = [
            "👋 {name}, sizni sog'indik! Til o'rganishni davom ettiramizmi? 📚",
            "🌟 {name}, yangi darslar kutayapti! Keling, o'rganishni davom ettiraylik! 🚀",
            "📖 {name}, bilimlaringizni yangilash vaqti keldi! Testlarni ham unutmang! 🧠",
            "🎯 {name}, maqsadlaringizga erishish uchun har kun bir qadam tashlang! 💪"
        ]
        
        sent_count = 0
        for user_id, first_name, last_activity in inactive_users:
            try:
                message = random.choice(reminder_messages)
                personalized_message = message.format(name=first_name or "Do'stim")
                await bot.send_message(user_id, personalized_message)
                sent_count += 1
                await asyncio.sleep(0.2)
            except:
                continue
        
        print(f"Sent engagement reminders to {sent_count} users")
        
    except Exception as e:
        print(f"Error sending engagement reminders: {e}")

async def start_scheduler(bot: Bot):
    """Start the scheduler with all jobs"""
    
    print(f"[SCHEDULER] Starting scheduler setup...")
    print(f"[SCHEDULER] Current scheduler state: {scheduler.running}")
    
    # Check if scheduler is already running
    if scheduler.running:
        print("[SCHEDULER] Scheduler already running, skipping setup")
        return
    
    # Weekly motivational messages - every Monday at 10 AM
    scheduler.add_job(
        send_weekly_motivational_messages,
        CronTrigger(day_of_week=0, hour=MOTIVATIONAL_MESSAGE_HOUR, minute=0),
        args=[bot],
        id='weekly_motivational'
    )
    
    # Premium promotion messages - 1st and 15th of every month at 2 PM
    for day in PREMIUM_PROMOTION_DAYS:
        scheduler.add_job(
            send_premium_promotion_messages,
            CronTrigger(day=day, hour=14, minute=0),
            args=[bot],
            id=f'premium_promotion_{day}'
        )
    
    # Weekly bonuses - every Sunday at 11 PM
    scheduler.add_job(
        award_weekly_bonuses,
        CronTrigger(day_of_week=6, hour=23, minute=0),
        args=[bot],
        id='weekly_bonuses'
    )
    
    # Clean up expired premiums - daily at midnight
    scheduler.add_job(
        cleanup_expired_premiums,
        CronTrigger(hour=0, minute=30),
        args=[bot],
        id='cleanup_premiums'
    )
    
    # Engagement reminders - every Tuesday and Friday at 6 PM
    scheduler.add_job(
        send_engagement_reminders,
        CronTrigger(day_of_week='1,4', hour=18, minute=0),
        args=[bot],
        id='engagement_reminders'
    )
    
    # Start scheduler
    try:
        scheduler.start()
        print("[SCHEDULER] ✅ Scheduler started successfully with all jobs")
    except Exception as e:
        print(f"[SCHEDULER] ❌ Error starting scheduler: {e}")

async def stop_scheduler():
    """Stop the scheduler"""
    scheduler.shutdown()
    print("Scheduler stopped")
