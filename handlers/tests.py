from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from typing import cast
import aiosqlite

from config import ADMIN_ID
from database import DATABASE_PATH, get_user, create_quiz, add_question, get_quizzes, get_quiz_questions

router = Router()

class TestStates(StatesGroup):
    creating_quiz = State()
    quiz_title = State()
    quiz_description = State()
    adding_question = State()
    question_text = State()
    question_options = State()
    question_answer = State()
    question_explanation = State()

# =====================
# MAIN TESTS MENU - Entry point from main keyboard
# =====================

@router.callback_query(F.data == "tests")
async def main_tests_menu(callback: CallbackQuery):
    """Asosiy testlar menyusi - barcha foydalanuvchilar uchun"""
    try:
        if not callback.message or not callback.from_user:
            await callback.answer("❌ Xatolik!", show_alert=True)
            return
            
        user_id = callback.from_user.id
        is_admin = (user_id == ADMIN_ID)
        
        # Get user's quiz statistics
        async with aiosqlite.connect(DATABASE_PATH) as db:
            cursor = await db.execute("""
                SELECT COUNT(*) FROM quizzes WHERE created_by = ?
            """, (user_id,))
            my_quizzes = (await cursor.fetchone())[0]
            
            cursor = await db.execute("SELECT COUNT(*) FROM quizzes WHERE created_by IS NOT NULL")
            total_quizzes = (await cursor.fetchone())[0]
        
        quiz_text = f"🧠 <b>Testlar bo'limi</b>\n\n"
        quiz_text += f"📊 <b>Statistika:</b>\n"
        quiz_text += f"• Sizning testlaringiz: {my_quizzes}\n"
        quiz_text += f"• Jami testlar: {total_quizzes}\n\n"
        quiz_text += f"💡 Siz ham o'z testingizni yaratib, do'stlaringiz bilan baham ko'rishingiz mumkin!"
        
        keyboard = [
            [InlineKeyboardButton(text="🎯 Testlarni yechish", callback_data="take_quizzes")],
            [InlineKeyboardButton(text="➕ Yangi test yaratish", callback_data="user_create_quiz")],
            [InlineKeyboardButton(text="📋 Mening testlarim", callback_data="my_quizzes")],
            [InlineKeyboardButton(text="🏆 Top testlar", callback_data="popular_quizzes")]
        ]
        
        if is_admin:
            keyboard.append([InlineKeyboardButton(text="⚙️ Admin test panel", callback_data="admin_quiz")])
            
        keyboard.append([InlineKeyboardButton(text="🔙 Bosh menu", callback_data="main_menu")])
        
        message = cast(Message, callback.message)
        await message.edit_text(
            quiz_text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
            parse_mode="HTML"
        )
        await callback.answer()
        
    except Exception as e:
        print(f"Main tests menu error: {e}")
        try:
            await callback.answer("❌ Xatolik!", show_alert=True)
        except:
            pass

# =====================
# TESTLARNI YECHISH 
# =====================

@router.callback_query(F.data == "take_quizzes")
async def take_quizzes_menu(callback: CallbackQuery):
    """Testlarni yechish menyusi"""
    try:
        if not callback.message or not callback.from_user:
            await callback.answer("❌ Xatolik!", show_alert=True)
            return
        
        # Get all available quizzes with questions
        async with aiosqlite.connect(DATABASE_PATH) as db:
            cursor = await db.execute("""
                SELECT q.id, q.title, q.quiz_type, q.created_by, u.first_name, COUNT(qu.id) as question_count
                FROM quizzes q
                LEFT JOIN questions qu ON q.id = qu.quiz_id  
                LEFT JOIN users u ON q.created_by = u.user_id
                WHERE q.created_by IS NOT NULL
                GROUP BY q.id
                HAVING question_count > 0
                ORDER BY q.created_at DESC
                LIMIT 20
            """)
            quizzes = await cursor.fetchall()
        
        if not quizzes:
            message = cast(Message, callback.message)
            await message.edit_text(
                "📭 <b>Hozircha testlar mavjud emas</b>\n\n"
                "Test yaratuvchilar kutilmoqda...",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="➕ Birinchi testni yarating", callback_data="user_create_quiz")],
                    [InlineKeyboardButton(text="🔙 Testlar", callback_data="tests")]
                ]),
                parse_mode="HTML"
            )
            await callback.answer()
            return
        
        quiz_text = f"🎯 <b>Testlar ({len(quizzes)} ta)</b>\n\n"
        keyboard = []
        
        for quiz in quizzes:
            quiz_id, title, quiz_type, created_by, creator_name, question_count = quiz
            type_icons = {"korean": "🇰🇷", "japanese": "🇯🇵", "general": "📚", "topik": "📚", "jlpt": "🇯🇵"}
            icon = type_icons.get(quiz_type, "📝")
            
            quiz_text += f"{icon} <b>{title}</b>\n"
            quiz_text += f"   👤 {creator_name or 'Nomalum'} | 📊 {question_count} savol\n\n"
            
            keyboard.append([InlineKeyboardButton(
                text=f"{icon} {title} ({question_count} savol)", 
                callback_data=f"start_quiz_{quiz_id}"
            )])
        
        keyboard.append([InlineKeyboardButton(text="🔙 Testlar", callback_data="tests")])
        
        message = cast(Message, callback.message)
        await message.edit_text(
            quiz_text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
            parse_mode="HTML"
        )
        await callback.answer()
        
    except Exception as e:
        print(f"Take quizzes error: {e}")
        try:
            await callback.answer("❌ Xatolik!", show_alert=True)
        except:
            pass

