"""
Kontent boshqaruvi - video, audio, hujjat va matn yuklash
"""
import aiosqlite
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from typing import cast

from config import DATABASE_PATH, ADMIN_ID
from database import get_user

router = Router()

class ContentStates(StatesGroup):
    content_title = State()
    content_description = State()
    content_file = State()
    content_type_selected = State()

# Admin decorator removed - using direct admin check instead

# =====================
# DATABASE FUNCTIONS
# =====================

async def add_content(section_id: int, subsection_id: int, title: str, description: str, 
                     content_type: str, file_id: str = None, file_path: str = None, 
                     text_content: str = None, is_premium: bool = False):
    """Kontent qo'shish"""
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            cursor = await db.execute("""
                INSERT INTO content (
                    section_id, subsection_id, title, description, content_type,
                    file_id, file_path, content_text, is_premium, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """, (
                section_id or 0, subsection_id or 0, title, description, content_type,
                file_id, file_path, text_content, is_premium
            ))
            await db.commit()
            return cursor.lastrowid
    except Exception as e:
        print(f"Add content error: {e}")
        return None

async def get_content_by_section(section_id: int):
    """Bo'lim bo'yicha kontentni olish"""
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            cursor = await db.execute("""
                SELECT id, title, description, content_type, file_id, file_path, 
                       content_text, is_premium FROM content 
                WHERE section_id = ? ORDER BY created_at DESC
            """, (section_id,))
            return await cursor.fetchall()
    except Exception as e:
        print(f"Get content by section error: {e}")
        return []

async def get_content_by_subsection(subsection_id: int):
    """Pastki bo'lim bo'yicha kontentni olish"""
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            cursor = await db.execute("""
                SELECT id, title, description, content_type, file_id, file_path, 
                       content_text, is_premium FROM content 
                WHERE subsection_id = ? ORDER BY created_at DESC
            """, (subsection_id,))
            return await cursor.fetchall()
    except Exception as e:
        print(f"Get content by subsection error: {e}")
        return []

async def get_content_by_id(content_id: int):
    """ID bo'yicha kontentni olish"""
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            cursor = await db.execute("""
                SELECT id, section_id, subsection_id, title, description, content_type, 
                       file_id, file_path, content_text, is_premium FROM content 
                WHERE id = ?
            """, (content_id,))
            return await cursor.fetchone()
    except Exception as e:
        print(f"Get content by id error: {e}")
        return None

async def delete_content(content_id: int):
    """Kontentni o'chirish"""
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            await db.execute("DELETE FROM content WHERE id = ?", (content_id,))
            await db.commit()
            return True
    except Exception as e:
        print(f"Delete content error: {e}")
        return False

# =====================
# ADMIN HANDLERS
# =====================

@router.callback_query(F.data.startswith("add_content_"))
async def add_content_menu(callback: CallbackQuery, state: FSMContext):
    """Kontent qo'shish menyusi"""
    try:
        # Check admin access
        if not callback.from_user or callback.from_user.id != ADMIN_ID:
            await callback.answer("❌ Sizda admin huquqlari yo'q!", show_alert=True)
            return
        if not callback.data:
            await callback.answer("❌ Xatolik!", show_alert=True)
            return
            
        target_id = int(callback.data.split("_")[-1])
        target_type = "section"  # default
        
        # Check if it's subsection
        if "subsection" in callback.data:
            target_type = "subsection"
        
        await state.update_data(target_id=target_id, target_type=target_type)
        
        if not callback.message:
            await callback.answer("❌ Xatolik!", show_alert=True)
            return
            
        keyboard = [
            [InlineKeyboardButton(text="📝 Matn", callback_data="content_type_text")],
            [InlineKeyboardButton(text="🖼️ Rasm", callback_data="content_type_photo")],
            [InlineKeyboardButton(text="🎥 Video", callback_data="content_type_video")],
            [InlineKeyboardButton(text="🎵 Audio", callback_data="content_type_audio")],
            [InlineKeyboardButton(text="📄 Hujjat", callback_data="content_type_document")],
            [InlineKeyboardButton(text="🎶 Musiqa", callback_data="content_type_music")],
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_sections")]
        ]
        
        message = cast(Message, callback.message)
        await message.edit_text(
            "📁 <b>Kontent turi tanlang</b>\n\n"
            "Qanday turdagi kontent qo'shmoqchisiz?",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
            parse_mode="HTML"
        )
        await callback.answer()
        
    except Exception as e:
        print(f"Add content menu error: {e}")
        try:
            await callback.answer("❌ Xatolik!", show_alert=True)
        except:
            pass

