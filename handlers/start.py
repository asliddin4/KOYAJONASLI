"""
Fixed start.py - Production ready version with all errors resolved
"""
import re
import asyncio
import aiosqlite
from datetime import datetime, timedelta
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import BOT_TOKEN, ADMIN_ID, DATABASE_PATH
from database import (
    get_user, create_user, update_user_activity, update_user_rating,
    add_referral, get_user_stats
)
from utils.subscription_check import check_subscriptions
from messages import WELCOME_MESSAGE, SUBSCRIPTION_REQUIRED_MESSAGE
from keyboards import get_main_menu, get_subscription_keyboard

router = Router()

class StartStates(StatesGroup):
    waiting_for_subscription = State()

async def process_new_referral(referrer_id: int, new_user_id: int, new_user_name: str, bot):
    """Process new referral - update count and check for premium upgrade"""
    try:
        print(f"[REFERRAL] Processing referral: {referrer_id} <- {new_user_id} ({new_user_name})")
        
        async with aiosqlite.connect(DATABASE_PATH) as db:
            # Update referrer's referral count
            await db.execute("""
                UPDATE users 
                SET referral_count = referral_count + 1 
                WHERE user_id = ?
            """, (referrer_id,))
            await db.commit()
            print(f"[REFERRAL] Updated referral count for user {referrer_id}")
            
            # Get updated referral count and referrer info
            cursor = await db.execute("""
                SELECT first_name, referral_count, is_premium 
                FROM users WHERE user_id = ?
            """, (referrer_id,))
            referrer_data = await cursor.fetchone()
            
            if not referrer_data:
                print(f"[REFERRAL] Referrer data not found for ID: {referrer_id}")
                return
                
            referrer_name, referral_count, is_premium = referrer_data
            print(f"[REFERRAL] Referrer {referrer_name} now has {referral_count} referrals")
        
        # Check if referrer reached 10 referrals and isn't already premium
        if referral_count >= 10 and not is_premium:
            # Grant premium for 30 days
            premium_expires_at = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
            
            async with aiosqlite.connect(DATABASE_PATH) as db:
                await db.execute("""
                    UPDATE users 
                    SET is_premium = 1, premium_expires_at = ?
                    WHERE user_id = ?
                """, (premium_expires_at, referrer_id))
                await db.commit()
            
            # Send premium notification
            try:
                await bot.send_message(
                    referrer_id,
                    "🎉🎉🎉 <b>TABRIKLAYMIZ!</b> 🎉🎉🎉\n\n"
                    f"👤 <b>{new_user_name}</b> sizning 10-referalingiz bo'ldi!\n\n"
                    "💎 <b>PREMIUM MUKOFOT:</b>\n"
                    "✅ 30 kunlik premium obuna berildi!\n"
                    "✅ Barcha premium bo'limlarga kirish\n"
                    "✅ Maxsus materiallar va testlar\n"
                    "✅ AI suhbat bilan amaliyot\n\n"
                    f"🗓 Muddat: {premium_expires_at.split()[0]} gacha\n\n"
                    "🚀 Premium imkoniyatlardan foydalaning!",
                    parse_mode="HTML"
                )
                print(f"[REFERRAL] Premium notification sent to {referrer_id}")
            except Exception as e:
                print(f"[REFERRAL] Failed to send premium notification: {e}")
                
            # Reset referral count for next reward cycle
            async with aiosqlite.connect(DATABASE_PATH) as db:
                await db.execute("""
                    UPDATE users 
                    SET referral_count = 0 
                    WHERE user_id = ?
                """, (referrer_id,))
                await db.commit()
                
        else:
            # Send regular referral notification
            remaining_referrals = max(0, 10 - referral_count)
            try:
                await bot.send_message(
                    referrer_id,
                    f"🎉 <b>Yangi referral!</b>\n\n"
                    f"👤 <b>{new_user_name}</b> sizning taklifingiz bilan qo'shildi!\n\n"
                    f"📊 <b>Referral hisobi:</b>\n"
                    f"✅ Hozirgi: {referral_count}/10\n"
                    f"⏳ Qolgan: {remaining_referrals} ta\n\n"
                    f"💎 {remaining_referrals} ta referral qoldi va 1 oy bepul premium olasiz!",
                    parse_mode="HTML"
                )
                print(f"[REFERRAL] Notification sent to {referrer_id}: {referral_count}/10 referrals")
            except Exception as e:
                print(f"[REFERRAL] Failed to send notification: {e}")
                
    except Exception as e:
        print(f"Referral processing error: {e}")