# =====================
# YANGI TEST YARATISH
# =====================

@router.callback_query(F.data == "user_create_quiz")
async def user_create_quiz_menu(callback: CallbackQuery, state: FSMContext):
    """Foydalanuvchi test yaratish menyusi"""
    try:
        if not callback.message or not callback.from_user:
            await callback.answer("❌ Xatolik!", show_alert=True)
            return
        
        keyboard = [
            [InlineKeyboardButton(text="🇰🇷 Koreys tili testi", callback_data="user_quiz_korean")],
            [InlineKeyboardButton(text="🇯🇵 Yapon tili testi", callback_data="user_quiz_japanese")],
            [InlineKeyboardButton(text="📚 Umumiy bilim testi", callback_data="user_quiz_general")],
            [InlineKeyboardButton(text="🔙 Testlar", callback_data="tests")]
        ]
        
        message = cast(Message, callback.message)
        await message.edit_text(
            "✨ <b>Yangi test yaratish</b>\n\n"
            "📝 Qanday test yaratmoqchisiz?\n\n"
            "💡 <b>Maslahat:</b> Telegram quiz kabi ishlaydi!\n"
            "• Ko'p tanlovli savollar\n"
            "• To'g'ri javob bilan\n"
            "• Boshqalar bilan baham ko'ring",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
            parse_mode="HTML"
        )
        await callback.answer()
        
    except Exception as e:
        print(f"User create quiz menu error: {e}")
        try:
            await callback.answer("❌ Xatolik!", show_alert=True)
        except:
            pass

@router.callback_query(F.data.startswith("user_quiz_"))
async def user_quiz_type_selected(callback: CallbackQuery, state: FSMContext):
    """Foydalanuvchi test turi tanladi"""
    try:
        quiz_type_map = {
            "korean": "korean",
            "japanese": "japanese", 
            "general": "general"
        }
        
        selected_type = callback.data.split("_")[-1]
        quiz_type = quiz_type_map.get(selected_type, "general")
        
        await state.update_data(quiz_type=quiz_type, created_by=callback.from_user.id)
        await state.set_state(TestStates.quiz_title)
        
        type_names = {
            "korean": "🇰🇷 Koreys tili",
            "japanese": "🇯🇵 Yapon tili",
            "general": "📚 Umumiy bilim"
        }
        
        if not callback.message:
            await callback.answer("❌ Xatolik!", show_alert=True)
            return
            
        message = cast(Message, callback.message)
        await message.edit_text(
            f"{type_names.get(quiz_type, '📝')} <b>test yaratish</b>\n\n"
            "1️⃣ <b>Test nomini yozing:</b>\n\n"
            "💡 Misol: \"Koreys tilida salomlashish\"\n"
            "💡 /cancel - bekor qilish",
            reply_markup=None,
            parse_mode="HTML"
        )
        await callback.answer()
        
    except Exception as e:
        print(f"User quiz type error: {e}")
        try:
            await callback.answer("❌ Xatolik!", show_alert=True)
        except:
            pass