@router.callback_query(F.data.startswith("content_type_"))
async def content_type_selected(callback: CallbackQuery, state: FSMContext):
    """Kontent turi tanlandi"""
    try:
        if not callback.from_user or callback.from_user.id != ADMIN_ID:
            await callback.answer("❌ Sizda admin huquqlari yo'q!", show_alert=True)
            return
        if not callback.data:
            await callback.answer("❌ Xatolik!", show_alert=True)
            return
        content_type = callback.data.split("_")[-1]
        await state.update_data(content_type=content_type)
        await state.set_state(ContentStates.content_title)
        
        type_names = {
            "text": "📝 Matn",
            "photo": "🖼️ Rasm", 
            "video": "🎥 Video",
            "audio": "🎵 Audio",
            "document": "📄 Hujjat",
            "music": "🎶 Musiqa"
        }
        
        if not callback.message:
            await callback.answer("❌ Xatolik!", show_alert=True)
            return
            
        message = cast(Message, callback.message)
        await message.edit_text(
            f"📝 <b>{type_names.get(content_type, 'Kontent')} qo'shish</b>\n\n"
            "Kontent sarlavhasini yozing:\n\n"
            "💡 /cancel - bekor qilish",
            reply_markup=None,
            parse_mode="HTML"
        )
        await callback.answer()
        
    except Exception as e:
        print(f"Content type selected error: {e}")
        try:
            await callback.answer("❌ Xatolik!", show_alert=True)
        except:
            pass

@router.message(ContentStates.content_title)
async def content_title_received(message: Message, state: FSMContext):
    """Kontent sarlavhasi qabul qilish"""
    try:
        if not message.from_user or message.from_user.id != ADMIN_ID:
            await message.answer("❌ Sizda admin huquqlari yo'q!")
            return
            
        if not message or not message.text:
            return
            
        if message.text == "/cancel":
            await state.clear()
            await message.answer("❌ Bekor qilindi")
            return
        
        await state.update_data(title=message.text)
        await state.set_state(ContentStates.content_description)
        
        await message.answer(
            f"✅ <b>Sarlavha:</b> {message.text}\n\n"
            "📝 Endi kontent ta'rifini yozing:\n\n"
            "💡 /cancel - bekor qilish",
            parse_mode="HTML"
        )
        
    except Exception as e:
        print(f"Content title received error: {e}")

@router.message(ContentStates.content_description)
async def content_description_received(message: Message, state: FSMContext):
    """Kontent ta'rifi qabul qilish"""
    try:
        if not message.from_user or message.from_user.id != ADMIN_ID:
            await message.answer("❌ Sizda admin huquqlari yo'q!")
            return
            
        if not message or not message.text:
            return
            
        if message.text == "/cancel":
            await state.clear()
            await message.answer("❌ Bekor qilindi")
            return
        
        data = await state.get_data()
        content_type = data.get('content_type', '')
        
        await state.update_data(description=message.text)
        
        if content_type == "text":
            await state.set_state(ContentStates.content_file)
            await message.answer(
                f"✅ <b>Ta'rif:</b> {message.text}\n\n"
                "📝 Endi matn kontentini yozing:\n\n"
                "💡 /cancel - bekor qilish",
                parse_mode="HTML"
            )
        else:
            await state.set_state(ContentStates.content_file)
            file_types = {
                "photo": "🖼️ rasm",
                "video": "🎥 video", 
                "audio": "🎵 audio fayl",
                "document": "📄 hujjat",
                "music": "🎶 musiqa fayl"
            }
            await message.answer(
                f"✅ <b>Ta'rif:</b> {message.text}\n\n"
                f"📎 Endi {file_types.get(content_type, 'fayl')}ni yuboring:\n\n"
                "💡 /cancel - bekor qilish",
                parse_mode="HTML"
            )
        
    except Exception as e:
        print(f"Content description received error: {e}")