@router.message(CommandStart())
async def start_command(message: Message, state: FSMContext):
    if not message.from_user:
        return
    user_id = message.from_user.id
    
    # Check if user exists
    user = await get_user(user_id)
    
    # Handle referral code
    referred_by = None
    if message.text and len(message.text.split()) > 1:
        referral_param = message.text.split()[1]
        print(f"[REFERRAL DEBUG] Raw parameter: {referral_param}")
        
        # Handle ref_USERID format
        if referral_param.startswith("ref_"):
            try:
                referrer_id = int(referral_param.replace("ref_", ""))
                print(f"[REFERRAL DEBUG] Extracted referrer ID: {referrer_id}")
                
                # Verify referrer exists
                async with aiosqlite.connect(DATABASE_PATH) as db:
                    cursor = await db.execute(
                        "SELECT user_id, first_name FROM users WHERE user_id = ?", 
                        (referrer_id,)
                    )
                    referrer = await cursor.fetchone()
                    if referrer:
                        referred_by = referrer[0]
                        print(f"[REFERRAL DEBUG] Valid referrer found: {referrer[1]} (ID: {referrer_id})")
                    else:
                        print(f"[REFERRAL DEBUG] Referrer not found in database: {referrer_id}")
            except ValueError:
                print(f"[REFERRAL DEBUG] Invalid referrer ID format: {referral_param}")
    
    # Create user if doesn't exist
    if not user:
        await create_user(
            user_id=user_id,
            username=message.from_user.username or "",
            first_name=message.from_user.first_name or "",
            last_name=message.from_user.last_name or "",
            referred_by=referred_by
        )
        
        # Add referral record if user was referred
        if referred_by:
            print(f"[REFERRAL DEBUG] Processing referral: {referred_by} -> {user_id}")
            try:
                await add_referral(referred_by, user_id)
                await process_new_referral(referred_by, user_id, message.from_user.first_name or "Anonim", message.bot)
                print(f"[REFERRAL DEBUG] Referral processed successfully")
            except Exception as e:
                print(f"[REFERRAL DEBUG] Error processing referral: {e}")
    
    # Update user activity
    await update_user_activity(user_id)
    await update_user_rating(user_id, 'session_start')
    
    # Show main menu directly (subscription check disabled)
    await message.answer(
        WELCOME_MESSAGE.format(
            first_name=message.from_user.first_name or "Foydalanuvchi"
        ),
        reply_markup=get_main_menu(user_id == ADMIN_ID)
    )

# Safe callback handlers with message checks
@router.callback_query(F.data == "main_menu")
async def main_menu_callback(callback: CallbackQuery):
    if not callback.message or not callback.from_user:
        await callback.answer("Xatolik yuz berdi!")
        return
        
    user_id = callback.from_user.id
    
    try:
        await callback.message.edit_text(
            WELCOME_MESSAGE.format(
                first_name=callback.from_user.first_name or "Foydalanuvchi"
            ),
            reply_markup=get_main_menu(user_id == ADMIN_ID)
        )
    except Exception as e:
        print(f"Error editing message: {e}")
        await callback.answer("Menyu yangilandi!")