@router.message(TestStates.quiz_title)
async def user_quiz_title_received(message: Message, state: FSMContext):
    """Test nomi qabul qilish"""
    try:
        if not message or not message.text or not message.from_user:
            return
            
        if message.text == "/cancel":
            await state.clear()
            await message.answer("❌ Test yaratish bekor qilindi")
            return
        
        await state.update_data(title=message.text)
        await state.set_state(TestStates.quiz_description)
        
        await message.answer(
            f"✅ <b>Test nomi:</b> {message.text}\n\n"
            "2️⃣ <b>Test ta'rifini yozing:</b>\n\n"
            "💡 Misol: \"Bu test koreys tilida salomlashish so'zlari va iboralarini o'rganish uchun\"\n"
            "💡 /cancel - bekor qilish",
            parse_mode="HTML"
        )
        
    except Exception as e:
        print(f"Quiz title error: {e}")

@router.message(TestStates.quiz_description)
async def user_quiz_description_received(message: Message, state: FSMContext):
    """Test ta'rifi qabul qilish"""
    try:
        if not message or not message.text or not message.from_user:
            return
            
        if message.text == "/cancel":
            await state.clear()
            await message.answer("❌ Test yaratish bekor qilindi")
            return
        
        data = await state.get_data()
        title = data.get('title', '')
        quiz_type = data.get('quiz_type', 'general')
        created_by = data.get('created_by')
        
        # Testni saqlash
        quiz_id = await create_quiz(
            title=title,
            description=message.text,
            quiz_type=quiz_type,
            difficulty="beginner",
            created_by=created_by
        )
        
        await state.clear()
        
        if quiz_id:
            type_names = {
                "korean": "🇰🇷 Koreys tili",
                "japanese": "🇯🇵 Yapon tili", 
                "general": "📚 Umumiy bilim"
            }
            
            await message.answer(
                f"🎉 <b>{type_names.get(quiz_type, 'Test')} muvaffaqiyatli yaratildi!</b>\n\n"
                f"📝 <b>Nomi:</b> {title}\n"
                f"📄 <b>Ta'rifi:</b> {message.text}\n"
                f"🆔 <b>Test ID:</b> {quiz_id}\n\n"
                f"3️⃣ Endi savollar qo'shing:",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="➕ Birinchi savolni qo'shish", callback_data=f"add_question_{quiz_id}")],
                    [InlineKeyboardButton(text="📋 Mening testlarim", callback_data="my_quizzes")],
                    [InlineKeyboardButton(text="🧠 Testlar", callback_data="tests")]
                ]),
                parse_mode="HTML"
            )
        else:
            await message.answer("❌ Test yaratishda xatolik yuz berdi")
        
    except Exception as e:
        print(f"Quiz description error: {e}")

# =====================
# MENING TESTLARIM
# =====================

@router.callback_query(F.data == "my_quizzes")
async def my_quizzes_list(callback: CallbackQuery):
    """Foydalanuvchining testlari"""
    try:
        if not callback.message or not callback.from_user:
            await callback.answer("❌ Xatolik!", show_alert=True)
            return
            
        user_id = callback.from_user.id
        
        async with aiosqlite.connect(DATABASE_PATH) as db:
            cursor = await db.execute("""
                SELECT q.id, q.title, q.quiz_type, COUNT(qu.id) as question_count
                FROM quizzes q
                LEFT JOIN questions qu ON q.id = qu.quiz_id
                WHERE q.created_by = ?
                GROUP BY q.id
                ORDER BY q.created_at DESC
            """, (user_id,))
            my_quizzes = await cursor.fetchall()
        
        if not my_quizzes:
            message = cast(Message, callback.message)
            await message.edit_text(
                "📭 <b>Sizning testlaringiz yo'q</b>\n\n"
                "Yangi test yaratish uchun tugmani bosing:",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="➕ Yangi test yaratish", callback_data="user_create_quiz")],
                    [InlineKeyboardButton(text="🔙 Testlar", callback_data="tests")]
                ]),
                parse_mode="HTML"
            )
            await callback.answer()
            return
        
        quiz_text = f"📋 <b>Mening testlarim ({len(my_quizzes)} ta)</b>\n\n"
        keyboard = []
        
        for quiz in my_quizzes:
            quiz_id, title, quiz_type, question_count = quiz
            type_icons = {"korean": "🇰🇷", "japanese": "🇯🇵", "general": "📚", "topik": "📚", "jlpt": "🇯🇵"}
            icon = type_icons.get(quiz_type, "📝")
            
            quiz_text += f"{icon} <b>{title}</b>\n"
            quiz_text += f"   📊 {question_count} ta savol\n\n"
            
            keyboard.append([InlineKeyboardButton(
                text=f"{icon} {title} ({question_count} savol)", 
                callback_data=f"manage_quiz_{quiz_id}"
            )])
        
        keyboard.append([InlineKeyboardButton(text="➕ Yangi test", callback_data="user_create_quiz")])
        keyboard.append([InlineKeyboardButton(text="🔙 Testlar", callback_data="tests")])
        
        message = cast(Message, callback.message)
        await message.edit_text(
            quiz_text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
            parse_mode="HTML"
        )
        await callback.answer()
        
    except Exception as e:
        print(f"My quizzes error: {e}")
        try:
            await callback.answer("❌ Xatolik!", show_alert=True)
        except:
            pass

