# Welcome and basic messages
WELCOME_MESSAGE = """
🎉 <b>Xush kelibsiz, {first_name}!</b>

🇰🇷🇯🇵 Koreys va Yapon tillarini o'rganish botiga xush kelibsiz!

<b>Bu botda siz:</b>
• 📚 Koreys va Yapon tillarini o'rganasiz
• 🧠 Testlar yechasiz va bilimingizni tekshirasiz
• 📊 O'sish jarayoningizni kuzatasiz
• 🏆 Reytingda raqobatlashasiz
• 💎 Premium kontentlardan foydalanasiz

<b>Boshlash uchun tugmalardan birini tanlang:</b>
"""

SUBSCRIPTION_REQUIRED_MESSAGE = """
⚠️ <b>Obuna bo'lish majburiy!</b>

Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling:

{missing_channels}

📷 <b>Instagram:</b> @kores_tili_online

Barcha kanallarga obuna bo'lgach, "✅ Obunani tekshirish" tugmasini bosing.
"""

ADMIN_WELCOME_MESSAGE = """
⚙️ <b>Admin Panel</b>

Salom admin! Quyidagi amallarni bajarishingiz mumkin:

📚 <b>Bo'limlar:</b> Yangi bo'lim va pastki bo'limlar yaratish
📁 <b>Kontent:</b> Video, audio, rasm, PDF fayllar yuklash
🧠 <b>Testlar:</b> Savol-javob testlari yaratish
📊 <b>Statistika:</b> Foydalanuvchilar va bot statistikasi

Nima qilmoqchisiz?
"""

# Premium related messages
PREMIUM_INFO_MESSAGE = """
💎 <b>Premium obuna</b>

<b>Joriy status:</b> {premium_status}

<b>Premium olish yo'llari:</b>

💰 <b>To'lov orqali:</b>
• Narx: {price:,} so'm/oy
• KAPITALBANK/VISA: 4278 3100 2775 4068
• Egasi: HOSHIMJON MAMADIYEV
• Barcha premium kontentlarga kirish

👥 <b>Referral orqali:</b>
• {referral_threshold} ta do'stni taklif qiling
• 1 oy bepul premium oling
• Joriy referrallar: {current_referrals}/{referral_threshold}
• Kerakli referrallar: {remaining_referrals}

<b>Premium imkoniyatlari:</b>
• Barcha premium bo'limlarga kirish
• Maxsus darslik va materiallar
• Premium testlar
• Reklama yo'q
• Batafsil statistika
"""

REFERRAL_MESSAGE = """
👥 <b>Do'stlaringizni taklif qiling!</b>

<b>Sizning referral linkingiz:</b>
<code>https://t.me/{bot_username}?start={referral_code}</code>

<b>Qanday ishlaydi:</b>
1️⃣ Yuqoridagi linkni do'stlaringizga yuboring
2️⃣ Ular shu linkni bosib botga kirishsin
3️⃣ {remaining_referrals} ta referral to'plang
4️⃣ 1 oy bepul premium oling!

<b>Joriy holat:</b>
✅ Tayyor referrallar: {current_referrals}
⏳ Kerakli referrallar: {remaining_referrals}

<b>Do'stlaringizga yuboring:</b>
"Koreys va Yapon tilini o'rganish uchun bu linkni bosing: https://t.me/{bot_username}?start={referral_code}

Bu orqali kirsangiz, biz ikkalamiz ham premium olishimiz mumkin! 🎁"
"""

# Motivational messages for weekly scheduler
MOTIVATIONAL_MESSAGES = [
    """
🌟 <b>Haftalik motivatsiya!</b>

Salom {name}! 

Til o'rganish - bu har kuni bir qadam tashlaydigan sayohat. Siz ajoyib ish qilyapsiz! 

📚 Bugun yangi so'zlar o'rganing
🧠 Test yechishni unutmang  
🎯 Maqsadlaringizga qarab yuring!

Davom eting! 💪
    """,
    
    """
🎯 <b>Muvaffaqiyat yaqin!</b>

{name}, siz to'g'ri yo'ldasiz!

🇰🇷🇯🇵 Har bir o'rganilgan so'z sizni maqsadingizga yaqinlashtiradi. 

Bugun nima o'rganasiz?
• Yangi grammatika
• Qiziqarli audio darslar  
• Testlar orqali bilimni mustahkamlash

Keling, birga o'rganaylik! 🚀
    """,
    
    """
💡 <b>Bilim - kuch!</b>

{name}, sizning sa'y-harakatingiz meva bermoqda!

📈 Reytingingiz o'sib bormoqda
🏆 Yuqori o'rinlarga yaqinlashyapsiz
💪 Har kun yangi bilim egasiga aylanmoqdasiz

Davom eting, muvaffaqiyat sizniki! ✨
    """,
    
    """
🌈 <b>Yangi hafta, yangi imkoniyatlar!</b>

{name}, til o'rganish - bu hayotni o'zgartiruvchi tajriba!

🎨 Yangi madaniyatlar bilan tanishing
🤝 Yangi do'stlar toping
🌍 Dunyoni yangi ko'z bilan ko'ring

Bugun qaysi darsdan boshlaysiz? 📚
    """
]

