import asyncio
import aiosqlite
from datetime import datetime
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from typing import cast
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter

from config import BOT_TOKEN, ADMIN_ID, DATABASE_PATH, PREMIUM_PRICE_UZS
from database import get_user, update_user_activity
from keyboards import get_admin_menu
from messages import ADMIN_WELCOME_MESSAGE

router = Router()

class AdminStates(StatesGroup):
    creating_section = State()
    creating_quiz = State()
    broadcast_text = State()

def admin_only(func):
    """Safe decorator for admin access"""
    async def wrapper(*args, **kwargs):
        try:
            # Get the first argument (update object)
            update = args[0] if args else None
            user_id = None
            
            if isinstance(update, Message) and update.from_user:
                user_id = update.from_user.id
            elif isinstance(update, CallbackQuery) and update.from_user:
                user_id = update.from_user.id
            
            if user_id != ADMIN_ID:
                if isinstance(update, Message):
                    await update.answer("❌ Sizda admin huquqlari yo'q!")
                elif isinstance(update, CallbackQuery):
                    try:
                        await update.answer("❌ Sizda admin huquqlari yo'q!", show_alert=True)
                    except:
                        pass
                return
            
            return await func(*args, **kwargs)
        except Exception as e:
            print(f"Admin decorator error: {e}")
            return
    return wrapper

@router.callback_query(F.data == "admin_panel")
async def admin_panel(callback: CallbackQuery):
    """Safe admin panel handler"""
    try:
        # Check admin access
        if not callback.from_user or callback.from_user.id != ADMIN_ID:
            await callback.answer("❌ Sizda admin huquqlari yo'q!", show_alert=True)
            return
            
        print(f"[ADMIN] Admin panel accessed by user {callback.from_user.id}")
        
        if not callback.message:
            print("[ADMIN] No callback.message found")
            await callback.answer("❌ Xatolik yuz berdi", show_alert=True)
            return
            
        message = cast(Message, callback.message)
        print(f"[ADMIN] Editing message with admin menu")
        
        await message.edit_text(
            ADMIN_WELCOME_MESSAGE,
            reply_markup=get_admin_menu(),
            parse_mode="HTML"
        )
        
        await callback.answer()
        print("[ADMIN] Admin panel displayed successfully")
        
    except Exception as e:
        print(f"[ADMIN] Admin panel error: {e}")
        import traceback
        print(f"[ADMIN] Traceback: {traceback.format_exc()}")
        try:
            await callback.answer("❌ Xatolik yuz berdi", show_alert=True)
        except:
            pass

@router.callback_query(F.data == "admin_stats") 
async def admin_stats(callback: CallbackQuery):
    """Safe admin stats handler"""
    try:
        # Check admin access
        if not callback.from_user or callback.from_user.id != ADMIN_ID:
            await callback.answer("❌ Sizda admin huquqlari yo'q!", show_alert=True)
            return
            
        if not callback.message:
            await callback.answer("❌ Xatolik yuz berdi", show_alert=True)
            return
            
        total_users = 0
        premium_users = 0
        active_today = 0
        total_sections = 0
        total_quizzes = 0
        
        try:
            async with aiosqlite.connect(DATABASE_PATH) as db:
                # Total users
                cursor = await db.execute("SELECT COUNT(*) FROM users")
                result = await cursor.fetchone()
                total_users = result[0] if result else 0
                
                # Premium users  
                cursor = await db.execute("SELECT COUNT(*) FROM users WHERE is_premium = 1")
                result = await cursor.fetchone()
                premium_users = result[0] if result else 0
                
                # Active today
                cursor = await db.execute("""
                    SELECT COUNT(*) FROM users 
                    WHERE last_activity > datetime('now', '-1 day')
                """)
                result = await cursor.fetchone()
                active_today = result[0] if result else 0
                
                # Total sections
                cursor = await db.execute("SELECT COUNT(*) FROM sections")
                result = await cursor.fetchone()
                total_sections = result[0] if result else 0
                
                # Total quizzes
                cursor = await db.execute("SELECT COUNT(*) FROM quizzes")
                result = await cursor.fetchone()
                total_quizzes = result[0] if result else 0
                
        except Exception as db_error:
            print(f"Database error: {db_error}")

        stats_text = f"""📊 <b>Bot Statistikasi</b>

👥 <b>Foydalanuvchilar:</b>
• Jami: {total_users}
• Premium: {premium_users}
• Bugun faol: {active_today}

📚 <b>Kontent:</b>
• Bo'limlar: {total_sections}
• Testlar: {total_quizzes}

💰 <b>Premium narxi:</b> {PREMIUM_PRICE_UZS:,} so'm"""

        message = cast(Message, callback.message)
        await message.edit_text(
            stats_text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Admin panel", callback_data="admin_panel")]
            ]),
            parse_mode="HTML"
        )
        
        await callback.answer()
        
    except Exception as e:
        print(f"Admin stats error: {e}")
        try:
            await callback.answer("❌ Xatolik yuz berdi", show_alert=True)
        except:
            pass

@router.callback_query(F.data == "admin_broadcast")
async def admin_broadcast_menu(callback: CallbackQuery):
    """Safe broadcast menu"""
    try:
        # Check admin access
        if not callback.from_user or callback.from_user.id != ADMIN_ID:
            await callback.answer("❌ Sizda admin huquqlari yo'q!", show_alert=True)
            return
            
        if not callback.message:
            await callback.answer("❌ Xatolik yuz berdi", show_alert=True)
            return
            
        message = cast(Message, callback.message)
        await message.edit_text(
            "📢 <b>Barchaga xabar yuborish</b>\n\n"
            "🎯 Barcha aktiv foydalanuvchilarga matn xabar yuborish\n\n"
            "⚠️ Xabar yuborishdan oldin tekshirish bo'ladi",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📝 Matn xabar yuborish", callback_data="broadcast_text")],
                [InlineKeyboardButton(text="🔙 Admin panel", callback_data="admin_panel")]
            ])
        )
        
        await callback.answer()
        
    except Exception as e:
        print(f"Broadcast menu error: {e}")
        try:
            await callback.answer("❌ Xatolik yuz berdi", show_alert=True)
        except:
            pass

@router.callback_query(F.data == "broadcast_text")
async def broadcast_text_start(callback: CallbackQuery, state: FSMContext):
    """Safe broadcast text start"""
    try:
        # Check admin access
        if not callback.from_user or callback.from_user.id != ADMIN_ID:
            await callback.answer("❌ Sizda admin huquqlari yo'q!", show_alert=True)
            return
            
        await state.set_state(AdminStates.broadcast_text)
        
        if not callback.message:
            await callback.answer("❌ Xatolik yuz berdi", show_alert=True)
            return
            
        message = cast(Message, callback.message)
        await message.edit_text(
            "📝 <b>Matn xabar yozish</b>\n\n"
            "Barcha foydalanuvchilarga yubormoqchi bo'lgan xabaringizni yozing:\n\n"
            "💡 /cancel - bekor qilish",
            reply_markup=None
        )
        
        await callback.answer()
        
    except Exception as e:
        print(f"Broadcast text start error: {e}")
        try:
            await callback.answer("❌ Xatolik yuz berdi", show_alert=True)
        except:
            pass

