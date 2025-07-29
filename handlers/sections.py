"""
Bo'limlar va pastki bo'limlar boshqaruvi
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

class SectionStates(StatesGroup):
    creating_section = State()
    section_name = State()
    section_description = State()
    creating_subsection = State()
    subsection_name = State()
    subsection_description = State()

def admin_only(func):
    """Admin decorator"""
    async def wrapper(*args, **kwargs):
        try:
            update = args[0] if args else None
            user_id = None
            
            if isinstance(update, Message) and update.from_user:
                user_id = update.from_user.id
            elif isinstance(update, CallbackQuery) and update.from_user:
                user_id = update.from_user.id
            
            if user_id != ADMIN_ID:
                if isinstance(update, CallbackQuery):
                    await update.answer("❌ Admin huquqlari kerak!", show_alert=True)
                return
            
            return await func(*args, **kwargs)
        except Exception as e:
            print(f"Admin decorator error: {e}")
            return
    return wrapper

# =====================
# DATABASE FUNCTIONS
# =====================

async def create_section(name: str, description: str, language: str = "korean", is_premium: bool = False):
    """Bo'lim yaratish"""
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            cursor = await db.execute("""
                INSERT INTO sections (name, description, language, is_premium, created_at) 
                VALUES (?, ?, ?, ?, datetime('now'))
            """, (name, description, language, is_premium))
            await db.commit()
            return cursor.lastrowid
    except Exception as e:
        print(f"Create section error: {e}")
        return None

async def create_subsection(section_id: int, name: str, description: str):
    """Pastki bo'lim yaratish"""
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            cursor = await db.execute("""
                INSERT INTO subsections (section_id, name, description, created_at) 
                VALUES (?, ?, ?, datetime('now'))
            """, (section_id, name, description))
            await db.commit()
            return cursor.lastrowid
    except Exception as e:
        print(f"Create subsection error: {e}")
        return None

async def get_sections(language: str = None):
    """Bo'limlarni olish"""
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            if language:
                cursor = await db.execute("""
                    SELECT id, name, description, language, is_premium FROM sections 
                    WHERE language = ? ORDER BY created_at DESC
                """, (language,))
            else:
                cursor = await db.execute("""
                    SELECT id, name, description, language, is_premium FROM sections 
                    ORDER BY created_at DESC
                """)
            return await cursor.fetchall()
    except Exception as e:
        print(f"Get sections error: {e}")
        return []

async def get_subsections(section_id: int):
    """Pastki bo'limlarni olish"""
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            cursor = await db.execute("""
                SELECT id, name, description FROM subsections 
                WHERE section_id = ? ORDER BY created_at DESC
            """, (section_id,))
            return await cursor.fetchall()
    except Exception as e:
        print(f"Get subsections error: {e}")
        return []

async def delete_section(section_id: int):
    """Bo'limni o'chirish"""
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            # Avval pastki bo'limlarni o'chirish
            await db.execute("DELETE FROM subsections WHERE section_id = ?", (section_id,))
            # Keyin bo'limni o'chirish
            await db.execute("DELETE FROM sections WHERE id = ?", (section_id,))
            await db.commit()
            return True
    except Exception as e:
        print(f"Delete section error: {e}")
        return False

# =====================
# ADMIN HANDLERS
# =====================

@router.callback_query(F.data == "admin_sections")
@admin_only
async def admin_sections_menu(callback: CallbackQuery):
    """Admin bo'limlar menusi"""
    try:
        if not callback.message:
            await callback.answer("❌ Xatolik!", show_alert=True)
            return
            
        sections = await get_sections()
        sections_text = "📚 <b>Bo'limlar boshqaruvi</b>\n\n"
        
        if sections:
            sections_text += "📋 <b>Mavjud bo'limlar:</b>\n"
            for section in sections:
                subsections = await get_subsections(section[0])
                sections_text += f"• {section[1]} ({len(subsections)} pastki bo'lim)\n"
        else:
            sections_text += "📭 Hozircha bo'limlar yo'q"
            
        keyboard = [
            [InlineKeyboardButton(text="➕ Bo'lim qo'shish", callback_data="create_section")],
            [InlineKeyboardButton(text="📋 Bo'limlarni ko'rish", callback_data="view_sections")],
            [InlineKeyboardButton(text="🗑️ Bo'lim o'chirish", callback_data="delete_sections_menu")],
            [InlineKeyboardButton(text="🔙 Admin panel", callback_data="admin_panel")]
        ]
        
        message = cast(Message, callback.message)
        await message.edit_text(
            sections_text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
            parse_mode="HTML"
        )
        await callback.answer()
        
    except Exception as e:
        print(f"Admin sections menu error: {e}")
        try:
            await callback.answer("❌ Xatolik yuz berdi", show_alert=True)
        except:
            pass

