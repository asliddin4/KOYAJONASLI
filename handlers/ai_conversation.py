from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import asyncio

from database import get_user, is_premium_active, update_user_rating
from utils.ai_conversation_advanced import get_korean_response, get_japanese_response

router = Router()

class ConversationStates(StatesGroup):
    korean_chat = State()
    japanese_chat = State()

# AI instances imported from advanced module

@router.callback_query(F.data == "conversation")
async def show_conversation_menu(callback: CallbackQuery):
    """Premium AI suhbat menu"""
    try:
        user_id = callback.from_user.id
        user = await get_user(user_id)
        
        # Premium foydalanuvchi tekshiruvi
        is_premium = await is_premium_active(user_id) if user else False
        
        if not is_premium:
            # Premium reklama xabari
            premium_ad_text = """🤖 <b>AI bilan suhbat - Premium xizmat</b>

🌟 <b>PREMIUM AI BILAN SUHBAT AFZALLIKLARI:</b>

🧠 <b>Haqiqiy AI tajriba:</b>
• Sizni tushunuvchi va javob beruvchi AI
• Kores va yapon tillarida professional suhbat
• 12,000+ so'z va ibora lug'ati
• Cultural awareness va context understanding

💎 <b>Exclusive Premium foydalari:</b>
• Cheksiz AI suhbat sessiyalari
• Har xabar uchun +1.5 reyting ball
• Personal AI language tutor
• 24/7 mavjudlik va tez javob

🚀 <b>Til o'rganishda super tezlik:</b>
• Interactive conversation practice
• Real-time grammar correction
• Vocabulary expansion
• Pronunciation guidance

📈 <b>Progress tracking:</b>
• Sizning til darajangizni kuzatadi
• Individual learning path
• Achievement system
• Weekly progress reports

💰 <b>Premium obuna:</b>
• Oyiga 50,000 som
• Yoki 10 ta referral = 1 oy bepul
• Premium content access
• AI conversation unlimited

🎯 <b>Natija kafolati:</b>
• 30 kun ichida sezilarli o'sish
• Professional conversation skills
• Native speaker confidence level
• Sertifikat olish imkoniyati"""

            premium_keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="💎 Premium sotib olish", callback_data="premium")
                ],
                [
                    InlineKeyboardButton(text="👥 10 Referral to'plash", callback_data="referral_program")
                ],
                [
                    InlineKeyboardButton(text="🔙 Bosh menu", callback_data="main_menu")
                ]
            ])
            
            if callback.message:
                await callback.message.edit_text(
                    premium_ad_text,
                    reply_markup=premium_keyboard,
                    parse_mode="HTML"
                )
            await callback.answer()
            return
        
        # Premium foydalanuvchi uchun AI menu
        ai_menu_text = """🤖 <b>AI bilan suhbat - Premium</b>

🎯 <b>Qaysi AI bilan suhbatlashmoqchisiz?</b>

🇰🇷 <b>Korean AI:</b>
• 12,000+ korean so'z va ibora
• Grammar patterns va cultural topics
• Real-time korean conversation

🇯🇵 <b>Japanese AI:</b>
• 12,000+ japanese so'z (hiragana, katakana, kanji)
• Authentic japanese expressions
• Cultural awareness

💡 <b>Foyda:</b> Har xabaringiz uchun +1.5 reyting ball!"""

        ai_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🇰🇷 Korean AI", callback_data="korean_conversation"),
                InlineKeyboardButton(text="🇯🇵 Japanese AI", callback_data="japanese_conversation")
            ],
            [
                InlineKeyboardButton(text="🔙 Bosh menu", callback_data="main_menu")
            ]
        ])
        
        if callback.message:
            await callback.message.edit_text(
                ai_menu_text,
                reply_markup=ai_keyboard,
                parse_mode="HTML"
            )
        await callback.answer()
        
    except Exception as e:
        print(f"AI conversation menu error: {e}")
        await callback.answer("❌ Xatolik yuz berdi!")