@router.message(AdminStates.broadcast_text)
async def broadcast_text_received(message: Message, state: FSMContext):
    """Safe broadcast text handler"""
    try:
        # Check admin access
        if not message.from_user or message.from_user.id != ADMIN_ID:
            await message.answer("❌ Sizda admin huquqlari yo'q!")
            return
            
        if not message or not message.text:
            return
            
        if message.text == "/cancel":
            await state.clear()
            await message.answer("❌ Bekor qilindi")
            return
        
        # Save message
        await state.update_data(message_text=message.text, message_type="text")
        
        # Show confirmation
        await message.answer(
            f"📋 <b>Tasdiqlash</b>\n\n"
            f"📝 <b>Xabar:</b>\n{message.text}\n\n"
            f"⚠️ Bu xabar barchaga yuboriladi!",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="✅ Yuborish", callback_data="confirm_broadcast"),
                    InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_broadcast")
                ]
            ])
        )
        
    except Exception as e:
        print(f"Broadcast text received error: {e}")

@router.callback_query(F.data == "confirm_broadcast")
async def confirm_broadcast(callback: CallbackQuery, state: FSMContext):
    """Safe broadcast confirmation"""
    try:
        # Check admin access
        if not callback.from_user or callback.from_user.id != ADMIN_ID:
            await callback.answer("❌ Sizda admin huquqlari yo'q!", show_alert=True)
            return
            
        data = await state.get_data()
        
        if not data or not callback.message:
            await callback.answer("❌ Xatolik!", show_alert=True)
            return
            
        message = cast(Message, callback.message)
        await message.edit_text("🚀 Yuborilmoqda...")
        
        # Send to all users - simplified for now
        sent_count = 0
        try:
            async with aiosqlite.connect(DATABASE_PATH) as db:
                cursor = await db.execute("SELECT user_id FROM users")
                users = await cursor.fetchall()
                
                for user_row in users:
                    try:
                        bot = Bot(token=BOT_TOKEN)
                        await bot.send_message(user_row[0], data.get('message_text', ''))
                        sent_count += 1
                    except Exception:
                        pass  # User might have blocked bot
        except Exception as e:
            print(f"Broadcast error: {e}")
        
        await state.clear()
        await message.edit_text(
            f"✅ <b>Xabar yuborildi!</b>\n\n"
            f"📊 {sent_count} ta foydalanuvchiga yuborildi",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Admin panel", callback_data="admin_panel")]
            ])
        )
        
        await callback.answer()
        
    except Exception as e:
        print(f"Confirm broadcast error: {e}")
        try:
            await callback.answer("❌ Xatolik yuz berdi", show_alert=True)
        except:
            pass

@router.callback_query(F.data == "cancel_broadcast")
async def cancel_broadcast(callback: CallbackQuery, state: FSMContext):
    """Cancel broadcast"""
    try:
        await state.clear()
        
        if not callback.message:
            await callback.answer("❌ Xatolik yuz berdi", show_alert=True)  
            return
            
        message = cast(Message, callback.message)
        await message.edit_text(
            "❌ <b>Xabar yuborish bekor qilindi</b>",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Admin panel", callback_data="admin_panel")]
            ]),
            parse_mode="HTML"
        )
        
        await callback.answer()
        
    except Exception as e:
        print(f"Cancel broadcast error: {e}")
        try:
            await callback.answer("❌ Xatolik yuz berdi", show_alert=True)
        except:
            pass

async def send_broadcast_message(data):
    """Safe broadcast sender"""
    bot = Bot(token=BOT_TOKEN)
    sent_count = 0
    
    try:
        # Get all users
        async with aiosqlite.connect(DATABASE_PATH) as db:
            cursor = await db.execute("SELECT user_id FROM users")
            users = await cursor.fetchall()
        
        message_text = data.get("message_text", "")
        
        if not message_text:
            return 0
            
        for (user_id,) in users:
            try:
                await bot.send_message(user_id, message_text)
                sent_count += 1
                await asyncio.sleep(0.05)  # Rate limiting
            except Exception:
                continue
        
        await bot.session.close()
        return sent_count
        
    except Exception as e:
        print(f"Broadcast error: {e}")
        try:
            await bot.session.close()
        except:
            pass
        return sent_count

# ================================
# OTHER ADMIN HANDLERS - SAFE STUBS
# ================================

@router.callback_query(F.data == "admin_sections")
async def admin_sections(callback: CallbackQuery):
    """Safe admin sections handler"""
    try:
        # Check admin access
        if not callback.from_user or callback.from_user.id != ADMIN_ID:
            await callback.answer("❌ Sizda admin huquqlari yo'q!", show_alert=True)
            return
            
        if not callback.message:
            await callback.answer("❌ Xatolik yuz berdi", show_alert=True)
            return
            
        message = cast(Message, callback.message)
        
        # Get sections from database
        from .sections import get_sections
        sections = await get_sections()
        sections_list = list(sections) if sections else []
        
        # Create sections management keyboard
        keyboard = []
        
        if sections_list:
            keyboard.append([InlineKeyboardButton(text="📋 Mavjud bo'limlarni ko'rish", callback_data="view_all_sections")])
            
        keyboard.extend([
            [InlineKeyboardButton(text="➕ Yangi bo'lim yaratish", callback_data="create_new_section")],
            [InlineKeyboardButton(text="🗑️ Bo'limni o'chirish", callback_data="delete_section_menu")],
            [InlineKeyboardButton(text="🔙 Admin panel", callback_data="admin_panel")]
        ])
        
        await message.edit_text(
            f"📚 <b>Bo'limlar boshqaruvi</b>\n\n"
            f"📊 Jami bo'limlar: {len(sections_list)}\n\n"
            f"Quyidagi amallarni tanlang:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
            parse_mode="HTML"
        )
        await callback.answer()
    except Exception as e:
        print(f"Admin sections error: {e}")
        try:
            await callback.answer("❌ Xatolik yuz berdi", show_alert=True)
        except:
            pass

@router.callback_query(F.data == "admin_content")
async def admin_content(callback: CallbackQuery):
    """Safe admin content handler"""
    try:
        # Check admin access
        if not callback.from_user or callback.from_user.id != ADMIN_ID:
            await callback.answer("❌ Sizda admin huquqlari yo'q!", show_alert=True)
            return
            
        if not callback.message:
            await callback.answer("❌ Xatolik yuz berdi", show_alert=True)
            return
            
        message = cast(Message, callback.message)
        
        # Get content statistics
        try:
            async with aiosqlite.connect(DATABASE_PATH) as db:
                cursor = await db.execute("SELECT COUNT(*) FROM content")
                content_count = await cursor.fetchone()
                content_total = content_count[0] if content_count else 0
                
                cursor = await db.execute("SELECT COUNT(*) FROM content WHERE is_premium = 1")
                premium_count = await cursor.fetchone()
                premium_total = premium_count[0] if premium_count else 0
        except Exception:
            content_total = 0
            premium_total = 0
        
        keyboard = [
            [InlineKeyboardButton(text="📋 Barcha kontentni ko'rish", callback_data="view_all_content")],
            [InlineKeyboardButton(text="➕ Yangi kontent qo'shish", callback_data="add_new_content")],
            [InlineKeyboardButton(text="🗑️ Kontentni o'chirish", callback_data="delete_content_menu")],
            [InlineKeyboardButton(text="💎 Premium kontentlar", callback_data="manage_premium_content")],
            [InlineKeyboardButton(text="🔙 Admin panel", callback_data="admin_panel")]
        ]
        
        await message.edit_text(
            f"📁 <b>Kontent boshqaruvi</b>\n\n"
            f"📊 Jami kontentlar: {content_total}\n"
            f"💎 Premium kontentlar: {premium_total}\n\n"
            f"Quyidagi amallarni tanlang:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
            parse_mode="HTML"
        )
        await callback.answer()
    except Exception as e:
        print(f"Admin content error: {e}")
        try:
            await callback.answer("❌ Xatolik yuz berdi", show_alert=True)
        except:
            pass