@router.callback_query(F.data == "premium")
async def premium_menu(callback: CallbackQuery):
    if not callback.message or not callback.from_user:
        await callback.answer("Xatolik yuz berdi!")
        return
        
    user_id = callback.from_user.id
    user_stats = await get_user_stats(user_id)
    
    if not user_stats:
        await callback.answer("❌ Foydalanuvchi ma'lumotlari topilmadi!")
        return
    
    # Safe tuple unpacking
    is_premium = user_stats[4] if len(user_stats) > 4 else False
    referral_count = user_stats[5] if len(user_stats) > 5 else 0
    
    if is_premium:
        premium_text = """💎 <b>PREMIUM FOYDALANUVCHI</b>

✅ Premium status faol
🎯 Barcha funksiyalar ochiq
🚀 Cheksiz foydalanish

<b>Premium imkoniyatlar:</b>
• 🤖 AI suhbat (Korean/Japanese)
• 📚 Premium bo'limlar
• 🎯 Maxsus testlar
• 📈 Kengaytirilgan statistika"""
        
        premium_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🤖 AI Suhbat", callback_data="ai_conversation")],
            [InlineKeyboardButton(text="👥 Referral dasturi", callback_data="referral_program")],
            [InlineKeyboardButton(text="📊 Statistika", callback_data="rating")],
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="main_menu")]
        ])
    else:
        remaining_referrals = max(0, 10 - referral_count)
        premium_text = f"""💎 <b>PREMIUM OBUNA</b>

🚀 <b>Premium imkoniyatlar:</b>
• 🤖 AI suhbat (Korean/Japanese)
• 📚 Premium bo'limlar 
• 🎯 Maxsus testlar
• 📈 Kengaytirilgan statistika

💰 <b>Narx:</b> 50,000 som/oy

🆓 <b>BEPUL OLISH:</b>
Referral: {referral_count}/10
{remaining_referrals} ta qoldi = BEPUL Premium!"""
        
        premium_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💳 Premium sotib olish", callback_data="premium_purchase")],
            [InlineKeyboardButton(text="👥 Referral dasturi", callback_data="referral_program")],
            [InlineKeyboardButton(text="ℹ️ Referral ma'lumot", callback_data="referral_info")],
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="main_menu")]
        ])
    
    try:
        await callback.message.edit_text(
            premium_text,
            reply_markup=premium_keyboard,
            parse_mode="HTML"
        )
    except Exception as e:
        print(f"Error editing premium message: {e}")
    
    await callback.answer()

@router.callback_query(F.data == "referral_program")
async def handle_referral_program(callback: CallbackQuery):
    if not callback.message or not callback.from_user:
        await callback.answer("Xatolik!")
        return
        
    user_id = callback.from_user.id
    username = callback.from_user.username or "user"
    
    user_stats = await get_user_stats(user_id)
    referral_count = user_stats[5] if user_stats and len(user_stats) > 5 else 0
    remaining_referrals = max(0, 10 - referral_count)
    
    referral_text = f"""👥 <b>REFERRAL DASTURI - Bepul Premium!</b>

🎯 <b>SIZNING HOLATINGIZ:</b>
• Hozirgi referrallar: {referral_count}/10
• Kerak: yana {remaining_referrals} ta
• Progress: {'█' * referral_count}{'░' * remaining_referrals}

🚀 <b>QANDAY ISHLAYDI:</b>

1️⃣ <b>Referral havolangiz:</b>
`https://t.me/KoreYap_ProGradBot?start=ref_{user_id}`

2️⃣ <b>Ulashing:</b>
• Do'stlaringizga yuboring
• Social media da e'lon qiling  
• Telegram guruhlariga tashlang

3️⃣ <b>Natija:</b>
• Har yangi a'zo = +1 referral
• 10 referral = 30 kun BEPUL Premium!

💰 <b>QIYMAT:</b> 50,000 som tejash"""

    referral_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Havolani nusxalash", callback_data="copy_referral_link")],
        [InlineKeyboardButton(text="📊 Referral statistika", callback_data="referral_stats")],
        [InlineKeyboardButton(text="🎁 Mukofotlarim", callback_data="my_rewards")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="premium")]
    ])
    
    try:
        await callback.message.edit_text(
            referral_text,
            reply_markup=referral_keyboard, 
            parse_mode="HTML"
        )
    except Exception as e:
        print(f"Error editing referral message: {e}")
    
    await callback.answer()