# =====================
# TOP TESTLAR
# =====================

@router.callback_query(F.data == "popular_quizzes")
async def popular_quizzes_menu(callback: CallbackQuery):
    """Top testlar menyusi"""
    try:
        if not callback.message or not callback.from_user:
            await callback.answer("❌ Xatolik!", show_alert=True)
            return
        
        # Get popular quizzes (most questions)
        async with aiosqlite.connect(DATABASE_PATH) as db:
            cursor = await db.execute("""
                SELECT q.id, q.title, q.quiz_type, q.created_by, u.first_name, COUNT(qu.id) as question_count
                FROM quizzes q
                LEFT JOIN questions qu ON q.id = qu.quiz_id  
                LEFT JOIN users u ON q.created_by = u.user_id
                WHERE q.created_by IS NOT NULL
                GROUP BY q.id
                HAVING question_count > 0
                ORDER BY question_count DESC, q.created_at DESC
                LIMIT 10
            """)
            popular_quizzes = await cursor.fetchall()
        
        if not popular_quizzes:
            message = cast(Message, callback.message)
            await message.edit_text(
                "📭 <b>Hozircha mashhur testlar yo'q</b>\n\n"
                "Birinchi testni yarating va mashhur bo'ling!",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="➕ Test yaratish", callback_data="user_create_quiz")],
                    [InlineKeyboardButton(text="🔙 Testlar", callback_data="tests")]
                ]),
                parse_mode="HTML"
            )
            await callback.answer()
            return
        
        quiz_text = f"🏆 <b>Top testlar</b>\n\n"
        keyboard = []
        
        for i, quiz in enumerate(popular_quizzes, 1):
            quiz_id, title, quiz_type, created_by, creator_name, question_count = quiz
            type_icons = {"korean": "🇰🇷", "japanese": "🇯🇵", "general": "📚", "topik": "📚", "jlpt": "🇯🇵"}
            icon = type_icons.get(quiz_type, "📝")
            
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            quiz_text += f"{medal} {icon} <b>{title}</b>\n"
            quiz_text += f"    👤 {creator_name or 'Nomalum'} | 📊 {question_count} savol\n\n"
            
            keyboard.append([InlineKeyboardButton(
                text=f"{medal} {title} ({question_count} savol)", 
                callback_data=f"start_quiz_{quiz_id}"
            )])
        
        keyboard.append([InlineKeyboardButton(text="🔙 Testlar", callback_data="tests")])
        
        message = cast(Message, callback.message)
        await message.edit_text(
            quiz_text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
            parse_mode="HTML"
        )
        await callback.answer()
        
    except Exception as e:
        print(f"Popular quizzes error: {e}")
        try:
            await callback.answer("❌ Xatolik!", show_alert=True)
        except:
            pass

# =====================
# ADMIN PANEL
# =====================

@router.callback_query(F.data == "admin_quiz")
async def admin_quiz_panel(callback: CallbackQuery):
    """Admin test paneli"""
    try:
        if not callback.from_user or callback.from_user.id != ADMIN_ID:
            await callback.answer("❌ Admin huquqi kerak!", show_alert=True)
            return
            
        if not callback.message:
            await callback.answer("❌ Xatolik!", show_alert=True)
            return
        
        message = cast(Message, callback.message)
        await message.edit_text(
            "⚙️ <b>Admin Test Panel</b>\n\n"
            "Bu bo'limda admin testlarni boshqaradi",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Testlar", callback_data="tests")]
            ]),
            parse_mode="HTML"
        )
        await callback.answer()
        
    except Exception as e:
        print(f"Admin quiz panel error: {e}")
        try:
            await callback.answer("❌ Xatolik!", show_alert=True)
        except:
            pass