@router.callback_query(F.data == "create_section")
@admin_only
async def create_section_start(callback: CallbackQuery, state: FSMContext):
    """Bo'lim yaratishni boshlash"""
    try:
        await state.set_state(SectionStates.section_name)
        
        if not callback.message:
            await callback.answer("❌ Xatolik!", show_alert=True)
            return
            
        message = cast(Message, callback.message)
        await message.edit_text(
            "📚 <b>Yangi bo'lim yaratish</b>\n\n"
            "Bo'lim nomini yozing:\n\n"
            "💡 /cancel - bekor qilish",
            reply_markup=None,
            parse_mode="HTML"
        )
        await callback.answer()
        
    except Exception as e:
        print(f"Create section start error: {e}")
        try:
            await callback.answer("❌ Xatolik!", show_alert=True)
        except:
            pass

@router.message(SectionStates.section_name)
@admin_only
async def section_name_received(message: Message, state: FSMContext):
    """Bo'lim nomi qabul qilish"""
    try:
        if not message or not message.text:
            return
            
        if message.text == "/cancel":
            await state.clear()
            await message.answer("❌ Bekor qilindi")
            return
        
        await state.update_data(section_name=message.text)
        await state.set_state(SectionStates.section_description)
        
        await message.answer(
            f"✅ <b>Bo'lim nomi:</b> {message.text}\n\n"
            "📝 Endi bo'lim ta'rifini yozing:\n\n"
            "💡 /cancel - bekor qilish",
            parse_mode="HTML"
        )
        
    except Exception as e:
        print(f"Section name received error: {e}")

@router.message(SectionStates.section_description)
@admin_only
async def section_description_received(message: Message, state: FSMContext):
    """Bo'lim ta'rifi qabul qilish"""
    try:
        if not message or not message.text:
            return
            
        if message.text == "/cancel":
            await state.clear()
            await message.answer("❌ Bekor qilindi")
            return
        
        data = await state.get_data()
        section_name = data.get('section_name', '')
        
        # Bo'limni saqlash
        section_id = await create_section(
            name=section_name,
            description=message.text,
            language="korean",
            is_premium=False  # Default as free
        )
        
        await state.clear()
        
        if section_id:
            await message.answer(
                f"✅ <b>Bo'lim muvaffaqiyatli yaratildi!</b>\n\n"
                f"📚 <b>Nomi:</b> {section_name}\n"
                f"📝 <b>Ta'rifi:</b> {message.text}\n"
                f"🆔 <b>ID:</b> {section_id}",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="➕ Pastki bo'lim qo'shish", callback_data=f"add_subsection_{section_id}")],
                    [InlineKeyboardButton(text="📚 Bo'limlar", callback_data="admin_sections")]
                ]),
                parse_mode="HTML"
            )
        else:
            await message.answer("❌ Bo'lim yaratishda xatolik yuz berdi")
        
    except Exception as e:
        print(f"Section description received error: {e}")

@router.callback_query(F.data.startswith("add_subsection_"))
@admin_only
async def add_subsection_start(callback: CallbackQuery, state: FSMContext):
    """Pastki bo'lim qo'shishni boshlash"""
    try:
        section_id = int(callback.data.split("_")[-1])
        await state.update_data(section_id=section_id)
        await state.set_state(SectionStates.subsection_name)
        
        if not callback.message:
            await callback.answer("❌ Xatolik!", show_alert=True)
            return
            
        message = cast(Message, callback.message)
        await message.edit_text(
            "📂 <b>Pastki bo'lim qo'shish</b>\n\n"
            "Pastki bo'lim nomini yozing:\n\n"
            "💡 /cancel - bekor qilish",
            reply_markup=None,
            parse_mode="HTML"
        )
        await callback.answer()
        
    except Exception as e:
        print(f"Add subsection start error: {e}")
        try:
            await callback.answer("❌ Xatolik!", show_alert=True)
        except:
            pass

@router.message(SectionStates.subsection_name)
@admin_only
async def subsection_name_received(message: Message, state: FSMContext):
    """Pastki bo'lim nomi qabul qilish"""
    try:
        if not message or not message.text:
            return
            
        if message.text == "/cancel":
            await state.clear()
            await message.answer("❌ Bekor qilindi")
            return
        
        await state.update_data(subsection_name=message.text)
        await state.set_state(SectionStates.subsection_description)
        
        await message.answer(
            f"✅ <b>Pastki bo'lim nomi:</b> {message.text}\n\n"
            "📝 Endi pastki bo'lim ta'rifini yozing:\n\n"
            "💡 /cancel - bekor qilish",
            parse_mode="HTML"
        )
        
    except Exception as e:
        print(f"Subsection name received error: {e}")