# Minimal handlers for other callbacks
@router.callback_query(F.data == "copy_referral_link")
async def handle_copy_referral_link(callback: CallbackQuery):
    """Referral havolasini ko'rsatish"""
    if not callback.message or not callback.from_user:
        await callback.answer("Xatolik!")
        return
        
    user_id = callback.from_user.id
    referral_link = f"https://t.me/KoreYap_ProGradBot?start=ref_{user_id}"
    
    copy_text = f"""📋 <b>SIZNING REFERRAL HAVOLANGIZ:</b>

<code>{referral_link}</code>

🚀 <b>ULASHISH YO'LLARI:</b>

📱 <b>Telegram:</b>
• Do'stlar bilan shaxsiy chat
• Familiya guruhlari  
• Til o'rganuvchi guruhlar

🌐 <b>Ijtimoiy tarmoqlar:</b>
• Instagram story/post
• Facebook ulashish
• TikTok bio/comment

💡 <b>Maslahat:</b> "Men koreys/yapon tili o'rganaman. Sizga ham tavsiya qilaman!" deb yozing va havolani qo'shing.

🎯 <b>Har yangi a'zo = +1 referral</b>
💎 <b>10 referral = 30 kun BEPUL Premium!</b>"""

    copy_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Referral menu", callback_data="referral_program")]
    ])
    
    try:
        await callback.message.edit_text(
            copy_text,
            reply_markup=copy_keyboard,
            parse_mode="HTML"
        )
    except Exception as e:
        print(f"Error editing copy referral message: {e}")
    
    await callback.answer("📋 Havola tayyor! Nusxalang va ulashing!", show_alert=True)

@router.callback_query(F.data == "referral_stats")
async def handle_referral_stats(callback: CallbackQuery):
    """Referral statistikasini ko'rsatish"""
    if not callback.message or not callback.from_user:
        await callback.answer("Xatolik!")
        return
        
    user_id = callback.from_user.id
    user_stats = await get_user_stats(user_id)
    
    if not user_stats:
        await callback.answer("❌ Ma'lumot topilmadi!")
        return
    
    referral_count = user_stats[5] if len(user_stats) > 5 else 0
    remaining = max(0, 10 - referral_count)
    progress_bar = "█" * referral_count + "░" * remaining
    
    # Get detailed referral info
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("""
            SELECT r.referred_id, u.first_name, r.created_at 
            FROM referrals r 
            LEFT JOIN users u ON r.referred_id = u.user_id 
            WHERE r.referrer_id = ? 
            ORDER BY r.created_at DESC 
            LIMIT 10
        """, (user_id,))
        referrals = await cursor.fetchall()
    
    stats_text = f"""📊 <b>REFERRAL STATISTIKA</b>

🎯 <b>SIZNING NATIJALRINGIZ:</b>
• Umumiy referrallar: {referral_count}/10
• Qolgan: {remaining} ta
• Progress: {progress_bar}

📈 <b>MUKOFOT HISOBI:</b>
• Hozirgi sikl: {referral_count}/10
• Keyingi premium: {remaining} ta qoldi
• Maqsad: 50,000 som tejash

👥 <b>OXIRGI REFERRALLAR:</b>"""
    
    if referrals:
        for i, (ref_id, name, created_at) in enumerate(referrals[:5], 1):
            user_name = name or "Anonim"
            date = created_at.split()[0] if created_at else "Noma'lum"
            stats_text += f"\n{i}. {user_name} - {date}"
    else:
        stats_text += "\nHali referrallar yo'q"
    
    stats_text += f"""

💡 <b>KEYINGI QADAM:</b>
Yana {remaining} kishi taklif qiling va 30 kunlik BEPUL Premium oling!"""

    stats_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Havola nusxalash", callback_data="copy_referral_link")],
        [InlineKeyboardButton(text="🔙 Referral menu", callback_data="referral_program")]
    ])
    
    try:
        await callback.message.edit_text(
            stats_text,
            reply_markup=stats_keyboard,
            parse_mode="HTML"
        )
    except Exception as e:
        print(f"Error editing referral stats message: {e}")
    
    await callback.answer()