@router.message(ContentStates.content_file)
async def content_file_received(message: Message, state: FSMContext):
    """Kontent fayli qabul qilish"""
    try:
        if not message.from_user or message.from_user.id != ADMIN_ID:
            await message.answer("❌ Sizda admin huquqlari yo'q!")
            return
            
        if not message:
            return
            
        if message.text == "/cancel":
            await state.clear()
            await message.answer("❌ Bekor qilindi")
            return
        
        data = await state.get_data()
        content_type = data.get('content_type', '')
        target_id = data.get('target_id', 0)
        target_type = data.get('target_type', 'section')
        title = data.get('title', '')
        description = data.get('description', '')
        
        file_id = None
        text_content = None
        
        # Handle different content types
        if content_type == "text" and message.text:
            text_content = message.text
        elif content_type == "photo" and message.photo:
            file_id = message.photo[-1].file_id
        elif content_type == "video" and message.video:
            file_id = message.video.file_id
        elif content_type == "audio" and message.audio:
            file_id = message.audio.file_id
        elif content_type == "music" and (message.audio or message.voice):
            file_id = message.audio.file_id if message.audio else message.voice.file_id
        elif content_type == "document" and message.document:
            file_id = message.document.file_id
        else:
            await message.answer("❌ Noto'g'ri fayl turi. Qaytadan urinib ko'ring.")
            return
        
        # Save content
        section_id = target_id if target_type == "section" else 0
        subsection_id = target_id if target_type == "subsection" else 0
        
        content_id = await add_content(
            section_id=section_id,
            subsection_id=subsection_id,
            title=title,
            description=description,
            content_type=content_type,
            file_id=file_id,
            text_content=text_content,
            is_premium=False  # Default not premium
        )
        
        await state.clear()
        
        if content_id:
            type_names = {
                "text": "📝 Matn",
                "photo": "🖼️ Rasm", 
                "video": "🎥 Video",
                "audio": "🎵 Audio",
                "document": "📄 Hujjat",
                "music": "🎶 Musiqa"
            }
            
            await message.answer(
                f"✅ <b>{type_names.get(content_type, 'Kontent')} muvaffaqiyatli qo'shildi!</b>\n\n"
                f"📝 <b>Sarlavha:</b> {title}\n"
                f"📄 <b>Ta'rif:</b> {description}\n"
                f"🆔 <b>ID:</b> {content_id}",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="➕ Yana qo'shish", callback_data=f"add_content_{target_id}")],
                    [InlineKeyboardButton(text="📚 Bo'limlar", callback_data="admin_sections")]
                ]),
                parse_mode="HTML"
            )
        else:
            await message.answer("❌ Kontent qo'shishda xatolik yuz berdi")
        
    except Exception as e:
        print(f"Content file received error: {e}")

# =====================
# USER HANDLERS
# =====================