@router.message(SectionStates.subsection_description)
@admin_only
async def subsection_description_received(message: Message, state: FSMContext):
    """Pastki bo'lim ta'rifi qabul qilish"""
    try:
        if not message or not message.text:
            return
            
        if message.text == "/cancel":
            await state.clear()
            await message.answer("❌ Bekor qilindi")
            return
        
        data = await state.get_data()
        section_id = data.get('section_id')
        subsection_name = data.get('subsection_name', '')
        
        # Pastki bo'limni saqlash
        subsection_id = await create_subsection(
            section_id=section_id,
            name=subsection_name,
            description=message.text
        )
        
        await state.clear()
        
        if subsection_id:
            await message.answer(
                f"✅ <b>Pastki bo'lim muvaffaqiyatli yaratildi!</b>\n\n"
                f"📂 <b>Nomi:</b> {subsection_name}\n"
                f"📝 <b>Ta'rifi:</b> {message.text}\n"
                f"🆔 <b>ID:</b> {subsection_id}",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="➕ Yana qo'shish", callback_data=f"add_subsection_{section_id}")],
                    [InlineKeyboardButton(text="📚 Bo'limlar", callback_data="admin_sections")]
                ]),
                parse_mode="HTML"
            )
        else:
            await message.answer("❌ Pastki bo'lim yaratishda xatolik yuz berdi")
        
    except Exception as e:
        print(f"Subsection description received error: {e}")

@router.callback_query(F.data == "view_sections")
@admin_only
async def view_sections(callback: CallbackQuery):
    """Bo'limlarni ko'rish"""
    try:
        if not callback.message:
            await callback.answer("❌ Xatolik!", show_alert=True)
            return
            
        sections = await get_sections()
        
        if not sections:
            message = cast(Message, callback.message)
            await message.edit_text(
                "📭 <b>Hozircha bo'limlar yo'q</b>\n\n"
                "Yangi bo'lim yaratish uchun '➕ Bo'lim qo'shish' tugmasini bosing",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="➕ Bo'lim qo'shish", callback_data="create_section")],
                    [InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_sections")]
                ]),
                parse_mode="HTML"
            )
            await callback.answer()
            return
        
        keyboard = []
        for section in sections:
            subsections = await get_subsections(section[0])
            button_text = f"📚 {section[1]} ({len(subsections)} pastki bo'lim)"
            keyboard.append([InlineKeyboardButton(text=button_text, callback_data=f"section_details_{section[0]}")])
        
        keyboard.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_sections")])
        
        message = cast(Message, callback.message)
        await message.edit_text(
            "📋 <b>Barcha bo'limlar</b>\n\n"
            "Bo'lim tafsilotlarini ko'rish uchun tanlang:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
            parse_mode="HTML"
        )
        await callback.answer()
        
    except Exception as e:
        print(f"View sections error: {e}")
        try:
            await callback.answer("❌ Xatolik!", show_alert=True)
        except:
            pass

@router.callback_query(F.data.startswith("section_details_"))
@admin_only
async def section_details(callback: CallbackQuery):
    """Bo'lim tafsilotlari"""
    try:
        section_id = int(callback.data.split("_")[-1])
        
        if not callback.message:
            await callback.answer("❌ Xatolik!", show_alert=True)
            return
        
        # Bo'lim ma'lumotlarini olish
        async with aiosqlite.connect(DATABASE_PATH) as db:
            cursor = await db.execute("""
                SELECT id, name, description, language FROM sections WHERE id = ?
            """, (section_id,))
            section = await cursor.fetchone()
        
        if not section:
            await callback.answer("❌ Bo'lim topilmadi!", show_alert=True)
            return
        
        subsections = await get_subsections(section_id)
        
        details_text = f"📚 <b>{section[1]}</b>\n\n"
        details_text += f"📝 <b>Ta'rif:</b> {section[2]}\n"
        details_text += f"🌐 <b>Til:</b> {section[3]}\n"
        details_text += f"🆔 <b>ID:</b> {section[0]}\n\n"
        
        if subsections:
            details_text += f"📂 <b>Pastki bo'limlar ({len(subsections)}):</b>\n"
            for sub in subsections:
                details_text += f"• {sub[1]}\n"
        else:
            details_text += "📭 Pastki bo'limlar yo'q"
        
        keyboard = [
            [InlineKeyboardButton(text="➕ Pastki bo'lim qo'shish", callback_data=f"add_subsection_{section_id}")],
            [InlineKeyboardButton(text="📁 Kontent qo'shish", callback_data=f"add_content_{section_id}")],
            [InlineKeyboardButton(text="🗑️ Bo'limni o'chirish", callback_data=f"delete_section_{section_id}")],
            [InlineKeyboardButton(text="🔙 Bo'limlar", callback_data="view_sections")]
        ]
        
        message = cast(Message, callback.message)
        await message.edit_text(
            details_text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
            parse_mode="HTML"
        )
        await callback.answer()
        
    except Exception as e:
        print(f"Section details error: {e}")
        try:
            await callback.answer("❌ Xatolik!", show_alert=True)
        except:
            pass