@router.callback_query(F.data == "my_rewards")
async def handle_my_rewards(callback: CallbackQuery):
    """Foydalanuvchi mukofotlarini ko'rsatish"""
    if not callback.message or not callback.from_user:
        await callback.answer("Xatolik!")
        return
        
    user_id = callback.from_user.id
    user_stats = await get_user_stats(user_id)
    
    if not user_stats:
        await callback.answer("❌ Ma'lumot topilmadi!")
        return
    
    referral_count = user_stats[5] if len(user_stats) > 5 else 0
    is_premium = user_stats[4] if len(user_stats) > 4 else False
    premium_expires = user_stats[6] if len(user_stats) > 6 else None
    
    rewards_text = f"""🎁 <b>SIZNING MUKOFOTLARINGIZ</b>

📊 <b>JORIY HOLAT:</b>
• Referral hisobi: {referral_count}/10
• Premium status: {'✅ Faol' if is_premium else '❌ Yoq'}"""

    if is_premium and premium_expires:
        rewards_text += f"\n• Premium tugashi: {premium_expires.split()[0]}"
    
    rewards_text += f"""

🏆 <b>OLGAN MUKOFOTLAR:</b>"""
    
    # Calculate completed cycles (how many times user got 10 referrals)
    completed_cycles = referral_count // 10 if referral_count >= 10 else 0
    if is_premium:
        completed_cycles += 1  # Current premium
    
    if completed_cycles > 0:
        rewards_text += f"\n✅ {completed_cycles} marta 30 kunlik Premium olgan"
        rewards_text += f"\n💰 Jami tejagan: {completed_cycles * 50000:,} som"
    else:
        rewards_text += "\nHali mukofotlar yo'q"
    
    remaining = max(0, 10 - (referral_count % 10))
    rewards_text += f"""

🎯 <b>KEYINGI MUKOFOT:</b>
• Qolgan referrallar: {remaining}/10
• Keyingi mukofot: 30 kun Premium (50,000 som)
• Foiz: {((referral_count % 10) / 10 * 100):.0f}%

🚀 <b>MOTIVATSIYA:</b>
Har yangi referral sizni premium mukofotga yaqinlashtiradi!"""

    rewards_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👥 Referral to'plash", callback_data="copy_referral_link")],
        [InlineKeyboardButton(text="📊 Statistika", callback_data="referral_stats")],
        [InlineKeyboardButton(text="🔙 Referral menu", callback_data="referral_program")]
    ])
    
    try:
        await callback.message.edit_text(
            rewards_text,
            reply_markup=rewards_keyboard,
            parse_mode="HTML"
        )
    except Exception as e:
        print(f"Error editing rewards message: {e}")
    
    await callback.answer()

@router.callback_query(F.data.startswith("premium_purchase"))
async def handle_premium_purchase(callback: CallbackQuery):
    if not callback.message or not callback.from_user:
        await callback.answer("Xatolik!")
        return
        
    user_id = callback.from_user.id
    username = callback.from_user.username or "user"
    
    purchase_text = f"""💎 <b>PREMIUM SOTIB OLISH</b>

🌟 <b>PREMIUM IMKONIYATLARI:</b>
• AI Suhbat (Korean & Japanese)
• JLPT testlar (N5-N1)
• Premium kontentlar
• Reklama yo'q
• Prioritet yordam

💰 <b>NARX:</b> 50,000 som (30 kun)
📊 <b>Kuniga:</b> 1,667 som

💳 <b>TO'LOV USULLARI:</b>

🏦 <b>Karta orqali:</b>
<code>4278 3100 2775 4068</code>
Xoshimjon Mamadiyev
(Kapital Bank Visa)

📱 <b>Elektron to'lovlar:</b>
• Click/Payme: +998917754441
• Humo/Uzcard: 8600 4954 7441 7777

💸 <b>Naqd pul:</b>
Janubiy Koreya, Seul/Inchon
@Chang_chi_won admin bilan bog'laning

⚠️ <b>MUHIM:</b> To'lovdan keyin skrinshot yuboring!"""

    purchase_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Karta ma'lumotini nusxalash", callback_data="copy_card_info")],
        [InlineKeyboardButton(text="📱 Click/Payme raqam", callback_data="copy_click_number")],
        [InlineKeyboardButton(text="💸 Humo/Uzcard raqam", callback_data="copy_humo_number")],
        [InlineKeyboardButton(text="📸 To'lov tasdiqini yuborish", callback_data="send_payment_proof")],
        [InlineKeyboardButton(text="👨‍💼 Admin bilan bog'lanish", url="https://t.me/Chang_chi_won")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="premium")]
    ])
    
    try:
        await callback.message.edit_text(
            purchase_text,
            reply_markup=purchase_keyboard,
            parse_mode="HTML"
        )
    except Exception as e:
        print(f"Error showing premium purchase: {e}")
    
    await callback.answer()