# Premium promotion messages for scheduler
PREMIUM_PROMOTION_MESSAGES = [
    """
💎 <b>Premium taklifimiz!</b>

{name}, sizning faoliyatingiz ajoyib!

Premium obuna bilan:
✨ Barcha kontentlarga kirish
🎯 Maxsus testlar va materiallar
📊 Batafsil tahlil va statistika

💰 Faqat {price:,} so'm/oy
👥 Yoki 10 ta do'st taklif qiling!

/premium - batafsil ma'lumot
    """,
    
    """
🚀 <b>O'sishingizni tezlashtiring!</b>

{name}, Premium bilan ko'proq o'rganing!

🌟 Maxsus video darslar
🧠 Premium testlar  
📈 Shaxsiy o'rganish rejasi
🎯 Tezkor natijalar

Bugun Premium oling va farqni his eting! 💪

/premium
    """,
    
    """
🎉 <b>Maxsus taklif!</b>

{name}, siz top foydalanuvchilardan birisiz!

Premium obuna sizga:
• Barcha premium bo'limlarni ochadi
• Maxsus materiallar beradi  
• Reyting tizimida ustunlik
• Reklama yo'q tajriba

Do'stlaringizni taklif qiling yoki to'lov qiling! 💎

/premium
    """
]

# Error messages
ERROR_MESSAGES = {
    'not_subscribed': "❌ Barcha kanallarga obuna bo'lmadingiz!",
    'premium_required': "💎 Bu premium kontent! Premium obuna oling.",
    'quiz_not_found': "❌ Test topilmadi!",
    'content_not_found': "❌ Kontent topilmadi!",
    'admin_only': "❌ Bu funksiya faqat admin uchun!",
    'file_too_large': "❌ Fayl hajmi juda katta!",
    'invalid_format': "❌ Noto'g'ri format!",
    'database_error': "❌ Ma'lumotlar bazasida xatolik yuz berdi.",
    'network_error': "❌ Tarmoq xatoligi. Qaytadan urinib ko'ring.",
    'permission_denied': "❌ Ruxsat rad etildi.",
    'rate_limit': "❌ Juda ko'p so'rov. Biroz kuting.",
}

# Success messages  
SUCCESS_MESSAGES = {
    'section_created': "✅ Bo'lim muvaffaqiyatli yaratildi!",
    'content_uploaded': "✅ Kontent muvaffaqiyatli yuklandi!",
    'quiz_created': "✅ Test muvaffaqiyatli yaratildi!",
    'premium_activated': "🎉 Premium obuna faollashtirildi!",
    'payment_received': "✅ To'lov qabul qilindi!",
    'quiz_completed': "🎯 Test muvaffaqiyatli yakunlandi!",
    'progress_saved': "💾 Jarayon saqlandi!",
    'referral_added': "👥 Referral qo'shildi!",
}

# Help and info messages
HELP_TEXT = """
🤖 <b>Yordam bo'limi</b>

<b>Asosiy buyruqlar:</b>
/start - Botni qayta ishga tushirish
/help - Yordam ma'lumotlari
/profile - Shaxsiy profil
/premium - Premium obuna haqida

<b>Botdan foydalanish:</b>
1. Barcha kanallarga obuna bo'ling
2. Tilni tanlang (Koreys/Yapon)
3. Bo'limlarni o'rganing
4. Testlar yeching
5. Reytingda o'rningizni ko'ring

<b>Premium imkoniyatlari:</b>
• Barcha premium kontentlar
• Maxsus testlar
• Batafsil statistika
• Reklama yo'q

<b>Muammolar bo'lsa:</b>
Admin: @chang_chi_won
"""

ABOUT_TEXT = """
🇰🇷🇯🇵 <b>Koreys va Yapon tili o'rganish boti</b>

<b>Nima taqdim etamiz:</b>
• Boshlang'ich dan ilg'or darajagacha darslar
• Interaktiv testlar va mashqlar
• Audio va video materiallar
• Grammatika va lug'at
• Madaniy ma'lumotlar

<b>Bizning afzalliklarimiz:</b>
✅ Tizimli o'rgatish metodikasi
✅ Havsala afzoylik tizimi
✅ Premium kontentlar
✅ Doimiy yangilanishlar

<b>Statistika:</b>
🎯 1000+ faol o'quvchi
📚 500+ dars materiallari
🧠 200+ test savollari

Admin: @chang_chi_won
Kanallarimiz: @koreys_quiz, @korestili_teknkurs
"""