@router.callback_query(F.data == "admin_quiz")
async def admin_quiz(callback: CallbackQuery):
    """Safe admin quiz handler"""
    try:
        # Check admin access
        if not callback.from_user or callback.from_user.id != ADMIN_ID:
            await callback.answer("❌ Sizda admin huquqlari yo'q!", show_alert=True)
            return
            
        if not callback.message:
            await callback.answer("❌ Xatolik yuz berdi", show_alert=True)
            return
            
        message = cast(Message, callback.message)
        
        # Get quiz statistics
        try:
            async with aiosqlite.connect(DATABASE_PATH) as db:
                cursor = await db.execute("SELECT COUNT(*) FROM quizzes")
                quiz_count = await cursor.fetchone()
                quiz_total = quiz_count[0] if quiz_count else 0
                
                cursor = await db.execute("SELECT COUNT(*) FROM questions")
                question_count = await cursor.fetchone()
                question_total = question_count[0] if question_count else 0
        except Exception:
            quiz_total = 0
            question_total = 0
        
        keyboard = [
            [InlineKeyboardButton(text="📋 Barcha testlarni ko'rish", callback_data="view_all_quizzes")],
            [InlineKeyboardButton(text="➕ Yangi test yaratish", callback_data="create_new_quiz")],
            [InlineKeyboardButton(text="❓ Savol qo'shish", callback_data="add_quiz_question")],
            [InlineKeyboardButton(text="🗑️ Test o'chirish", callback_data="delete_quiz_menu")],
            [InlineKeyboardButton(text="🔙 Admin panel", callback_data="admin_panel")]
        ]
        
        await message.edit_text(
            f"🧠 <b>Testlar boshqaruvi</b>\n\n"
            f"📊 Jami testlar: {quiz_total}\n"
            f"❓ Jami savollar: {question_total}\n\n"
            f"Quyidagi amallarni tanlang:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
            parse_mode="HTML"
        )
        await callback.answer()
    except Exception as e:
        print(f"Admin quiz error: {e}")
        try:
            await callback.answer("❌ Xatolik yuz berdi", show_alert=True)
        except:
            pass

# MISSING ADMIN HANDLERS
@router.callback_query(F.data == "admin_premium")
async def admin_premium(callback: CallbackQuery):
    """Admin premium management"""
    try:
        # Check admin access
        if not callback.from_user or callback.from_user.id != ADMIN_ID:
            await callback.answer("❌ Sizda admin huquqlari yo'q!", show_alert=True)
            return
            
        if not callback.message:
            await callback.answer("❌ Xatolik yuz berdi", show_alert=True)
            return
            
        message = cast(Message, callback.message)
        
        # Get premium user statistics
        try:
            async with aiosqlite.connect(DATABASE_PATH) as db:
                cursor = await db.execute("SELECT COUNT(*) FROM users WHERE is_premium = 1")
                premium_count = await cursor.fetchone()
                premium_users = premium_count[0] if premium_count else 0
                
                cursor = await db.execute("SELECT COUNT(*) FROM users")
                total_count = await cursor.fetchone()
                total_users = total_count[0] if total_count else 0
        except Exception:
            premium_users = 0
            total_users = 0
        
        keyboard = [
            [InlineKeyboardButton(text="👥 Premium foydalanuvchilar", callback_data="view_premium_users")],
            [InlineKeyboardButton(text="➕ Premium berish", callback_data="grant_premium")],
            [InlineKeyboardButton(text="➖ Premium olib tashlash", callback_data="revoke_premium")],
            [InlineKeyboardButton(text="📊 Premium statistika", callback_data="premium_stats")],
            [InlineKeyboardButton(text="🔙 Admin panel", callback_data="admin_panel")]
        ]
        
        await message.edit_text(
            f"💎 <b>Premium boshqaruv</b>\n\n"
            f"👥 Premium foydalanuvchilar: {premium_users}\n"
            f"📊 Jami foydalanuvchilar: {total_users}\n"
            f"📈 Premium foiz: {(premium_users/total_users*100):.1f}%" if total_users > 0 else "📈 Premium foiz: 0%",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
            parse_mode="HTML"
        )
        await callback.answer()
    except Exception as e:
        print(f"Admin premium error: {e}")
        try:
            await callback.answer("❌ Xatolik yuz berdi", show_alert=True)
        except:
            pass

@router.callback_query(F.data == "admin_payments")
async def admin_payments(callback: CallbackQuery):
    """Admin payments management"""  
    try:
        # Check admin access
        if not callback.from_user or callback.from_user.id != ADMIN_ID:
            await callback.answer("❌ Sizda admin huquqlari yo'q!", show_alert=True)
            return
            
        if not callback.message:
            await callback.answer("❌ Xatolik yuz berdi", show_alert=True)
            return
            
        message = cast(Message, callback.message)
        
        # Get pending payment requests (if any)
        try:
            async with aiosqlite.connect(DATABASE_PATH) as db:
                cursor = await db.execute("SELECT COUNT(*) FROM users WHERE payment_pending = 1")
                pending_count = await cursor.fetchone()
                pending_payments = pending_count[0] if pending_count else 0
        except Exception:
            pending_payments = 0
        
        keyboard = [
            [InlineKeyboardButton(text="📋 Kutilayotgan to'lovlar", callback_data="view_pending_payments")],
            [InlineKeyboardButton(text="✅ To'lovni tasdiqlash", callback_data="confirm_payment")],
            [InlineKeyboardButton(text="❌ To'lovni rad etish", callback_data="reject_payment")],
            [InlineKeyboardButton(text="📊 To'lov tarixi", callback_data="payment_history")],
            [InlineKeyboardButton(text="🔙 Admin panel", callback_data="admin_panel")]
        ]
        
        await message.edit_text(
            f"💳 <b>To'lov tasdiqlash</b>\n\n"
            f"⏳ Kutilayotgan to'lovlar: {pending_payments}\n\n"
            f"To'lov tasdiqlash va boshqaruv:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
            parse_mode="HTML"
        )
        await callback.answer()
    except Exception as e:
        print(f"Admin payments error: {e}")
        try:
            await callback.answer("❌ Xatolik yuz berdi", show_alert=True)
        except:
            pass

@router.callback_query(F.data == "content_delete_menu")
async def content_delete_menu(callback: CallbackQuery):
    """Content delete menu"""
    try:
        # Check admin access
        if not callback.from_user or callback.from_user.id != ADMIN_ID:
            await callback.answer("❌ Sizda admin huquqlari yo'q!", show_alert=True)
            return
            
        if not callback.message:
            await callback.answer("❌ Xatolik yuz berdi", show_alert=True)
            return
            
        message = cast(Message, callback.message)
        await message.edit_text(
            "🗑️ <b>Content o'chirish</b>\n\n"
            "Bu funksiya hozircha ishlab chiqilmoqda...",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Admin panel", callback_data="admin_panel")]
            ])
        )
        await callback.answer()
    except Exception as e:
        print(f"Content delete error: {e}")
        try:
            await callback.answer("❌ Xatolik yuz berdi", show_alert=True)
        except:
            pass