@router.callback_query(F.data.startswith("copy_card_info"))
async def handle_copy_card_info(callback: CallbackQuery):
    await callback.answer("💳 Karta ma'lumoti nusxalandi:\n4278 3100 2775 4068\nXoshimjon Mamadiyev", show_alert=True)

@router.callback_query(F.data.startswith("copy_click_number"))
async def handle_copy_click_number(callback: CallbackQuery):
    await callback.answer("📱 Click/Payme raqam nusxalandi:\n+998917754441", show_alert=True)

@router.callback_query(F.data.startswith("copy_humo_number"))
async def handle_copy_humo_number(callback: CallbackQuery):
    await callback.answer("💸 Humo/Uzcard raqam nusxalandi:\n8600 4954 7441 7777", show_alert=True)

@router.callback_query(F.data.startswith("send_payment_proof"))
async def handle_send_payment_proof(callback: CallbackQuery):
    if not callback.message or not callback.from_user:
        await callback.answer("Xatolik!")
        return
    
    proof_text = """📸 <b>TO'LOV TASDIQINI YUBORISH</b>

📋 <b>Qanday yuborish:</b>
1. To'lov skrinshot tayyorlang
2. @Chang_chi_won admin ga yuboring
3. Username va ID ni ham yuboring

👤 <b>Sizning ma'lumotlaringiz:</b>
• ID: <code>{}</code>
• Username: @{}

⏰ <b>Tasdiqlash vaqti:</b> 1-24 soat

✅ <b>Tasdiqlangandan keyin Premium avtomatik faollashadi!</b>"""

    try:
        await callback.message.edit_text(
            proof_text.format(callback.from_user.id, callback.from_user.username or "none"),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="👨‍💼 Admin ga yozish", url="https://t.me/Chang_chi_won")],
                [InlineKeyboardButton(text="🔙 Orqaga", callback_data="premium_purchase")]
            ]),
            parse_mode="HTML"
        )
    except Exception as e:
        print(f"Error showing payment proof info: {e}")
    
    await callback.answer()

@router.callback_query(F.data == "referral_info")
async def handle_referral_info(callback: CallbackQuery):
    if not callback.message or not callback.from_user:
        await callback.answer("Xatolik!")
        return
        
    user_id = callback.from_user.id
    user_stats = await get_user_stats(user_id)
    referral_count = user_stats[5] if user_stats and len(user_stats) > 5 else 0
    remaining_referrals = max(0, 10 - referral_count)
    
    info_text = f"""ℹ️ <b>REFERRAL DASTURI MA'LUMOT</b>

💰 <b>QIYMAT HISOB-KITOBI:</b>
• Premium narx: 50,000 som/oy  
• 10 referral = BEPUL 1 oy
• Sizning tejashingiz: 50,000 som!

🎯 <b>SIZNING HOLATINGIZ:</b>
• Hozir: {referral_count}/10 referral
• Qolgan: {remaining_referrals} ta 
• Tejash imkoniyati: {50000 if remaining_referrals == 0 else 0:,} som

🚀 <b>TEZKOR TO'PLASH USULLARI:</b>

📱 <b>Telegram:</b>
• Do'stlar/qarindoshlar guruhida ulashing
• Til o'rganish guruhlariga tashlang
• Shaxsiy chatda yuboring

🌐 <b>Social Media:</b>
• Instagram story/post
• Facebook ulashing
• WhatsApp status

🎭 <b>Tavsiya matni:</b>
"Men koreys/yapon tili o'rganaman va juda yaxshi natija berib turibdi! Sizga ham tavsiya qilaman - bepul boshlash mumkin!"

💡 <b>Pro maslahat:</b>
Guruhlarda faol bo'ling, foydali kontent ulashing, keyin taklifingizni qo'shing."""

    info_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Havolani olish", callback_data="copy_referral_link")],
        [InlineKeyboardButton(text="📊 Mening statistikam", callback_data="referral_stats")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="premium")]
    ])
    
    try:
        await callback.message.edit_text(
            info_text,
            reply_markup=info_keyboard,
            parse_mode="HTML"
        )
    except Exception as e:
        print(f"Error editing referral info message: {e}")
    
    await callback.answer()