# Quiz related messages
QUIZ_START_MESSAGE = """
🧠 <b>Test boshlandi!</b>

<b>Qoidalar:</b>
• Har bir savol uchun bir necha variant beriladi
• To'g'ri javobni tanlang
• Vaqt chekovi yo'q
• Xato qilsangiz ham davom eting

Omad tilaymiz! 🍀
"""

QUIZ_RESULT_EXCELLENT = """
🏆 <b>A'lo natija!</b>

Siz ajoyib natija ko'rsatdingiz! Bilimingiz yuqori darajada.

Keyingi qadamlar:
• Yangi testlarni yeching
• Qiyinroq bo'limlarni o'rganing  
• Premium kontentlarni ko'ring

Davom eting! 🌟
"""

QUIZ_RESULT_GOOD = """
🥇 <b>Yaxshi natija!</b>

Yaxshi ish qildingiz! Bir necha joyni takrorlash kerak.

Tavsiyalar:
• Xato qilgan savollarni qayta ko'ring
• Shu mavzudagi materiallarni takrorlang
• Ko'proq mashq qiling

Siz qila olasiz! 💪
"""

QUIZ_RESULT_POOR = """
📚 <b>Takrorlash kerak!</b>

Xafa bo'lmang! Har kim xato qiladi.

Nima qilish kerak:
• Dars materiallarini qayta o'qing
• Video darslarni tomosha qiling
• Audio materiallarni tinglang
• Qaytadan test yeching

Sabr va mehnat bilan hammasi bo'ladi! 🎯
"""

# Notification messages
DAILY_REMINDER = """
⏰ <b>Kunlik eslatma!</b>

{name}, bugun til o'rganish vaqti!

📅 Bugungi rejangiz:
• 10-15 daqiqa yangi so'zlar
• 1-2 ta test yeching
• Audio/video material tinglang

Kichik qadamlar katta muvaffaqiyatga olib boradi! 🚶‍♂️➡️🏆
"""

ACHIEVEMENT_UNLOCKED = """
🏅 <b>Yangi muvaffaqiyat!</b>

{name}, siz yangi achievement oldingiz:

🎯 <b>{achievement_name}</b>
📝 {achievement_description}
⭐ +{points} reyting ball

Davom eting va yangi yutuqlarga erishing! 🚀
"""

# Admin notification messages
ADMIN_NEW_USER = """
👤 <b>Yangi foydalanuvchi!</b>

Foydalanuvchi: {name}
ID: {user_id}
Username: @{username}
Referral: {referrer}
Vaqt: {join_time}
"""

ADMIN_PAYMENT_NOTIFICATION = """
💳 <b>Yangi to'lov!</b>

Foydalanuvchi: {name} ({user_id})
Summa: {amount} so'm
To'lov turi: {payment_type}
Vaqt: {payment_time}

Tasdiqlash uchun: /activate_premium {user_id}
"""

ADMIN_QUIZ_COMPLETED = """
🧠 <b>Test yakunlandi!</b>

Foydalanuvchi: {name}
Test: {quiz_title}
Natija: {score}/{max_score} ({percentage}%)
Vaqt: {completion_time}
"""

# Special occasion messages
WELCOME_BACK = """
🎉 <b>Xush kelibsiz!</b>

{name}, sizni qayta ko'rganimizdan xursandmiz!

Sizning so'nggi faoliyatingizdan keyin:
• {new_content} ta yangi kontent qo'shildi
• {new_quizzes} ta yangi test yaratildi
• Reytingingiz: {rating} ball

Yangiliklar bilan tanishib, o'rganishni davom eting! 📚
"""

MILESTONE_REACHED = """
🎊 <b>Muhim chegara!</b>

{name}, tabriklaymiz!

Siz {milestone} ga erishdingiz:
• Jami o'rganilgan so'zlar: {words}
• Yechilgan testlar: {quizzes}  
• Umumiy reyting: {rating}

Bu katta muvaffaqiyat! Davom eting! 🏆
"""

WEEKLY_SUMMARY = """
📊 <b>Haftalik xulosа!</b>

{name}, bu hafta sizning natijalaringiz:

📚 O'rganilgan kontentlar: {content_count}
🧠 Yechilgan testlar: {quiz_count}
⭐ Oshgan reyting: +{rating_increase}
🏆 Joriy o'rin: {rank}

Keyingi hafta uchun maqsad qo'ying! 🎯
"""