# =====================
# USER HANDLERS
# =====================

@router.callback_query(F.data == "sections")
async def user_sections(callback: CallbackQuery):
    """Foydalanuvchilar uchun bo'limlar"""  
    try:
        if not callback.message or not callback.from_user:
            await callback.answer("❌ Xatolik!", show_alert=True)
            return
            
        user_id = callback.from_user.id
        user = await get_user(user_id)
        
        if not user:
            await callback.answer("❌ Foydalanuvchi topilmadi!", show_alert=True)
            return
        
        sections = await get_sections("korean")
        
        if not sections:
            message = cast(Message, callback.message)
            await message.edit_text(
                "📭 <b>Hozircha bo'limlar yo'q</b>\n\n"
                "Admin tomonidan bo'limlar qo'shilguncha kuting",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 Bosh menu", callback_data="main_menu")]
                ]),
                parse_mode="HTML"
            )
            await callback.answer()
            return
        
        keyboard = []
        is_premium = user[8] if user and len(user) > 8 else False
        
        for section in sections:
            section_id, name, description, language, section_is_premium = section
            subsections = await get_subsections(section_id)
            
            if section_is_premium and not is_premium:
                # Non-premium user sees premium section with lock icon
                button_text = f"🔒 {name} (Premium) ({len(subsections)})"
                keyboard.append([InlineKeyboardButton(text=button_text, callback_data=f"premium_required_{section_id}")])
            else:
                # Premium user or free section
                icon = "💎" if section_is_premium else "📚"
                button_text = f"{icon} {name} ({len(subsections)})"
                keyboard.append([InlineKeyboardButton(text=button_text, callback_data=f"user_section_{section_id}")])
        
        keyboard.append([InlineKeyboardButton(text="🔙 Bosh menu", callback_data="main_menu")])
        
        message = cast(Message, callback.message)
        await message.edit_text(
            "📚 <b>O'quv bo'limlari</b>\n\n"
            "Qaysi bo'limni o'rganishni xohlaysiz?",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
            parse_mode="HTML"
        )
        await callback.answer()
        
    except Exception as e:
        print(f"User sections error: {e}")
        try:
            await callback.answer("❌ Xatolik!", show_alert=True)
        except:
            pass