@router.callback_query(F.data == "admin_test_messages")
async def admin_test_messages(callback: CallbackQuery):
    """Admin test messages"""
    try:
        # Check admin access
        if not callback.from_user or callback.from_user.id != ADMIN_ID:
            await callback.answer("❌ Sizda admin huquqlari yo'q!", show_alert=True)
            return
            
        if not callback.message:
            await callback.answer("❌ Xatolik yuz berdi", show_alert=True)
            return
            
        message = cast(Message, callback.message)
        await message.edit_text(
            "📨 <b>Test xabarlar</b>\n\n"
            "Bu funksiya hozircha ishlab chiqilmoqda...",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Admin panel", callback_data="admin_panel")]
            ])
        )
        await callback.answer()
    except Exception as e:
        print(f"Test messages error: {e}")
        try:
            await callback.answer("❌ Xatolik yuz berdi", show_alert=True)
        except:
            pass

@router.callback_query(F.data == "delete_section_menu")
async def delete_section_menu(callback: CallbackQuery):
    """Show sections for deletion"""
    try:
        if not callback.from_user or callback.from_user.id != ADMIN_ID:
            await callback.answer("❌ Sizda admin huquqlari yo'q!", show_alert=True)
            return
            
        from .sections import get_sections
        sections = await get_sections()
        sections_list = list(sections) if sections else []
        
        if not sections_list:
            await callback.answer("📝 Hech qanday bo'lim topilmadi", show_alert=True)
            return
            
        if not callback.message:
            await callback.answer("❌ Xatolik yuz berdi", show_alert=True)
            return
            
        text = "🗑 <b>Bo'limni o'chirish</b>\n\n"
        text += "⚠️ <b>Ogohlantirish:</b> Bo'limni o'chirganda uning barcha kontenti ham o'chadi!\n\n"
        text += "Qaysi bo'limni o'chirmoqchisiz?\n\n"
        
        keyboard = []
        
        for i, section in enumerate(sections_list[:8], 1):  # Limit to 8 sections
            section_id, name, description, language, is_premium = section
            premium_text = " (Premium)" if is_premium else ""
            text += f"{i}. <b>{name}</b>{premium_text} ({language})\n"
            
            keyboard.append([InlineKeyboardButton(
                text=f"🗑 {name[:20]}...", 
                callback_data=f"confirm_delete_section_{section_id}"
            )])
        
        keyboard.append([InlineKeyboardButton(text="🔙 Bo'limlar boshqaruvi", callback_data="admin_sections")])
        
        message = cast(Message, callback.message)
        await message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
            parse_mode="HTML"
        )
        await callback.answer()
        
    except Exception as e:
        print(f"Delete section menu error: {e}")
        await callback.answer("❌ Xatolik yuz berdi", show_alert=True)

@router.callback_query(F.data.startswith("confirm_delete_section_"))
async def confirm_delete_section(callback: CallbackQuery):
    """Confirm section deletion"""
    try:
        if not callback.from_user or callback.from_user.id != ADMIN_ID:
            await callback.answer("❌ Sizda admin huquqlari yo'q!", show_alert=True)
            return
            
        section_id = int(callback.data.split("_")[-1])
        
        # Get section details for confirmation
        async with aiosqlite.connect(DATABASE_PATH) as db:
            cursor = await db.execute("SELECT name, description FROM sections WHERE id = ?", (section_id,))
            section = await cursor.fetchone()
            
            if not section:
                await callback.answer("❌ Bo'lim topilmadi", show_alert=True)
                return
                
            name, description = section
            
            # Count content and subsections
            cursor = await db.execute("SELECT COUNT(*) FROM content WHERE section_id = ?", (section_id,))
            content_count = (await cursor.fetchone())[0]
            
            cursor = await db.execute("SELECT COUNT(*) FROM subsections WHERE section_id = ?", (section_id,))
            subsection_count = (await cursor.fetchone())[0]
        
        if not callback.message:
            await callback.answer("❌ Xatolik yuz berdi", show_alert=True)
            return
            
        text = f"⚠️ <b>Bo'limni o'chirishni tasdiqlang</b>\n\n"
        text += f"📝 <b>Bo'lim:</b> {name}\n"
        text += f"📖 <b>Tavsif:</b> {description[:50]}...\n\n"
        text += f"📊 <b>O'chiriladigan ma'lumotlar:</b>\n"
        text += f"• {subsection_count} ta bo'lim kichik qismi\n"
        text += f"• {content_count} ta kontent\n\n"
        text += f"❌ <b>Bu amalni bekor qilib bo'lmaydi!</b>"
        
        keyboard = [
            [
                InlineKeyboardButton(text="✅ Ha, o'chirish", callback_data=f"execute_delete_section_{section_id}"),
                InlineKeyboardButton(text="❌ Bekor qilish", callback_data="delete_section_menu")
            ],
            [InlineKeyboardButton(text="🔙 Bo'limlar boshqaruvi", callback_data="admin_sections")]
        ]
        
        message = cast(Message, callback.message)
        await message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
            parse_mode="HTML"
        )
        await callback.answer()
        
    except Exception as e:
        print(f"Confirm delete section error: {e}")
        await callback.answer("❌ Xatolik yuz berdi", show_alert=True)

@router.callback_query(F.data.startswith("execute_delete_section_"))
async def execute_delete_section(callback: CallbackQuery):
    """Execute section deletion"""
    try:
        if not callback.from_user or callback.from_user.id != ADMIN_ID:
            await callback.answer("❌ Sizda admin huquqlari yo'q!", show_alert=True)
            return
            
        section_id = int(callback.data.split("_")[-1])
        
        # Delete section and all related data
        async with aiosqlite.connect(DATABASE_PATH) as db:
            # Get section name for confirmation message
            cursor = await db.execute("SELECT name FROM sections WHERE id = ?", (section_id,))
            section = await cursor.fetchone()
            
            if not section:
                await callback.answer("❌ Bo'lim topilmadi", show_alert=True)
                return
                
            section_name = section[0]
            
            # Delete all related content first
            await db.execute("DELETE FROM content WHERE section_id = ?", (section_id,))
            
            # Delete all subsections
            await db.execute("DELETE FROM subsections WHERE section_id = ?", (section_id,))
            
            # Finally delete the section
            await db.execute("DELETE FROM sections WHERE id = ?", (section_id,))
            
            await db.commit()
        
        if not callback.message:
            await callback.answer("❌ Xatolik yuz berdi", show_alert=True)
            return
            
        keyboard = [
            [InlineKeyboardButton(text="📚 Bo'limlar boshqaruvi", callback_data="admin_sections")],
            [InlineKeyboardButton(text="🔙 Admin panel", callback_data="admin_panel")]
        ]
        
        message = cast(Message, callback.message)
        await message.edit_text(
            f"✅ <b>Bo'lim muvaffaqiyatli o'chirildi!</b>\n\n"
            f"📝 <b>O'chirilgan bo'lim:</b> {section_name}\n\n"
            f"Barcha bog'liq kontent va bo'lim kichik qismlari ham o'chirildi.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
            parse_mode="HTML"
        )
        await callback.answer("✅ Bo'lim o'chirildi!")
        
    except Exception as e:
        print(f"Execute delete section error: {e}")
        await callback.answer("❌ Xatolik yuz berdi", show_alert=True)

# =======================================================
# NEW ADMIN HANDLER IMPLEMENTATIONS - SECTIONS MANAGEMENT
# =======================================================