@router.callback_query(F.data == "rating")
async def handle_rating(callback: CallbackQuery):
    if not callback.message or not callback.from_user:
        await callback.answer("Xatolik!")
        return
        
    user_id = callback.from_user.id
    user_stats = await get_user_stats(user_id)
    
    if not user_stats:
        await callback.answer("❌ Foydalanuvchi ma'lumotlari topilmadi!")
        return
    
    try:
        # Show user statistics
        rating, total_sessions, words_learned = user_stats[1], user_stats[2], user_stats[3]
        is_premium = user_stats[4] if len(user_stats) > 4 else False
        referral_count = user_stats[5] if len(user_stats) > 5 else 0
        
        stats_text = f"""📊 <b>SIZNING STATISTIKANGIZ</b>

🌟 <b>Reyting:</b> {rating} ball
📚 <b>Sessiyalar:</b> {total_sessions} ta
📖 <b>O'rganilgan so'zlar:</b> {words_learned} ta
💎 <b>Status:</b> {"Premium" if is_premium else "Oddiy"}
👥 <b>Referrallar:</b> {referral_count}/10

📈 <b>O'sish dinamikasi:</b>
• Har sessiya: +2 ball
• Har test: +5 ball  
• AI suhbat: +1.5 ball/xabar
• Quiz yechish: +3 ball

🎯 <b>Keyingi maqsad:</b>
{"Premium imkoniyatlardan foydalaning!" if is_premium else f"{10-referral_count} ta referral qoldi = Premium!"}"""

        stats_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="👥 Referral dasturi", callback_data="referral_program")] if not is_premium else [],
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="premium")]
        ])

        await callback.message.edit_text(
            stats_text,
            reply_markup=stats_keyboard,
            parse_mode="HTML"
        )
    except Exception as e:
        print(f"Error showing statistics: {e}")
        await callback.answer("Statistika yuklanmoqda...")
    
    await callback.answer()

@router.callback_query(F.data == "conversation")
async def handle_ai_conversation(callback: CallbackQuery):
    if not callback.message or not callback.from_user:
        await callback.answer("Xatolik!")
        return
        
    user_id = callback.from_user.id
    user_stats = await get_user_stats(user_id)
    
    if not user_stats:
        await callback.answer("❌ Foydalanuvchi ma'lumotlari topilmadi!")
        return
    
    # Check premium status
    is_premium = user_stats[4] if len(user_stats) > 4 else False
    
    if not is_premium:
        try:
            await callback.message.edit_text(
                "🤖 <b>AI Suhbat - Premium Xizmat</b>\n\n"
                "🌟 <b>Premium AI bilan suhbat:</b>\n"
                "• Korean va Japanese AI chat\n"
                "• 12,000+ so'z lug'ati\n"
                "• Real-time conversation\n"
                "• Har xabar uchun +1.5 reyting\n\n"
                "💎 <b>Premium kerak:</b>\n"
                "50,000 som/oy yoki 10 referral\n\n"
                "🎯 <b>Premium oling va AI bilan suhbatlashing!</b>",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="💳 Premium sotib olish", callback_data="premium_purchase")],
                    [InlineKeyboardButton(text="👥 Referral to'plash", callback_data="referral_program")],
                    [InlineKeyboardButton(text="🔙 Orqaga", callback_data="premium")]
                ]),
                parse_mode="HTML"
            )
        except Exception as e:
            print(f"Error showing AI conversation premium message: {e}")
        
        await callback.answer("💎 Premium kerak!")
        return
    
    # Premium user - show AI conversation options
    try:
        await callback.message.edit_text(
            "🤖 <b>AI SUHBAT - Premium</b>\n\n"
            "🌟 <b>Til tanlang:</b>\n"
            "• Korean AI - 12,000+ so'z\n"
            "• Japanese AI - 12,000+ so'z\n"
            "• Interactive conversation\n"
            "• Har xabar +1.5 reyting\n\n"
            "🚀 <b>Qaysi AI bilan suhbatlashmoqchisiz?</b>",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🇰🇷 Korean AI", callback_data="korean_conversation")],
                [InlineKeyboardButton(text="🇯🇵 Japanese AI", callback_data="japanese_conversation")],
                [InlineKeyboardButton(text="💡 Conversation tips", callback_data="conversation_tips")],
                [InlineKeyboardButton(text="🔙 Orqaga", callback_data="premium")]
            ]),
            parse_mode="HTML"
        )
    except Exception as e:
        print(f"Error showing AI conversation options: {e}")
    
    await callback.answer()