@router.callback_query(F.data.startswith("user_section_"))
async def user_section_view(callback: CallbackQuery):
    """Foydalanuvchi bo'limini ko'rish"""
    try:
        section_id = int(callback.data.split("_")[-1])
        
        if not callback.message or not callback.from_user:
            await callback.answer("❌ Xatolik!", show_alert=True)
            return
        
        user_id = callback.from_user.id
        user = await get_user(user_id)
        
        # Premium check
        is_premium = user[8] if user and len(user) > 8 else False
        
        # Bo'lim ma'lumontlarini olish
        async with aiosqlite.connect(DATABASE_PATH) as db:
            cursor = await db.execute("""
                SELECT id, name, description, language, is_premium FROM sections WHERE id = ?
            """, (section_id,))
            section = await cursor.fetchone()
        
        if not section:
            await callback.answer("❌ Bo'lim topilmadi!", show_alert=True)
            return
            
        # Premium access check
        section_is_premium = section[4] if len(section) > 4 else False
        if section_is_premium and not is_premium:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="💎 Premium sotib olish", callback_data="premium")],
                [InlineKeyboardButton(text="🔙 Bo'limlar", callback_data="sections")]
            ])
            
            message = cast(Message, callback.message)
            await message.edit_text(
                f"🔒 <b>{section[1]}</b>\n\n"
                f"❌ Bu bo'lim premium foydalanuvchilar uchun!\n\n"
                f"💎 Premium obunani olish uchun /premium buyrug'idan foydalaning",
                reply_markup=keyboard,
                parse_mode="HTML"
            )
            await callback.answer("🔒 Premium bo'lim!", show_alert=True)
            return
        
        subsections = await get_subsections(section_id)
        
        # Bo'limning to'g'ridan-to'g'ri kontentini olish
        from .content import get_content_by_section
        all_content = await get_content_by_section(section_id)
        
        # Database da subsection_id ni to'g'ri olish uchun to'liq query
        direct_content = []
        if all_content:
            async with aiosqlite.connect(DATABASE_PATH) as db:
                cursor = await db.execute("""
                    SELECT id, title, description, content_type, file_id, file_path, 
                           content_text, is_premium, subsection_id FROM content 
                    WHERE section_id = ? AND subsection_id = 0 ORDER BY created_at DESC
                """, (section_id,))
                direct_content = await cursor.fetchall()
        
        premium_icon = "💎" if section_is_premium else "📚"
        section_text = f"{premium_icon} <b>{section[1]}</b>\n\n"
        section_text += f"📝 {section[2]}\n\n"
        
        keyboard = []
        
        # To'g'ridan-to'g'ri bo'lim kontentini ko'rsatish
        if direct_content:
            section_text += f"📁 <b>Bo'lim kontenti:</b>\n"
            for content in direct_content:
                content_id, title, desc, c_type, file_id, file_path, text_content, is_content_premium, subsection_id = content
                
                # Premium content check
                if is_content_premium and not is_premium:
                    continue  # Skip premium content for non-premium users
                
                type_icons = {
                    "text": "📝", "photo": "🖼️", "video": "🎥", 
                    "audio": "🎵", "document": "📄", "music": "🎶"
                }
                icon = type_icons.get(c_type, "📄")
                premium_mark = " 💎" if is_content_premium else ""
                
                section_text += f"• {icon} {title}{premium_mark}\n"
                keyboard.append([InlineKeyboardButton(text=f"{icon} {title}", callback_data=f"view_content_{content_id}")])
            
            section_text += "\n"
        
        # Pastki bo'limlarni ko'rsatish
        if subsections:
            section_text += f"📂 <b>Pastki bo'limlar:</b>\n"
            for sub in subsections:
                section_text += f"• {sub[1]}\n"
                keyboard.append([InlineKeyboardButton(text=f"📖 {sub[1]}", callback_data=f"user_subsection_{sub[0]}")])
        elif not direct_content:
            section_text += "📭 Hozircha kontent va pastki bo'limlar yo'q"
        
        keyboard.append([InlineKeyboardButton(text="🔙 Bo'limlar", callback_data="sections")])
        
        message = cast(Message, callback.message)
        await message.edit_text(
            section_text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
            parse_mode="HTML"
        )
        await callback.answer()
        
    except Exception as e:
        print(f"User section view error: {e}")
        try:
            await callback.answer("❌ Xatolik!", show_alert=True)
        except:
            pass

@router.callback_query(F.data.startswith("premium_required_"))
async def premium_required_handler(callback: CallbackQuery):
    """Premium bo'lim uchun upgrade taklifi"""
    try:
        section_id = int(callback.data.split("_")[-1])
        
        if not callback.message or not callback.from_user:
            await callback.answer("❌ Xatolik!", show_alert=True)
            return
            
        # Bo'lim nomini olish
        async with aiosqlite.connect(DATABASE_PATH) as db:
            cursor = await db.execute("SELECT name FROM sections WHERE id = ?", (section_id,))
            section = await cursor.fetchone()
        
        section_name = section[0] if section else "Noma'lum bo'lim"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💎 Premium sotib olish", callback_data="premium")],
            [InlineKeyboardButton(text="👥 Do'stlaringizni taklif qiling", callback_data="referral_info")],
            [InlineKeyboardButton(text="🔙 Bo'limlar", callback_data="sections")]
        ])
        
        message = cast(Message, callback.message)
        await message.edit_text(
            f"🔒 <b>{section_name}</b>\n\n"
            f"❌ Bu bo'lim premium foydalanuvchilar uchun mo'ljallangan!\n\n"
            f"💎 <b>Premium afzalliklari:</b>\n"
            f"• Barcha premium bo'limlarga kirish\n"
            f"• AI suhbat bilan amaliyot\n"
            f"• Mukammal testlar va materiallar\n"
            f"• Tezkor yordam va qo'llab-quvvatlash\n\n"
            f"🎁 <b>Bepul olish:</b> 3 ta do'stingizni taklif qiling!",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        await callback.answer("🔒 Premium kerak!", show_alert=True)
        
    except Exception as e:
        print(f"Premium required handler error: {e}")
        try:
            await callback.answer("❌ Xatolik!", show_alert=True)
        except:
            pass