@router.callback_query(F.data == "view_all_sections")
async def view_all_sections(callback: CallbackQuery):
    """View all sections"""
    try:
        if not callback.from_user or callback.from_user.id != ADMIN_ID:
            await callback.answer("❌ Sizda admin huquqlari yo'q!", show_alert=True)
            return
            
        from .sections import get_sections
        sections = await get_sections()
        sections_list = list(sections) if sections else []
        
        if not sections_list:
            await callback.answer("📝 Hech qanday bo'lim topilmadi", show_alert=True)
            return
            
        if not callback.message:
            await callback.answer("❌ Xatolik yuz berdi", show_alert=True)
            return
            
        text = "📚 <b>Barcha bo'limlar:</b>\n\n"
        keyboard = []
        
        for i, section in enumerate(sections_list[:10], 1):  # Limit to 10 sections
            section_id, name, description, language, is_premium = section
            premium_text = "💎 Premium" if is_premium else "🆓 Tekin"
            text += f"{i}. <b>{name}</b> ({premium_text})\n"
            text += f"   📖 {description}\n"
            text += f"   🌐 {language.title()}\n\n"
            
            keyboard.append([InlineKeyboardButton(
                text=f"📝 {name[:25]}...", 
                callback_data=f"edit_section_{section_id}"
            )])
        
        keyboard.append([InlineKeyboardButton(text="🔙 Bo'limlar boshqaruvi", callback_data="admin_sections")])
        
        message = cast(Message, callback.message)
        await message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
            parse_mode="HTML"
        )
        await callback.answer()
        
    except Exception as e:
        print(f"View sections error: {e}")
        await callback.answer("❌ Xatolik yuz berdi", show_alert=True)

@router.callback_query(F.data == "create_new_section")
async def create_new_section(callback: CallbackQuery, state: FSMContext):
    """Start section creation"""
    try:
        if not callback.from_user or callback.from_user.id != ADMIN_ID:
            await callback.answer("❌ Sizda admin huquqlari yo'q!", show_alert=True)
            return
            
        await state.set_state("creating_section_name")
        
        if not callback.message:
            await callback.answer("❌ Xatolik yuz berdi", show_alert=True)
            return
            
        message = cast(Message, callback.message)
        await message.edit_text(
            "📝 <b>Yangi bo'lim yaratish</b>\n\n"
            "Bo'lim nomini kiriting:\n\n"
            "💡 /cancel - bekor qilish",
            reply_markup=None,
            parse_mode="HTML"
        )
        await callback.answer()
        
    except Exception as e:
        print(f"Create section error: {e}")
        await callback.answer("❌ Xatolik yuz berdi", show_alert=True)

# =======================================================
# CONTENT MANAGEMENT HANDLERS
# =======================================================

@router.callback_query(F.data == "view_all_content")
async def view_all_content(callback: CallbackQuery):
    """View all content"""
    try:
        if not callback.from_user or callback.from_user.id != ADMIN_ID:
            await callback.answer("❌ Sizda admin huquqlari yo'q!", show_alert=True)
            return
            
        async with aiosqlite.connect(DATABASE_PATH) as db:
            cursor = await db.execute("""
                SELECT c.id, c.title, c.content_type, c.is_premium, s.name as section_name
                FROM content c
                LEFT JOIN sections s ON c.section_id = s.id
                ORDER BY c.created_at DESC
                LIMIT 15
            """)
            content_list = await cursor.fetchall()
        
        if not content_list:
            await callback.answer("📝 Hech qanday kontent topilmadi", show_alert=True)
            return
            
        text = "📁 <b>Barcha kontentlar:</b>\n\n"
        keyboard = []
        
        for i, content in enumerate(content_list, 1):
            content_id, title, content_type, is_premium, section_name = content
            premium_icon = "💎" if is_premium else "📄"
            text += f"{i}. {premium_icon} <b>{title[:30]}...</b>\n"
            text += f"   📂 {section_name or 'Umum'}\n"
            text += f"   🎯 {content_type.title()}\n\n"
            
            keyboard.append([InlineKeyboardButton(
                text=f"{premium_icon} {title[:25]}...", 
                callback_data=f"edit_content_{content_id}"
            )])
        
        keyboard.append([InlineKeyboardButton(text="🔙 Kontent boshqaruvi", callback_data="admin_content")])
        
        if not callback.message:
            await callback.answer("❌ Xatolik yuz berdi", show_alert=True)
            return
            
        message = cast(Message, callback.message)
        await message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
            parse_mode="HTML"
        )
        await callback.answer()
        
    except Exception as e:
        print(f"View content error: {e}")
        await callback.answer("❌ Xatolik yuz berdi", show_alert=True)

@router.callback_query(F.data == "add_new_content")
async def add_new_content(callback: CallbackQuery):
    """Add new content - redirect to sections first"""
    try:
        if not callback.from_user or callback.from_user.id != ADMIN_ID:
            await callback.answer("❌ Sizda admin huquqlari yo'q!", show_alert=True)
            return
            
        from .sections import get_sections
        sections = await get_sections()
        sections_list = list(sections) if sections else []
        
        if not sections_list:
            await callback.answer("⚠️ Avval bo'lim yarating!", show_alert=True)
            return
            
        if not callback.message:
            await callback.answer("❌ Xatolik yuz berdi", show_alert=True)
            return
            
        keyboard = []
        for section in sections_list[:8]:  # Limit display
            section_id, name, _, _, is_premium = section
            premium_icon = "💎" if is_premium else "📂"
            keyboard.append([InlineKeyboardButton(
                text=f"{premium_icon} {name}", 
                callback_data=f"add_content_to_{section_id}"
            )])
        
        keyboard.append([InlineKeyboardButton(text="🔙 Kontent boshqaruvi", callback_data="admin_content")])
        
        message = cast(Message, callback.message)
        await message.edit_text(
            "📁 <b>Kontent qo'shish</b>\n\n"
            "Qaysi bo'limga kontent qo'shmoqchisiz?",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
            parse_mode="HTML"
        )
        await callback.answer()
        
    except Exception as e:
        print(f"Add content error: {e}")
        await callback.answer("❌ Xatolik yuz berdi", show_alert=True)

# =======================================================
# QUIZ MANAGEMENT HANDLERS  
# =======================================================

@router.callback_query(F.data == "view_all_quizzes")
async def view_all_quizzes(callback: CallbackQuery):
    """View all quizzes"""
    try:
        if not callback.from_user or callback.from_user.id != ADMIN_ID:
            await callback.answer("❌ Sizda admin huquqlari yo'q!", show_alert=True)
            return
            
        async with aiosqlite.connect(DATABASE_PATH) as db:
            cursor = await db.execute("""
                SELECT q.id, q.title, q.quiz_type, q.difficulty, 
                       COUNT(qu.id) as question_count
                FROM quizzes q
                LEFT JOIN questions qu ON q.id = qu.quiz_id
                GROUP BY q.id
                ORDER BY q.created_at DESC
                LIMIT 10
            """)
            quizzes = await cursor.fetchall()
        
        if not quizzes:
            await callback.answer("📝 Hech qanday test topilmadi", show_alert=True)
            return
            
        text = "🧠 <b>Barcha testlar:</b>\n\n"
        keyboard = []
        
        for i, quiz in enumerate(quizzes, 1):
            quiz_id, title, quiz_type, difficulty, question_count = quiz
            text += f"{i}. <b>{title}</b>\n"
            text += f"   🎯 {quiz_type.title()} - {difficulty}\n"
            text += f"   ❓ {question_count} ta savol\n\n"
            
            keyboard.append([InlineKeyboardButton(
                text=f"📝 {title[:25]}...", 
                callback_data=f"edit_quiz_{quiz_id}"
            )])
        
        keyboard.append([InlineKeyboardButton(text="🔙 Testlar boshqaruvi", callback_data="admin_quiz")])
        
        if not callback.message:
            await callback.answer("❌ Xatolik yuz berdi", show_alert=True)
            return
            
        message = cast(Message, callback.message)
        await message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
            parse_mode="HTML"
        )
        await callback.answer()
        
    except Exception as e:
        print(f"View quizzes error: {e}")
        await callback.answer("❌ Xatolik yuz berdi", show_alert=True)