@router.callback_query(F.data.startswith("user_subsection_"))
async def user_subsection_view(callback: CallbackQuery):
    """Foydalanuvchi pastki bo'limini ko'rish"""
    try:
        if not callback.data:
            await callback.answer("❌ Xatolik!", show_alert=True)
            return
        subsection_id = int(callback.data.split("_")[-1])
        
        if not callback.message or not callback.from_user:
            await callback.answer("❌ Xatolik!", show_alert=True)
            return
        
        user_id = callback.from_user.id
        user = await get_user(user_id)
        
        # Premium check
        is_premium = user[8] if user and len(user) > 8 else False
        
        # Pastki bo'lim ma'lumotlarini olish
        async with aiosqlite.connect(DATABASE_PATH) as db:
            cursor = await db.execute("""
                SELECT s.id, s.name, s.description, sec.name as section_name
                FROM subsections s
                JOIN sections sec ON s.section_id = sec.id
                WHERE s.id = ?
            """, (subsection_id,))
            subsection = await cursor.fetchone()
        
        if not subsection:
            await callback.answer("❌ Pastki bo'lim topilmadi!", show_alert=True)
            return
        
        # Kontent olish
        content_list = await get_content_by_subsection(subsection_id)
        
        subsection_text = f"📖 <b>{subsection[1]}</b>\n"
        subsection_text += f"📚 Bo'lim: {subsection[3]}\n\n"
        subsection_text += f"📝 {subsection[2]}\n\n"
        
        keyboard = []
        
        if content_list:
            subsection_text += f"📁 <b>Mavjud kontentlar:</b>\n"
            for content in content_list:
                content_id, title, desc, c_type, file_id, file_path, text_content, is_content_premium = content
                
                # Premium content check
                if is_content_premium and not is_premium:
                    continue  # Skip premium content for non-premium users
                
                type_icons = {
                    "text": "📝", "photo": "🖼️", "video": "🎥", 
                    "audio": "🎵", "document": "📄", "music": "🎶"
                }
                icon = type_icons.get(c_type, "📄")
                premium_mark = " 💎" if is_content_premium else ""
                
                subsection_text += f"• {icon} {title}{premium_mark}\n"
                keyboard.append([InlineKeyboardButton(text=f"{icon} {title}", callback_data=f"view_content_{content_id}")])
        else:
            subsection_text += "📭 Hozircha kontent yo'q"
        
        # Premium content promotion for non-premium users
        if not is_premium:
            premium_content_count = len([c for c in content_list if c[7]])  # is_premium field
            if premium_content_count > 0:
                subsection_text += f"\n\n💎 <b>Premium kontentlar:</b> {premium_content_count} ta\n"
                subsection_text += "Premium obuna uchun /premium buyrug'idan foydalaning"
        
        keyboard.append([InlineKeyboardButton(text="🔙 Bo'limga qaytish", callback_data=f"user_section_{subsection[0]}")])
        
        message = cast(Message, callback.message)
        await message.edit_text(
            subsection_text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
            parse_mode="HTML"
        )
        await callback.answer()
        
    except Exception as e:
        print(f"User subsection view error: {e}")
        try:
            await callback.answer("❌ Xatolik!", show_alert=True)
        except:
            pass

