from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import CHANNELS, INSTAGRAM_URL

def get_subscription_keyboard():
    """Keyboard for subscription verification"""
    buttons = []
    
    # Add channel subscription buttons
    for channel_username, channel_name in CHANNELS.items():
        buttons.append([
            InlineKeyboardButton(
                text=f"📱 {channel_name}",
                url=f"https://t.me/{channel_username[1:]}"  # Remove @ symbol
            )
        ])
    
    # Add Instagram button
    buttons.append([
        InlineKeyboardButton(
            text="📷 Instagram sahifamiz",
            url=INSTAGRAM_URL
        )
    ])
    
    # Add check subscription button
    buttons.append([
        InlineKeyboardButton(
            text="✅ Obunani tekshirish",
            callback_data="check_subscription"
        )
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_main_menu(is_admin: bool = False, is_premium: bool = False):
    """Main menu keyboard"""
    buttons = [
        [
            InlineKeyboardButton(text="📚 Bo'limlar", callback_data="sections"),
            InlineKeyboardButton(text="🧠 Testlar", callback_data="tests")
        ],
        [
            InlineKeyboardButton(text="🤖 AI suhbat", callback_data="conversation"),
            InlineKeyboardButton(text="🏆 Reyting", callback_data="rating")
        ],
        [
            InlineKeyboardButton(text="💎 Premium", callback_data="premium"),
            InlineKeyboardButton(text="📊 Mening statistikam", callback_data="my_stats")
        ]
    ]
    
    if is_admin:
        buttons.append([
            InlineKeyboardButton(text="⚙️ Admin panel", callback_data="admin_panel")
        ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_conversation_menu():
    """Premium conversation language selection menu"""
    buttons = [
        [
            InlineKeyboardButton(text="🇰🇷 Kores AI & Grammar (Premium)", callback_data="korean_conversation")
        ],
        [
            InlineKeyboardButton(text="🇯🇵 Yapon AI & Grammar (Premium)", callback_data="japanese_conversation")
        ],
        [
            InlineKeyboardButton(text="💡 Premium AI Info", callback_data="conversation_tips")
        ],
        [
            InlineKeyboardButton(text="🔙 Bosh menu", callback_data="main_menu")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_conversation_keyboard(language):
    """Conversation keyboard for specific language"""
    if language == "korean":
        buttons = [
            [
                InlineKeyboardButton(text="💡 Kores maslahatlari", callback_data="conversation_tips")
            ],
            [
                InlineKeyboardButton(text="🔙 Suhbat menu", callback_data="conversation"),
                InlineKeyboardButton(text="🏠 Bosh menu", callback_data="main_menu")
            ]
        ]
    else:  # japanese
        buttons = [
            [
                InlineKeyboardButton(text="💡 Yapon maslahatlari", callback_data="conversation_tips")
            ],
            [
                InlineKeyboardButton(text="🔙 Suhbat menu", callback_data="conversation"),
                InlineKeyboardButton(text="🏠 Bosh menu", callback_data="main_menu")
            ]
        ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_grammar_ai_menu():
    """Grammar AI language selection menu"""
    buttons = [
        [
            InlineKeyboardButton(text="🇰🇷 Kores Grammar AI", callback_data="korean_grammar"),
            InlineKeyboardButton(text="🇯🇵 Yapon Grammar AI", callback_data="japanese_grammar")
        ],
        [
            InlineKeyboardButton(text="💡 Grammar AI qo'llanma", callback_data="grammar_guide")
        ],
        [
            InlineKeyboardButton(text="🔙 Bosh menu", callback_data="main_menu")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_admin_menu():
    """Admin panel main menu"""
    buttons = [
        [
            InlineKeyboardButton(text="📚 Bo'limlar", callback_data="admin_sections"),
            InlineKeyboardButton(text="📁 Kontent", callback_data="admin_content")
        ],
        [
            InlineKeyboardButton(text="🧠 Testlar", callback_data="admin_quiz"),
            InlineKeyboardButton(text="📊 Statistika", callback_data="admin_stats")
        ],
        [
            InlineKeyboardButton(text="💎 Premium boshqaruv", callback_data="admin_premium"),
            InlineKeyboardButton(text="💳 To'lov tasdiqlash", callback_data="admin_payments")
        ],
        [
            InlineKeyboardButton(text="🗑️ Content o'chirish", callback_data="content_delete_menu"),
            InlineKeyboardButton(text="📨 Test xabarlar", callback_data="admin_test_messages")
        ],
        [
            InlineKeyboardButton(text="🗑 Bo'limlarni o'chirish", callback_data="admin_delete_sections")
        ],
        [
            InlineKeyboardButton(text="📢 Barchaga xabar", callback_data="admin_broadcast")
        ],
        [
            InlineKeyboardButton(text="🔙 Orqaga", callback_data="main_menu")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_admin_sections_keyboard():
    """Admin sections management keyboard"""
    buttons = [
        [
            InlineKeyboardButton(text="➕ Bo'lim yaratish", callback_data="create_section"),
            InlineKeyboardButton(text="➕ Pastki bo'lim yaratish", callback_data="create_subsection")
        ],
        [
            InlineKeyboardButton(text="📋 Bo'limlar ro'yxati", callback_data="list_sections")
        ],
        [
            InlineKeyboardButton(text="🔙 Admin panel", callback_data="admin_panel")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_admin_content_keyboard():
    """Content management keyboard"""
    buttons = [
        [
            InlineKeyboardButton(text="📤 Kontent yuklash", callback_data="upload_content")
        ],
        [
            InlineKeyboardButton(text="📋 Kontent ro'yxati", callback_data="list_content")
        ],
        [
            InlineKeyboardButton(text="🔙 Admin panel", callback_data="admin_panel")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_broadcast_menu():
    """Broadcast message type selection"""
    buttons = [
        [
            InlineKeyboardButton(text="📝 Matn xabar", callback_data="broadcast_text"),
            InlineKeyboardButton(text="🖼 Rasm + matn", callback_data="broadcast_photo")
        ],
        [
            InlineKeyboardButton(text="🎥 Video + matn", callback_data="broadcast_video"),
            InlineKeyboardButton(text="🎵 Audio + matn", callback_data="broadcast_audio")
        ],
        [
            InlineKeyboardButton(text="📎 Fayl + matn", callback_data="broadcast_document")
        ],
        [
            InlineKeyboardButton(text="🔙 Admin panel", callback_data="admin_panel")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_broadcast_confirm():
    """Broadcast confirmation keyboard"""
    buttons = [
        [
            InlineKeyboardButton(text="✅ Ha, yuborish", callback_data="confirm_broadcast"),
            InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_broadcast")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_admin_quiz_keyboard():
    """Quiz management keyboard"""
    buttons = [
        [
            InlineKeyboardButton(text="➕ Test yaratish", callback_data="create_quiz")
        ],
        [
            InlineKeyboardButton(text="📋 Testlar ro'yxati", callback_data="list_quizzes"),
            InlineKeyboardButton(text="🗑️ Test o'chirish", callback_data="delete_quizzes")
        ],
        [
            InlineKeyboardButton(text="📥 Testlarni import", callback_data="import_quizzes"),
            InlineKeyboardButton(text="📤 Export qilish", callback_data="export_quizzes")
        ],
        [
            InlineKeyboardButton(text="🔙 Admin panel", callback_data="admin_panel")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_quiz_continue_keyboard():
    """Keyboard for quiz creation continuation"""
    buttons = [
        [
            InlineKeyboardButton(text="➕ Yana savol qo'shish", callback_data="add_more_questions")
        ],
        [
            InlineKeyboardButton(text="✅ Testni yakunlash", callback_data="finish_quiz")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_topic_tests_keyboard(topic_number):
    """Keyboard for topic tests"""
    buttons = [
        [
            InlineKeyboardButton(text="📝 Lug'at testlari", callback_data=f"vocabulary_test_{topic_number}"),
            InlineKeyboardButton(text="📖 Grammatika testlari", callback_data=f"grammar_test_{topic_number}")
        ],
        [
            InlineKeyboardButton(text="🎯 Aralash testlar", callback_data=f"mixed_test_{topic_number}"),
            InlineKeyboardButton(text="🏃‍♂️ Tezlik testlari", callback_data=f"speed_test_{topic_number}")
        ],
        [
            InlineKeyboardButton(text="🔙 Bosh menu", callback_data="main_menu")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_jlpt_tests_keyboard():
    """Keyboard for JLPT tests (Premium only)"""
    buttons = [
        [
            InlineKeyboardButton(text="🥉 JLPT N5 testlari", callback_data="jlpt_n5_tests"),
            InlineKeyboardButton(text="🥈 JLPT N4 testlari", callback_data="jlpt_n4_tests")
        ],
        [
            InlineKeyboardButton(text="🥇 JLPT N3 testlari", callback_data="jlpt_n3_tests"),
            InlineKeyboardButton(text="💎 JLPT N2 testlari", callback_data="jlpt_n2_tests")
        ],
        [
            InlineKeyboardButton(text="👑 JLPT N1 testlari", callback_data="jlpt_n1_tests")
        ],
        [
            InlineKeyboardButton(text="💎 Premium olish", callback_data="premium"),
            InlineKeyboardButton(text="🔙 Bosh menu", callback_data="main_menu")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_jlpt_level_tests_keyboard(level):
    """Keyboard for specific JLPT level tests"""
    buttons = [
        [
            InlineKeyboardButton(text="📝 Lug'at (語彙)", callback_data=f"jlpt_{level}_vocabulary"),
            InlineKeyboardButton(text="📖 Grammatika (文法)", callback_data=f"jlpt_{level}_grammar")
        ],
        [
            InlineKeyboardButton(text="📚 O'qish (読解)", callback_data=f"jlpt_{level}_reading"),
            InlineKeyboardButton(text="👂 Tinglash (聴解)", callback_data=f"jlpt_{level}_listening")
        ],
        [
            InlineKeyboardButton(text="🎯 Aralash imtihon", callback_data=f"jlpt_{level}_mixed"),
            InlineKeyboardButton(text="⏱ Vaqtli imtihon", callback_data=f"jlpt_{level}_timed")
        ],
        [
            InlineKeyboardButton(text="🔙 JLPT testlari", callback_data="jlpt_tests")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_languages_keyboard():
    """Language selection keyboard"""
    buttons = [
        [
            InlineKeyboardButton(text="🇰🇷 Koreys tili", callback_data="korean"),
            InlineKeyboardButton(text="🇯🇵 Yapon tili", callback_data="japanese")
        ],
        [
            InlineKeyboardButton(text="🔙 Bosh menu", callback_data="main_menu")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_sections_keyboard(sections, language):
    """Keyboard for sections list"""
    buttons = []
    
    for section in sections:
        section_id, name, description, lang, is_premium, created_at, created_by = section
        premium_icon = "💎 " if is_premium else ""
        buttons.append([
            InlineKeyboardButton(
                text=f"{premium_icon}{name}",
                callback_data=f"section_{section_id}"
            )
        ])
    
    buttons.append([
        InlineKeyboardButton(text="🔙 Tillar", callback_data="learn")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_subsections_keyboard(subsections, section_id, language):
    """Keyboard for subsections list"""
    buttons = []
    
    for subsection in subsections:
        sub_id, sec_id, name, description, is_premium, created_at = subsection
        premium_icon = "💎 " if is_premium else ""
        buttons.append([
            InlineKeyboardButton(
                text=f"{premium_icon}{name}",
                callback_data=f"subsection_{sub_id}"
            )
        ])
    
    buttons.append([
        InlineKeyboardButton(
            text="🔙 Bo'limlar", 
            callback_data=f"back_to_sections_{language}"
        )
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_content_keyboard(subsection_id, section_id, language, content_items):
    """Keyboard for content list"""
    buttons = []
    
    for content in content_items:
        # Handle variable number of columns - content table has: id, subsection_id, title, file_id, file_type, caption, is_premium, created_at, content_text
        if len(content) >= 8:
            content_id, sub_id, title, file_id, file_type, caption, is_premium, created_at = content[:8]
        else:
            # Fallback for older structure
            content_id, sub_id, title, file_id, file_type, caption, is_premium, created_at = content
        
        # Add file type emoji
        type_emoji = {
            'video': '🎥',
            'audio': '🎵',
            'photo': '🖼',
            'document': '📄',
            'text': '📄'
        }.get(file_type, '📁')
        
        premium_icon = "💎 " if is_premium else ""
        
        # Limit title length for button text
        display_title = title[:30] + "..." if len(title) > 30 else title
        
        buttons.append([
            InlineKeyboardButton(
                text=f"{premium_icon}{type_emoji} {display_title}",
                callback_data=f"content_{content_id}"
            )
        ])
    
    buttons.append([
        InlineKeyboardButton(
            text="🔙 Pastki bo'limlar",
            callback_data=f"back_to_subsections_{section_id}_{language}"
        )
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_content_navigation_keyboard(subsection_id, section_id, language):
    """Keyboard for content navigation"""
    buttons = [
        [
            InlineKeyboardButton(
                text="🔙 Kontentlar",
                callback_data=f"back_to_content_{subsection_id}"
            )
        ],
        [
            InlineKeyboardButton(text="🏠 Bosh menu", callback_data="main_menu")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_premium_menu(is_premium: bool = False, can_activate_by_referral: bool = False):
    """Premium menu keyboard"""
    if is_premium:
        buttons = [
            [
                InlineKeyboardButton(text="💎 Premium imkoniyatlari", callback_data="premium_features")
            ],
            [
                InlineKeyboardButton(text="👥 Mening referrallarim", callback_data="my_referrals")
            ],
            [
                InlineKeyboardButton(text="🔙 Bosh menu", callback_data="main_menu")
            ]
        ]
    else:
        buttons = [
            [
                InlineKeyboardButton(text="💳 Premium sotib olish", callback_data="buy_premium")
            ],
            [
                InlineKeyboardButton(text="👥 Do'stlarni taklif qilish", callback_data="referral_premium")
            ]
        ]
        
        if can_activate_by_referral:
            buttons.insert(1, [
                InlineKeyboardButton(text="🎉 Premium faollashtirish", callback_data="activate_referral_premium")
            ])
        
        buttons.extend([
            [
                InlineKeyboardButton(text="💎 Premium imkoniyatlari", callback_data="premium_features")
            ],
            [
                InlineKeyboardButton(text="🔙 Bosh menu", callback_data="main_menu")
            ]
        ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_referral_keyboard():
    """Referral system keyboard"""
    buttons = [
        [
            InlineKeyboardButton(text="🔗 Mening referral linkim", callback_data="my_referral_code")
        ],
        [
            InlineKeyboardButton(text="👥 Mening referrallarim", callback_data="my_referrals")
        ],
        [
            InlineKeyboardButton(text="💳 To'lov qilish", callback_data="buy_premium")
        ],
        [
            InlineKeyboardButton(text="📞 Admin bilan bog'lanish", url="https://t.me/chang_chi_won")
        ],
        [
            InlineKeyboardButton(text="🔙 Premium", callback_data="premium")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_quiz_languages_keyboard():
    """Quiz language selection keyboard"""
    buttons = [
        [
            InlineKeyboardButton(text="🇰🇷 Koreys tili testlari", callback_data="quiz_korean"),
            InlineKeyboardButton(text="🇯🇵 Yapon tili testlari", callback_data="quiz_japanese")
        ],
        [
            InlineKeyboardButton(text="📊 Mening statistikam", callback_data="quiz_stats")
        ],
        [
            InlineKeyboardButton(text="🔙 Bosh menu", callback_data="main_menu")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_quizzes_keyboard(quizzes, language):
    """Keyboard for quizzes list"""
    buttons = []
    
    for quiz in quizzes:
        quiz_id, title, description, is_premium = quiz
        premium_icon = "💎 " if is_premium else ""
        
        buttons.append([
            InlineKeyboardButton(
                text=f"{premium_icon}🧠 {title}",
                callback_data=f"start_quiz_{quiz_id}"
            )
        ])
    
    buttons.append([
        InlineKeyboardButton(text="🔙 Testlar", callback_data="quizzes")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_quiz_question_keyboard(options, question_index):
    """Keyboard for quiz question options"""
    buttons = []
    
    for letter, option_text in options:
        buttons.append([
            InlineKeyboardButton(
                text=f"{letter}) {option_text}",
                callback_data=f"quiz_answer_{letter}_{question_index}"
            )
        ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_quiz_result_keyboard(quiz_id, language):
    """Keyboard for quiz results"""
    buttons = [
        [
            InlineKeyboardButton(text="📝 Javoblarni ko'rish", callback_data=f"quiz_review_{quiz_id}"),
            InlineKeyboardButton(text="🔄 Qayta yechish", callback_data=f"retake_quiz_{quiz_id}")
        ],
        [
            InlineKeyboardButton(text="📊 Statistikam", callback_data="quiz_stats")
        ],
        [
            InlineKeyboardButton(text="🔙 Testlar", callback_data=f"back_to_quizzes_{language}")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_premium_content_keyboard():
    """Premium content management keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📝 Topik 1", callback_data="admin_topik1"),
            InlineKeyboardButton(text="📝 Topik 2", callback_data="admin_topik2")
        ],
        [
            InlineKeyboardButton(text="🇯🇵 JLPT", callback_data="admin_jlpt")
        ],
        [
            InlineKeyboardButton(text="🔙 Admin panel", callback_data="admin_panel")
        ]
    ])

def get_section_admin_keyboard(section_type):
    """Section admin keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="➕ Kontent qo'shish", callback_data=f"add_content_{section_type}"),
            InlineKeyboardButton(text="📋 Kontent ko'rish", callback_data=f"view_content_{section_type}")
        ],
        [
            InlineKeyboardButton(text="🔙 Premium panel", callback_data="admin_premium_content")
        ]
    ])

def get_content_type_keyboard(section_type):
    """Content type selection keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📝 Matn", callback_data=f"content_text_{section_type}"),
            InlineKeyboardButton(text="🖼 Rasm", callback_data=f"content_photo_{section_type}")
        ],
        [
            InlineKeyboardButton(text="🎥 Video", callback_data=f"content_video_{section_type}"),
            InlineKeyboardButton(text="🎵 Audio", callback_data=f"content_audio_{section_type}")
        ],
        [
            InlineKeyboardButton(text="📎 Hujjat", callback_data=f"content_document_{section_type}"),
            InlineKeyboardButton(text="🎵 Musiqa", callback_data=f"content_music_{section_type}")
        ],
        [
            InlineKeyboardButton(text="🔙 Orqaga", callback_data=f"admin_{section_type}")
        ]
    ])

def get_premium_subsections_keyboard():
    """Premium subsection management sections"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📝 Topik 1 subsections", callback_data="subsection_topik1"),
            InlineKeyboardButton(text="📝 Topik 2 subsections", callback_data="subsection_topik2")
        ],
        [
            InlineKeyboardButton(text="🇯🇵 JLPT subsections", callback_data="subsection_jlpt")
        ],
        [
            InlineKeyboardButton(text="🔙 Admin panel", callback_data="admin_panel")
        ]
    ])

def get_subsection_admin_keyboard(section_type):
    """Subsection admin menu for a section"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="➕ Subsection qo'shish", callback_data=f"add_subsection_{section_type}")
        ],
        [
            InlineKeyboardButton(text="📋 Subsectionlar ro'yxati", callback_data=f"view_subsections_{section_type}")
        ],
        [
            InlineKeyboardButton(text="🔙 Premium subsections", callback_data="admin_premium_subsections")
        ]
    ])

def get_general_content_admin_keyboard():
    """General content management keyboard for admin"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🗣️ Gapirish", callback_data="admin_speaking"),
            InlineKeyboardButton(text="🎧 Audio lug'at", callback_data="admin_audio_dictionary")
        ],
        [
            InlineKeyboardButton(text="🗑️ Barcha kontentni o'chirish", callback_data="delete_all_general_content")
        ],
        [
            InlineKeyboardButton(text="🔙 Admin panel", callback_data="admin_panel")
        ]
    ])

def get_section_general_admin_keyboard(section_type):
    """General section admin keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="➕ Kontent qo'shish", callback_data=f"add_general_content_{section_type}"),
            InlineKeyboardButton(text="📋 Kontent ko'rish", callback_data=f"view_general_content_{section_type}")
        ],
        [
            InlineKeyboardButton(text="🗑️ Kontent o'chirish", callback_data=f"delete_general_content_{section_type}")
        ],
        [
            InlineKeyboardButton(text="🔙 Umumiy kontent", callback_data="admin_general_content")
        ]
    ])

def get_general_content_type_keyboard(section_type):
    """General content type selection keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📝 Matn", callback_data=f"general_content_text_{section_type}"),
            InlineKeyboardButton(text="🖼 Rasm", callback_data=f"general_content_photo_{section_type}")
        ],
        [
            InlineKeyboardButton(text="🎥 Video", callback_data=f"general_content_video_{section_type}"),
            InlineKeyboardButton(text="🎵 Audio", callback_data=f"general_content_audio_{section_type}")
        ],
        [
            InlineKeyboardButton(text="📎 Hujjat", callback_data=f"general_content_document_{section_type}"),
            InlineKeyboardButton(text="🎵 Musiqa", callback_data=f"general_content_music_{section_type}")
        ],
        [
            InlineKeyboardButton(text="🔙 Orqaga", callback_data=f"admin_{section_type}")
        ]
    ])