# Additional conversation handlers
@router.callback_query(F.data == "korean_conversation")
async def handle_korean_conversation(callback: CallbackQuery):
    if not callback.message or not callback.from_user:
        await callback.answer("Xatolik!")
        return
    
    await callback.message.edit_text(
        "🇰🇷 <b>Korean AI Chat</b>\n\n"
        "안녕하세요! Korean AI bilan suhbatlashishga tayyor!\n\n"
        "💬 Menga korean tilida yoki o'zbek tilida yozing\n"
        "🎯 Har xabar uchun +1.5 reyting ball\n"
        "📚 12,000+ korean so'z lug'ati\n\n"
        "Suhbatni boshlash uchun biror narsa yozing:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 AI Menyuga", callback_data="ai_conversation")]
        ]),
        parse_mode="HTML"
    )
    await callback.answer("🇰🇷 Korean AI faollashtirildi!")

@router.callback_query(F.data == "japanese_conversation") 
async def handle_japanese_conversation(callback: CallbackQuery):
    if not callback.message or not callback.from_user:
        await callback.answer("Xatolik!")
        return
    
    await callback.message.edit_text(
        "🇯🇵 <b>Japanese AI Chat</b>\n\n"
        "こんにちは! Japanese AI bilan suhbatlashishga tayyor!\n\n"
        "💬 Menga japanese tilida yoki o'zbek tilida yozing\n"
        "🎯 Har xabar uchun +1.5 reyting ball\n"
        "📚 12,000+ japanese so'z lug'ati\n\n"
        "Suhbatni boshlash uchun biror narsa yozing:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 AI Menyuga", callback_data="ai_conversation")]
        ]),
        parse_mode="HTML"
    )
    await callback.answer("🇯🇵 Japanese AI faollashtirildi!")

@router.callback_query(F.data == "conversation_tips")
async def handle_conversation_tips(callback: CallbackQuery):
    if not callback.message or not callback.from_user:
        await callback.answer("Xatolik!")
        return
    
    await callback.message.edit_text(
        "💡 <b>AI Suhbat Maslahatlar</b>\n\n"
        "🎯 <b>Qanday yozish kerak:</b>\n"
        "• Odatiy savol: \"Salom qalaysiz?\"\n"
        "• Grammar: \"Nima deb deyiladi?\"\n"
        "• Tarjima: \"Bu so'z nima degani?\"\n"
        "• Kultur: \"Korean odatlari haqida\"\n\n"
        "⭐ <b>AI sizga yordam beradi:</b>\n"
        "• Pronunciation guide\n"
        "• Grammar correction\n"
        "• Cultural context\n"
        "• Vocabulary expansion\n\n"
        "🚀 <b>Yaxshi natija uchun:</b>\n"
        "• To'liq gaplar yozing\n"
        "• Savol bering\n"
        "• Amaliyot qiling",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 AI Menyuga", callback_data="ai_conversation")]
        ]),
        parse_mode="HTML"
    )
    await callback.answer() 