@router.callback_query(F.data == "create_new_quiz")
async def create_new_quiz(callback: CallbackQuery, state: FSMContext):
    """Start quiz creation"""
    try:
        if not callback.from_user or callback.from_user.id != ADMIN_ID:
            await callback.answer("❌ Sizda admin huquqlari yo'q!", show_alert=True)
            return
            
        await state.set_state("creating_quiz_title")
        
        if not callback.message:
            await callback.answer("❌ Xatolik yuz berdi", show_alert=True)
            return
            
        message = cast(Message, callback.message)
        await message.edit_text(
            "🧠 <b>Yangi test yaratish</b>\n\n"
            "Test nomini kiriting:\n\n"
            "💡 /cancel - bekor qilish",
            reply_markup=None,
            parse_mode="HTML"
        )
        await callback.answer()
        
    except Exception as e:
        print(f"Create quiz error: {e}")
        await callback.answer("❌ Xatolik yuz berdi", show_alert=True)

# =======================================================
# PREMIUM MANAGEMENT HANDLERS
# =======================================================

@router.callback_query(F.data == "view_premium_users")
async def view_premium_users(callback: CallbackQuery):
    """View premium users"""
    try:
        if not callback.from_user or callback.from_user.id != ADMIN_ID:
            await callback.answer("❌ Sizda admin huquqlari yo'q!", show_alert=True)
            return
            
        async with aiosqlite.connect(DATABASE_PATH) as db:
            cursor = await db.execute("""
                SELECT user_id, first_name, last_name, username, premium_expires_at, rating_score
                FROM users 
                WHERE is_premium = 1
                ORDER BY premium_expires_at DESC
                LIMIT 15
            """)
            premium_users = await cursor.fetchall()
        
        if not premium_users:
            await callback.answer("👥 Premium foydalanuvchilar topilmadi", show_alert=True)
            return
            
        text = "💎 <b>Premium foydalanuvchilar:</b>\n\n"
        
        for i, user in enumerate(premium_users, 1):
            user_id, first_name, last_name, username, premium_expires_at, rating = user
            name = f"{first_name or ''} {last_name or ''}".strip() or "Noma'lum"
            username_text = f"@{username}" if username else ""
            
            text += f"{i}. <b>{name}</b> {username_text}\n"
            text += f"   🆔 {user_id}\n"
            text += f"   ⭐ {rating or 0} reyting\n"
            text += f"   📅 {premium_expires_at or 'Cheksiz'}\n\n"
        
        keyboard = [
            [InlineKeyboardButton(text="🔙 Premium boshqaruv", callback_data="admin_premium")]
        ]
        
        if not callback.message:
            await callback.answer("❌ Xatolik yuz berdi", show_alert=True)
            return
            
        message = cast(Message, callback.message)
        await message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
            parse_mode="HTML"
        )
        await callback.answer()
        
    except Exception as e:
        print(f"View premium users error: {e}")
        await callback.answer("❌ Xatolik yuz berdi", show_alert=True)

@router.callback_query(F.data == "grant_premium")
async def grant_premium(callback: CallbackQuery, state: FSMContext):
    """Grant premium to user"""
    try:
        if not callback.from_user or callback.from_user.id != ADMIN_ID:
            await callback.answer("❌ Sizda admin huquqlari yo'q!", show_alert=True)
            return
            
        await state.set_state("granting_premium")
        
        if not callback.message:
            await callback.answer("❌ Xatolik yuz berdi", show_alert=True)
            return
            
        message = cast(Message, callback.message)
        await message.edit_text(
            "💎 <b>Premium berish</b>\n\n"
            "Foydalanuvchi ID raqamini kiriting:\n\n"
            "💡 /cancel - bekor qilish",
            reply_markup=None,
            parse_mode="HTML"
        )
        await callback.answer()
        
    except Exception as e:
        print(f"Grant premium error: {e}")
        await callback.answer("❌ Xatolik yuz berdi", show_alert=True)

# =======================================================
# MESSAGE HANDLERS FOR CREATING SECTIONS/CONTENT/QUIZZES
# =======================================================

@router.message(F.text, StateFilter("creating_section_name"))
async def receive_section_name(message: Message, state: FSMContext):
    """Receive section name and ask for description"""
    try:
        if not message.from_user or message.from_user.id != ADMIN_ID:
            await message.answer("❌ Sizda admin huquqlari yo'q!")
            return
            
        if not message.text:
            return
            
        if message.text == "/cancel":
            await state.clear()
            await message.answer("❌ Bo'lim yaratish bekor qilindi")
            return
            
        section_name = message.text.strip()
        if len(section_name) < 2:
            await message.answer("⚠️ Bo'lim nomi kamida 2 ta belgidan iborat bo'lishi kerak")
            return
            
        await state.update_data(section_name=section_name)
        await state.set_state("creating_section_description")
        
        await message.answer(
            f"📝 <b>Bo'lim nomi:</b> {section_name}\n\n"
            f"Endi bo'lim tavsifini kiriting:\n\n"
            f"💡 /cancel - bekor qilish",
            parse_mode="HTML"
        )
        
    except Exception as e:
        print(f"Section name error: {e}")
        await message.answer("❌ Xatolik yuz berdi")

@router.message(F.text, StateFilter("creating_section_description"))
async def receive_section_description(message: Message, state: FSMContext):
    """Receive section description and ask premium status"""
    try:
        if not message.from_user or message.from_user.id != ADMIN_ID:
            await message.answer("❌ Sizda admin huquqlari yo'q!")
            return
            
        if not message.text:
            return
            
        if message.text == "/cancel":
            await state.clear()
            await message.answer("❌ Bo'lim yaratish bekor qilindi")
            return
            
        data = await state.get_data()
        section_name = data.get("section_name", "")
        section_description = message.text.strip()
        
        if len(section_description) < 5:
            await message.answer("⚠️ Bo'lim tavsifi kamida 5 ta belgidan iborat bo'lishi kerak")
            return
            
        await state.update_data(section_description=section_description)
        await state.set_state("creating_section_premium")
        
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🆓 Tekin", callback_data="section_premium_free")],
            [InlineKeyboardButton(text="💎 Premium", callback_data="section_premium_paid")],
            [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="admin_sections")]
        ])
        
        await message.answer(
            f"📝 <b>Bo'lim nomi:</b> {section_name}\n"
            f"📖 <b>Tavsif:</b> {section_description}\n\n"
            f"🔒 <b>Bo'lim turini tanlang:</b>\n\n"
            f"🆓 <b>Tekin</b> - barcha foydalanuvchilar ko'ra oladi\n"
            f"💎 <b>Premium</b> - faqat premium foydalanuvchilar ko'ra oladi\n\n"
            f"Qaysi turni tanlaysiz?",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
            
    except Exception as e:
        print(f"Section description error: {e}")
        await message.answer("❌ Xatolik yuz berdi")

@router.callback_query(F.data.startswith("section_premium_"))
async def receive_section_premium_status(callback: CallbackQuery, state: FSMContext):
    """Receive premium status and create section"""
    try:
        if not callback.from_user or callback.from_user.id != ADMIN_ID:
            await callback.answer("❌ Sizda admin huquqlari yo'q!", show_alert=True)
            return
            
        is_premium = callback.data == "section_premium_paid"
        premium_text = "💎 Premium" if is_premium else "🆓 Tekin"
        
        data = await state.get_data()
        section_name = data.get("section_name", "")
        section_description = data.get("section_description", "")
        
        # Create the section in database
        from .sections import create_section
        section_id = await create_section(
            name=section_name,
            description=section_description,
            language="korean",
            is_premium=is_premium
        )
        
        await state.clear()
        
        if not callback.message:
            await callback.answer("❌ Xatolik yuz berdi", show_alert=True)
            return
            
        if section_id:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📁 Kontent qo'shish", callback_data=f"add_content_{section_id}")],
                [InlineKeyboardButton(text="📚 Bo'limlar boshqaruvi", callback_data="admin_sections")],
                [InlineKeyboardButton(text="🔙 Admin panel", callback_data="admin_panel")]
            ])
            
            message = cast(Message, callback.message)
            await message.edit_text(
                f"✅ <b>Bo'lim muvaffaqiyatli yaratildi!</b>\n\n"
                f"📝 <b>Nomi:</b> {section_name}\n"
                f"📖 <b>Tavsif:</b> {section_description}\n"
                f"🔒 <b>Turi:</b> {premium_text}\n"
                f"🆔 <b>ID:</b> {section_id}\n\n"
                f"Endi bo'limga kontent qo'shishingiz mumkin!",
                reply_markup=keyboard,
                parse_mode="HTML"
            )
        else:
            await callback.message.edit_text("❌ Bo'lim yaratishda xatolik yuz berdi")
            
        await callback.answer(f"✅ {premium_text} bo'lim yaratildi!")
            
    except Exception as e:
        print(f"Section premium status error: {e}")
        await callback.answer("❌ Xatolik yuz berdi", show_alert=True)