@router.callback_query(F.data.startswith("view_content_"))
async def view_content(callback: CallbackQuery):
    """Kontentni ko'rish"""
    try:
        if not callback.data:
            await callback.answer("❌ Xatolik!", show_alert=True)
            return
        content_id = int(callback.data.split("_")[-1])
        
        if not callback.message or not callback.from_user:
            await callback.answer("❌ Xatolik!", show_alert=True)
            return
        
        user_id = callback.from_user.id
        user = await get_user(user_id)
        
        # Premium check
        is_premium = user[8] if user and len(user) > 8 else False
        
        # Kontent ma'lumotlarini olish
        content = await get_content_by_id(content_id)
        
        if not content:
            await callback.answer("❌ Kontent topilmadi!", show_alert=True)
            return
        
        content_id, section_id, subsection_id, title, description, content_type, file_id, file_path, text_content, is_content_premium = content
        
        # Premium content check
        if is_content_premium and not is_premium:
            await callback.answer("💎 Bu premium kontent! /premium buyrug'i orqali obuna bo'ling", show_alert=True)
            return
        
        # Send content based on type
        try:
            if content_type == "text" and text_content:
                await callback.message.answer(
                    f"📝 <b>{title}</b>\n\n"
                    f"📄 {description}\n\n"
                    f"📖 <b>Matn:</b>\n{text_content}",
                    parse_mode="HTML"
                )
            elif content_type == "photo" and file_id:
                await callback.message.answer_photo(
                    photo=file_id,
                    caption=f"🖼️ <b>{title}</b>\n\n📄 {description}",
                    parse_mode="HTML"
                )
            elif content_type == "video" and file_id:
                await callback.message.answer_video(
                    video=file_id,
                    caption=f"🎥 <b>{title}</b>\n\n📄 {description}",
                    parse_mode="HTML"
                )
            elif content_type in ["audio", "music"] and file_id:
                await callback.message.answer_audio(
                    audio=file_id,
                    caption=f"🎵 <b>{title}</b>\n\n📄 {description}",
                    parse_mode="HTML"
                )
            elif content_type == "document" and file_id:
                await callback.message.answer_document(
                    document=file_id,
                    caption=f"📄 <b>{title}</b>\n\n📄 {description}",
                    parse_mode="HTML"
                )
            else:
                await callback.answer("❌ Kontent mavjud emas!", show_alert=True)
                return
            
            await callback.answer("✅ Kontent yuborildi!")
            
            # Update user activity/rating here if needed
            from utils.rating_system import update_user_rating
            await update_user_rating(user_id, 'content_view')
            
        except Exception as send_error:
            print(f"Send content error: {send_error}")
            await callback.answer("❌ Kontentni yuborishda xatolik!", show_alert=True)
        
    except Exception as e:
        print(f"View content error: {e}")
        try:
            await callback.answer("❌ Xatolik!", show_alert=True)
        except:
            pass

# =====================
# ADMIN CONTENT MANAGEMENT
# =====================

@router.callback_query(F.data == "admin_content")
async def admin_content_menu(callback: CallbackQuery):
    """Admin kontent boshqaruvi"""
    try:
        if not callback.from_user or callback.from_user.id != ADMIN_ID:
            await callback.answer("❌ Sizda admin huquqlari yo'q!", show_alert=True)
            return
            
        if not callback.message:
            await callback.answer("❌ Xatolik!", show_alert=True)
            return
            
        # Get content statistics
        async with aiosqlite.connect(DATABASE_PATH) as db:
            cursor = await db.execute("SELECT COUNT(*) FROM content")
            total_content = (await cursor.fetchone())[0]
            
            cursor = await db.execute("SELECT COUNT(*) FROM content WHERE is_premium = 1")
            premium_content = (await cursor.fetchone())[0]
        
        content_text = f"📁 <b>Kontent boshqaruvi</b>\n\n"
        content_text += f"📊 <b>Statistika:</b>\n"
        content_text += f"• Jami kontent: {total_content}\n"
        content_text += f"• Premium kontent: {premium_content}\n\n"
        content_text += "Quyidagi amallardan birini tanlang:"
        
        keyboard = [
            [InlineKeyboardButton(text="📋 Barcha kontentlar", callback_data="view_all_content")],
            [InlineKeyboardButton(text="💎 Premium kontentlar", callback_data="view_premium_content")],
            [InlineKeyboardButton(text="🗑️ Kontent o'chirish", callback_data="content_delete_menu")],
            [InlineKeyboardButton(text="🔙 Admin panel", callback_data="admin_panel")]
        ]
        
        message = cast(Message, callback.message)
        await message.edit_text(
            content_text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
            parse_mode="HTML"
        )
        await callback.answer()
        
    except Exception as e:
        print(f"Admin content menu error: {e}")
        try:
            await callback.answer("❌ Xatolik!", show_alert=True)
        except:
            pass