@router.callback_query(F.data == "korean_conversation")
async def start_korean_conversation(callback: CallbackQuery, state: FSMContext):
    """Korean AI bilan suhbatni boshlash"""
    try:
        user_id = callback.from_user.id
        is_premium = await is_premium_active(user_id)
        
        if not is_premium:
            await callback.answer("❌ Premium kerak!", show_alert=True)
            return
        
        await state.set_state(ConversationStates.korean_chat)
        
        welcome_text = """🇰🇷 <b>Korean AI bilan suhbat boshlandi!</b>

안녕하세요! 저는 여러분의 한국어 선생님입니다! 🎓

🎯 <b>Qanday gaplashishingiz mumkin:</b>
• Koreyscha yozing - men koreyscha javob beraman
• O'zbekcha yozing - men tushunib, koreyscha o'rgataman
• "음식" (ovqat), "가족" (oila) kabi mavzularni muhokama qiling

💡 <b>Maslahat:</b> "안녕하세요" deb boshlang!

📝 <b>Har xabaringiz uchun +1.5 reyting ball olasiz!</b>

Koreyscha nima demoqchisiz? 🇰🇷✨"""

        exit_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="❌ Suhbatni tugatish", callback_data="end_conversation")
            ]
        ])
        
        if callback.message:
            await callback.message.edit_text(
                welcome_text,
                reply_markup=exit_keyboard,
                parse_mode="HTML"
            )
        await callback.answer()
        
    except Exception as e:
        print(f"Start Korean AI error: {e}")
        await callback.answer("❌ Xatolik!")

@router.callback_query(F.data == "japanese_conversation")
async def start_japanese_conversation(callback: CallbackQuery, state: FSMContext):
    """Japanese AI bilan suhbatni boshlash"""
    try:
        user_id = callback.from_user.id
        is_premium = await is_premium_active(user_id)
        
        if not is_premium:
            await callback.answer("❌ Premium kerak!", show_alert=True)
            return
        
        await state.set_state(ConversationStates.japanese_chat)
        
        welcome_text = """🇯🇵 <b>Japanese AI bilan suhbat boshlandi!</b>

こんにちは！私はあなたの日本語の先生です！🎓

🎯 <b>Qanday gaplashishingiz mumkin:</b>
• Yaponcha yozing - men yaponcha javob beraman
• O'zbekcha yozing - men tushunib, yaponcha o'rgataman
• "食べ物" (tabemono - ovqat), "家族" (kazoku - oila) mavzularni muhokama qiling

💡 <b>Maslahat:</b> "こんにちは" (konnichiha) deb boshlang!

📝 <b>Har xabaringiz uchun +1.5 reyting ball olasiz!</b>

Yaponcha nima demoqchisiz? 🇯🇵✨"""

        exit_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="❌ Suhbatni tugatish", callback_data="end_conversation")
            ]
        ])
        
        if callback.message:
            await callback.message.edit_text(
                welcome_text,
                reply_markup=exit_keyboard,
                parse_mode="HTML"
            )
        await callback.answer()
        
    except Exception as e:
        print(f"Start Japanese AI error: {e}")
        await callback.answer("❌ Xatolik!")

@router.message(ConversationStates.korean_chat)
async def handle_korean_conversation(message: Message, state: FSMContext):
    """Korean AI bilan suhbat"""
    try:
        user_id = message.from_user.id
        user_message = message.text
        
        if not user_message:
            await message.reply("❌ Faqat matn yuboring!")
            return
        
        # Premium tekshiruvi
        is_premium = await is_premium_active(user_id)
        if not is_premium:
            await message.reply("❌ Premium obuna kerak!")
            await state.clear()
            return
        
        # Typing animation
        if message.bot and message.chat:
            await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
        await asyncio.sleep(1)  # Thinking delay
        
        # AI javob olish
        ai_response = await korean_ai.generate_response(user_message, user_id)
        
        # Reyting yangilash (+1.5 ball)
        await update_user_rating(user_id, 1.5)
        
        # Exit keyboard
        exit_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="❌ Suhbatni tugatish", callback_data="end_conversation")
            ]
        ])
        
        await message.reply(
            f"{ai_response}\n\n<b>💎 +1.5 reyting ball!</b>",
            reply_markup=exit_keyboard,
            parse_mode="HTML"
        )
        
    except Exception as e:
        print(f"Korean conversation error: {e}")
        await message.reply("❌ Xatolik yuz berdi!")