@router.message(F.text, StateFilter("creating_quiz_title"))
async def receive_quiz_title(message: Message, state: FSMContext):
    """Receive quiz title and ask for description"""
    try:
        if not message.from_user or message.from_user.id != ADMIN_ID:
            await message.answer("❌ Sizda admin huquqlari yo'q!")
            return
            
        if not message.text:
            return
            
        if message.text == "/cancel":
            await state.clear()
            await message.answer("❌ Test yaratish bekor qilindi")
            return
            
        quiz_title = message.text.strip()
        if len(quiz_title) < 3:
            await message.answer("⚠️ Test nomi kamida 3 ta belgidan iborat bo'lishi kerak")
            return
            
        await state.update_data(quiz_title=quiz_title)
        await state.set_state("creating_quiz_description")
        
        await message.answer(
            f"🧠 <b>Test nomi:</b> {quiz_title}\n\n"
            f"Endi test tavsifini kiriting:\n\n"
            f"💡 /cancel - bekor qilish",
            parse_mode="HTML"
        )
        
    except Exception as e:
        print(f"Quiz title error: {e}")
        await message.answer("❌ Xatolik yuz berdi")

@router.message(F.text, StateFilter("creating_quiz_description"))
async def receive_quiz_description(message: Message, state: FSMContext):
    """Receive quiz description and create quiz"""
    try:
        if not message.from_user or message.from_user.id != ADMIN_ID:
            await message.answer("❌ Sizda admin huquqlari yo'q!")
            return
            
        if not message.text:
            return
            
        if message.text == "/cancel":
            await state.clear()
            await message.answer("❌ Test yaratish bekor qilindi")
            return
            
        data = await state.get_data()
        quiz_title = data.get("quiz_title", "")
        quiz_description = message.text.strip()
        
        if len(quiz_description) < 5:
            await message.answer("⚠️ Test tavsifi kamida 5 ta belgidan iborat bo'lishi kerak")
            return
            
        # Create quiz in database
        from .tests import create_quiz
        quiz_id = await create_quiz(quiz_title, quiz_description, "topik", "beginner")
        
        if quiz_id:
            await state.clear()
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="❓ Savol qo'shish", callback_data=f"add_question_to_{quiz_id}")],
                [InlineKeyboardButton(text="🧠 Testlar boshqaruvi", callback_data="admin_quiz")],
                [InlineKeyboardButton(text="🔙 Admin panel", callback_data="admin_panel")]
            ])
            
            await message.answer(
                f"✅ <b>Test muvaffaqiyatli yaratildi!</b>\n\n"
                f"📝 Nomi: {quiz_title}\n"
                f"📖 Tavsif: {quiz_description}\n"
                f"🆔 ID: {quiz_id}\n\n"
                f"Endi testga savollar qo'shishingiz mumkin:",
                reply_markup=keyboard,
                parse_mode="HTML"
            )
        else:
            await message.answer("❌ Test yaratishda xatolik yuz berdi")
            
    except Exception as e:
        print(f"Quiz description error: {e}")
        await message.answer("❌ Xatolik yuz berdi")

@router.message(F.text, StateFilter("granting_premium"))
async def receive_premium_user_id(message: Message, state: FSMContext):
    """Grant premium to user by ID"""
    try:
        if not message.from_user or message.from_user.id != ADMIN_ID:
            await message.answer("❌ Sizda admin huquqlari yo'q!")
            return
            
        if not message.text:
            return
            
        if message.text == "/cancel":
            await state.clear()
            await message.answer("❌ Premium berish bekor qilindi")
            return
            
        try:
            user_id = int(message.text.strip())
        except ValueError:
            await message.answer("⚠️ Foydalanuvchi ID raqam bo'lishi kerak")
            return
            
        # Check if user exists and grant premium
        async with aiosqlite.connect(DATABASE_PATH) as db:
            cursor = await db.execute("SELECT first_name, is_premium FROM users WHERE user_id = ?", (user_id,))
            user = await cursor.fetchone()
            
            if not user:
                await message.answer("❌ Bunday foydalanuvchi topilmadi")
                return
                
            first_name, is_premium = user
            
            if is_premium:
                await message.answer(f"⚠️ {first_name} allaqachon premium foydalanuvchi")
                return
                
            # Grant premium for 30 days
            from datetime import datetime, timedelta
            premium_expires_at = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
            
            await db.execute("""
                UPDATE users 
                SET is_premium = 1, premium_expires_at = ? 
                WHERE user_id = ?
            """, (premium_expires_at, user_id))
            await db.commit()
            
        await state.clear()
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💎 Premium boshqaruv", callback_data="admin_premium")],
            [InlineKeyboardButton(text="🔙 Admin panel", callback_data="admin_panel")]
        ])
        
        await message.answer(
            f"✅ <b>Premium muvaffaqiyatli berildi!</b>\n\n"
            f"👤 Foydalanuvchi: {first_name}\n"
            f"🆔 ID: {user_id}\n"
            f"📅 Muddat: {premium_expires_at} gacha",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        
        # Notify user about premium
        try:
            bot = Bot(token=BOT_TOKEN)
            await bot.send_message(
                user_id,
                "🎉 <b>Tabriklaymiz!</b>\n\n"
                "Sizga admin tomonidan 30 kunlik premium obuna berildi!\n\n"
                "💎 Premium imkoniyatlar:\n"
                "• Barcha testlarga kirish\n"
                "• Premium kontentlar\n"
                "• Cheksiz AI suhbat\n\n"
                "Premium obunangizdan foydalaning! 🚀",
                parse_mode="HTML"
            )
        except Exception:
            pass  # User might have blocked bot
            
    except Exception as e:
        print(f"Grant premium error: {e}")
        await message.answer("❌ Xatolik yuz berdi")

@router.callback_query(F.data == "revoke_premium")
async def revoke_premium(callback: CallbackQuery, state: FSMContext):
    """Remove premium from user"""
    try:
        if not callback.from_user or callback.from_user.id != ADMIN_ID:
            await callback.answer("❌ Sizda admin huquqlari yo'q!", show_alert=True)
            return
            
        await state.set_state("revoking_premium")
        
        if not callback.message:
            await callback.answer("❌ Xatolik yuz berdi", show_alert=True)
            return
            
        message = cast(Message, callback.message)
        await message.edit_text(
            "❌ <b>Premium olib tashlash</b>\n\n"
            "Foydalanuvchi ID raqamini kiriting:\n\n"
            "💡 /cancel - bekor qilish",
            reply_markup=None,
            parse_mode="HTML"
        )
        await callback.answer()
        
    except Exception as e:
        print(f"Revoke premium error: {e}")
        await callback.answer("❌ Xatolik yuz berdi", show_alert=True)

@router.callback_query(F.data == "premium_stats")
async def premium_stats(callback: CallbackQuery):
    """Premium statistics"""
    try:
        if not callback.from_user or callback.from_user.id != ADMIN_ID:
            await callback.answer("❌ Sizda admin huquqlari yo'q!", show_alert=True)
            return
            
        if not callback.message:
            await callback.answer("❌ Xatolik yuz berdi", show_alert=True)
            return
            
        # Get comprehensive premium statistics
        async with aiosqlite.connect(DATABASE_PATH) as db:
            # Total users
            cursor = await db.execute("SELECT COUNT(*) FROM users")
            total_users = (await cursor.fetchone())[0]
            
            # Premium users
            cursor = await db.execute("SELECT COUNT(*) FROM users WHERE is_premium = 1")
            premium_users = (await cursor.fetchone())[0]
            
            # New users this week
            cursor = await db.execute("""
                SELECT COUNT(*) FROM users 
                WHERE created_at >= datetime('now', '-7 days')
            """)
            new_users_week = (await cursor.fetchone())[0]
            
            # Premium users this week
            cursor = await db.execute("""
                SELECT COUNT(*) FROM users 
                WHERE is_premium = 1 AND premium_expires_at >= datetime('now')
            """)
            active_premium = (await cursor.fetchone())[0]
            
            # Expired premium
            cursor = await db.execute("""
                SELECT COUNT(*) FROM users 
                WHERE is_premium = 1 AND premium_expires_at < datetime('now')
            """)
            expired_premium = (await cursor.fetchone())[0]
            
            # Top users by rating
            cursor = await db.execute("""
                SELECT first_name, rating_score, is_premium FROM users 
                WHERE rating_score > 0
                ORDER BY rating_score DESC 
                LIMIT 5
            """)
            top_users = await cursor.fetchall()
        
        premium_percentage = (premium_users / total_users * 100) if total_users > 0 else 0
        
        stats_text = f"""📊 <b>Premium Statistikalar</b>

👥 <b>Foydalanuvchilar:</b>
• Jami: {total_users}
• Premium: {premium_users} ({premium_percentage:.1f}%)
• Aktiv premium: {active_premium}
• Muddati o'tgan: {expired_premium}

📈 <b>Bu hafta:</b>
• Yangi foydalanuvchilar: {new_users_week}

⭐ <b>Top foydalanuvchilar:</b>
"""
        
        for i, (name, rating, is_premium) in enumerate(top_users, 1):
            premium_mark = "💎" if is_premium else "🆓"
            unknown_text = "Noma'lum"
            stats_text += f"{i}. {name or unknown_text} - {rating or 0} ⭐ {premium_mark}\n"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Yangilash", callback_data="premium_stats")],
            [InlineKeyboardButton(text="🔙 Premium boshqaruv", callback_data="admin_premium")]
        ])
        
        message = cast(Message, callback.message)
        await message.edit_text(
            stats_text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        await callback.answer()
        
    except Exception as e:
        print(f"Premium stats error: {e}")
        await callback.answer("❌ Xatolik yuz berdi", show_alert=True)

@router.message(F.text, StateFilter("revoking_premium"))
async def receive_revoke_premium_id(message: Message, state: FSMContext):
    """Process premium removal"""
    try:
        if not message.from_user or message.from_user.id != ADMIN_ID:
            await message.answer("❌ Sizda admin huquqlari yo'q!")
            return
            
        if not message.text:
            return
            
        if message.text == "/cancel":
            await state.clear()
            await message.answer("❌ Premium olib tashlash bekor qilindi")
            return
            
        try:
            user_id = int(message.text.strip())
        except ValueError:
            await message.answer("⚠️ Foydalanuvchi ID raqam bo'lishi kerak")
            return
            
        # Check if user exists and remove premium
        async with aiosqlite.connect(DATABASE_PATH) as db:
            cursor = await db.execute("SELECT first_name, is_premium FROM users WHERE user_id = ?", (user_id,))
            user = await cursor.fetchone()
            
            if not user:
                await message.answer("❌ Bunday foydalanuvchi topilmadi")
                return
                
            first_name, is_premium = user
            
            if not is_premium:
                await message.answer(f"⚠️ {first_name} premium foydalanuvchi emas")
                return
                
            # Remove premium
            await db.execute("""
                UPDATE users 
                SET is_premium = 0, premium_expires_at = NULL 
                WHERE user_id = ?
            """, (user_id,))
            await db.commit()
            
        await state.clear()
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💎 Premium boshqaruv", callback_data="admin_premium")],
            [InlineKeyboardButton(text="🔙 Admin panel", callback_data="admin_panel")]
        ])
        
        await message.answer(
            f"✅ <b>Premium muvaffaqiyatli olib tashlandi!</b>\n\n"
            f"👤 Foydalanuvchi: {first_name}\n"
            f"🆔 ID: {user_id}",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        
        # Notify user about premium removal
        try:
            bot = Bot(token=BOT_TOKEN)
            await bot.send_message(
                user_id,
                "📢 <b>Premium obuna tugadi</b>\n\n"
                "Sizning premium obunangiz admin tomonidan bekor qilindi.\n\n"
                "Premium obunani qayta olish uchun /premium buyrug'idan foydalaning.",
                parse_mode="HTML"
            )
        except Exception:
            pass  # User might have blocked bot
            
    except Exception as e:
        print(f"Revoke premium error: {e}")
        await message.answer("❌ Xatolik yuz berdi")

# Catch-all for other admin callbacks
@router.callback_query(F.data.startswith("admin_"))
async def admin_catch_all(callback: CallbackQuery):
    """Safe catch-all for admin callbacks"""
    try:
        # Check admin access
        if not callback.from_user or callback.from_user.id != ADMIN_ID:
            await callback.answer("❌ Sizda admin huquqlari yo'q!", show_alert=True)
            return
            
        if not callback.message:
            await callback.answer("❌ Xatolik yuz berdi", show_alert=True)
            return
            
        message = cast(Message, callback.message)
        await message.edit_text(
            "🔧 <b>Admin Panel</b>\n\n"
            "Bu funksiya hozircha ishlab chiqilmoqda...\n\n"
            "Asosiy admin funksiyalar:\n"
            "• 📊 Statistika\n"
            "• 📢 Barchaga xabar yuborish",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📊 Statistika", callback_data="admin_stats")],
                [InlineKeyboardButton(text="📢 Xabar yuborish", callback_data="admin_broadcast")],
                [InlineKeyboardButton(text="🔙 Bosh menu", callback_data="main_menu")]
            ])
        )
        await callback.answer()
    except Exception as e:
        print(f"Admin catch-all error: {e}")
        try:
            await callback.answer("❌ Xatolik yuz berdi", show_alert=True)
        except:
            pass