@router.message(ConversationStates.japanese_chat)
async def handle_japanese_conversation(message: Message, state: FSMContext):
    """Japanese AI bilan suhbat"""
    try:
        user_id = message.from_user.id
        user_message = message.text
        
        if not user_message:
            await message.reply("❌ Faqat matn yuboring!")
            return
        
        # Premium tekshiruvi
        is_premium = await is_premium_active(user_id)
        if not is_premium:
            await message.reply("❌ Premium obuna kerak!")
            await state.clear()
            return
        
        # Typing animation
        if message.bot and message.chat:
            await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
        await asyncio.sleep(1)  # Thinking delay
        
        # AI javob olish
        ai_response = await japanese_ai.generate_response(user_message, user_id)
        
        # Reyting yangilash (+1.5 ball)
        await update_user_rating(user_id, 1.5)
        
        # Exit keyboard
        exit_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="❌ Suhbatni tugatish", callback_data="end_conversation")
            ]
        ])
        
        await message.reply(
            f"{ai_response}\n\n<b>💎 +1.5 reyting ball!</b>",
            reply_markup=exit_keyboard,
            parse_mode="HTML"
        )
        
    except Exception as e:
        print(f"Japanese conversation error: {e}")
        await message.reply("❌ Xatolik yuz berdi!")

@router.callback_query(F.data == "end_conversation")
async def end_conversation(callback: CallbackQuery, state: FSMContext):
    """Suhbatni tugatish"""
    try:
        await state.clear()
        
        end_text = """✅ <b>AI suhbat tugatilik!</b>

🎉 <b>Rahmat suhbat uchun!</b>

📊 <b>Sizning natijangiz:</b>
• Premium AI suhbat tugallandi
• Har xabar uchun +1.5 reyting ball oldingiz
• Til bilimingiz oshdi!

💡 <b>Keyingi safar:</b>
Yana AI bilan suhbatlashish uchun "🤖 AI bilan suhbat" tugmasini bosing!"""

        from keyboards import get_main_menu
        from config import ADMIN_ID
        main_keyboard = get_main_menu(callback.from_user.id == ADMIN_ID)
        
        if callback.message:
            await callback.message.edit_text(
                end_text,
                reply_markup=main_keyboard,
                parse_mode="HTML"
            )
        await callback.answer("✅ Suhbat tugadi!")
        
    except Exception as e:
        print(f"End conversation error: {e}")
        await callback.answer("❌ Xatolik!")

@router.callback_query(F.data == "conversation_tips")
async def show_conversation_tips(callback: CallbackQuery):
    """AI suhbat haqida maslahatlar"""
    tips_text = """💡 <b>Premium AI bilan suhbat maslahatlar</b>

🎯 <b>Eng yaxshi tajriba uchun:</b>

🇰🇷 <b>Korean AI:</b>
• Hangul (한글) yoki lotin harflarida yozing
• Grammatik savollar bering: "Bu gap to'g'rimi?"
• Yangi so'zlarni so'rang: "Sevgi haqida so'zlar"
• Nutq amaliyoti: "Koreyscha salomlashish"

🇯🇵 <b>Japanese AI:</b>
• Hiragana, katakana yoki romaji ishlatish mumkin
• Keigo (hurmat shakli) haqida so'rang
• Kanji ma'nolarini so'rang
• Madaniy kontekst: "Yapon an'analari"

📈 <b>Reyting tizimi:</b>
• Har xabar = +1.5 ball
• Faol suhbat = yuqori reyting
• So'z boyligingiz o'sadi
• Daraja ko'tariladi

🎪 <b>Foydalanish maslahatlar:</b>
• Qisqa va aniq savollar bering
• AI dan tushuntirish so'rang
• Xatoliklar haqida so'rang
• Amaliy misol so'rang"""

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇰🇷 Korean AI", callback_data="korean_conversation"),
            InlineKeyboardButton(text="🇯🇵 Japanese AI", callback_data="japanese_conversation")
        ],
        [
            InlineKeyboardButton(text="🔙 Bosh menu", callback_data="main_menu")
        ]
    ])
    
    await callback.message.edit_text(tips_text, reply_markup=keyboard)
    await callback.answer()