import aiosqlite
import asyncio
from datetime import datetime, timedelta
from typing import Optional, List, Tuple, Any
from config import DATABASE_PATH

async def init_db():
    """Initialize database with all required tables - RENDER DEPLOYMENT READY"""
    try:
        print(f"📊 Connecting to database: {DATABASE_PATH}")
        
        # Create database connection
        db = await aiosqlite.connect(DATABASE_PATH)
        print("🔧 Database connection established")
        
        try:
            # Enable foreign key support
            await db.execute("PRAGMA foreign_keys = ON")
            
            print("👥 Creating users table...")
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    is_premium BOOLEAN DEFAULT FALSE,
                    premium_expires_at TIMESTAMP,
                    referral_code TEXT UNIQUE,
                    referred_by INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    total_sessions INTEGER DEFAULT 0,
                    words_learned INTEGER DEFAULT 0,
                    quiz_score_total INTEGER DEFAULT 0,
                    quiz_attempts INTEGER DEFAULT 0,
                    rating_score REAL DEFAULT 0.0,
                    referral_count INTEGER DEFAULT 0
                )
            """)
            
            print("📁 Creating sections table...")
            await db.execute("""
                CREATE TABLE IF NOT EXISTS sections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    language TEXT,
                    is_premium BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_by INTEGER
                )
            """)
            
            print("📂 Creating subsections table...")
            await db.execute("""
                CREATE TABLE IF NOT EXISTS subsections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    section_id INTEGER,
                    name TEXT NOT NULL,
                    description TEXT,
                    is_premium BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (section_id) REFERENCES sections (id)
                )
            """)
            
            print("📝 Creating content table...")
            await db.execute("""
                CREATE TABLE IF NOT EXISTS content (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    section_id INTEGER DEFAULT 0,
                    subsection_id INTEGER DEFAULT 0,
                    title TEXT NOT NULL,
                    description TEXT,
                    content_type TEXT,
                    file_id TEXT,
                    file_path TEXT,
                    content_text TEXT,
                    is_premium BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (section_id) REFERENCES sections (id),
                    FOREIGN KEY (subsection_id) REFERENCES subsections (id)
                )
            """)
            
            print("🎯 Creating quizzes table...")
            await db.execute("""
                CREATE TABLE IF NOT EXISTS quizzes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    language TEXT,
                    category TEXT,
                    is_premium BOOLEAN DEFAULT FALSE,
                    created_by INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            print("❓ Creating questions table...")
            await db.execute("""
                CREATE TABLE IF NOT EXISTS questions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    quiz_id INTEGER,
                    question_text TEXT NOT NULL,
                    option_a TEXT NOT NULL,
                    option_b TEXT NOT NULL,
                    option_c TEXT NOT NULL,
                    option_d TEXT NOT NULL,
                    correct_answer TEXT NOT NULL,
                    explanation TEXT,
                    FOREIGN KEY (quiz_id) REFERENCES quizzes (id)
                )
            """)
            
            print("🏆 Creating quiz_attempts table...")
            await db.execute("""
                CREATE TABLE IF NOT EXISTS quiz_attempts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    quiz_id INTEGER,
                    score INTEGER,
                    total_questions INTEGER,
                    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id),
                    FOREIGN KEY (quiz_id) REFERENCES quizzes (id)
                )
            """)
            
            print("📊 Creating user_progress table...")
            await db.execute("""
                CREATE TABLE IF NOT EXISTS user_progress (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    content_id INTEGER,
                    completed BOOLEAN DEFAULT FALSE,
                    completed_at TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id),
                    FOREIGN KEY (content_id) REFERENCES content (id)
                )
            """)
            
            print("💎 Creating premium_content table...")
            await db.execute("""
                CREATE TABLE IF NOT EXISTS premium_content (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    section_type TEXT NOT NULL CHECK(section_type IN ('topik1', 'topik2', 'jlpt')),
                    title TEXT NOT NULL,
                    description TEXT,
                    file_id TEXT,
                    file_type TEXT CHECK(file_type IN ('photo', 'video', 'audio', 'document', 'music', 'text')),
                    content_text TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    order_index INTEGER DEFAULT 0
                )
            """)
            
            print("🔗 Creating referrals table...")
            await db.execute("""
                CREATE TABLE IF NOT EXISTS referrals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    referrer_id INTEGER,
                    referred_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (referrer_id) REFERENCES users (user_id),
                    FOREIGN KEY (referred_id) REFERENCES users (user_id)
                )
            """)
            
            # Commit all changes
            await db.commit()
            print("✅ All database tables created successfully!")
            
        finally:
            # Ensure database connection is closed
            await db.close()
            print("🔐 Database connection closed")
        
    except Exception as e:
        print(f"❌ Database initialization error: {e}")
        raise Exception(f"Failed to initialize database: {e}")

# Rest of the database functions (user management, etc.)
async def get_user(user_id: int) -> Optional[Tuple[Any, ...]]:
    """Get user by ID"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(
            "SELECT * FROM users WHERE user_id = ?", (user_id,)
        )
        return await cursor.fetchone()

async def create_user(user_id: int, username: Optional[str], first_name: str, last_name: Optional[str] = None, referred_by: Optional[int] = None) -> None:
    """Create new user"""
    import secrets
    referral_code = f"REF{secrets.randbelow(999999):06d}"
    
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            INSERT OR IGNORE INTO users 
            (user_id, username, first_name, last_name, referral_code, referred_by)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, username or "", first_name, last_name or "", referral_code, referred_by))
        await db.commit()

async def update_user_activity(user_id: int, activity_type: Optional[str] = None) -> None:
    """Update user's last activity and session count"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            UPDATE users 
            SET last_activity = CURRENT_TIMESTAMP,
                total_sessions = total_sessions + 1
            WHERE user_id = ?
        """, (user_id,))
        await db.commit()

async def is_premium_active(user_id: int) -> bool:
    """Check if user's premium is active"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("""
            SELECT is_premium, premium_expires_at FROM users WHERE user_id = ?
        """, (user_id,))
        result = await cursor.fetchone()
        
        if not result or not result[0]:
            return False
            
        if result[1] is None:
            return False
            
        try:
            expires_at = datetime.fromisoformat(result[1])
            return datetime.now() < expires_at
        except (ValueError, TypeError):
            return False

async def activate_premium(user_id: int, duration_days: int = 30) -> None:
    """Activate premium for user"""
    expires_at = datetime.now() + timedelta(days=duration_days)
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            UPDATE users 
            SET is_premium = TRUE, premium_expires_at = ?
            WHERE user_id = ?
        """, (expires_at.isoformat(), user_id))
        await db.commit()

# Essential functions for bot operation
async def get_sections(language: Optional[str] = None, is_premium: Optional[bool] = None) -> List[Any]:
    """Get sections, optionally filtered by language and premium status"""
    query = "SELECT * FROM sections WHERE 1=1"
    params = []
    
    if language:
        query += " AND language = ?"
        params.append(language)
    
    if is_premium is not None:
        query += " AND is_premium = ?"
        params.append(is_premium)
    
    query += " ORDER BY created_at"
    
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(query, params)
        rows = await cursor.fetchall()
        return [dict(row) for row in rows] if rows else []

async def create_section(name: str, description: str, language: str = "uzbek", is_premium: bool = False, created_by: Optional[int] = None) -> int:
    """Create a new section"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("""
            INSERT INTO sections (name, description, language, is_premium, created_by)
            VALUES (?, ?, ?, ?, ?)
        """, (name, description, language, is_premium, created_by))
        await db.commit()
        return cursor.lastrowid

async def add_content(section_id: int, subsection_id: int, title: str, description: str, 
                     content_type: str, file_id: Optional[str] = None, content_text: Optional[str] = None,
                     is_premium: bool = False) -> int:
    """Add content to section or subsection"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("""
            INSERT INTO content (section_id, subsection_id, title, description, content_type, file_id, content_text, is_premium)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (section_id, subsection_id, title, description, content_type, file_id, content_text, is_premium))
        await db.commit()
        return cursor.lastrowid

async def get_content_by_section(section_id: int) -> List[Any]:
    """Get all content for a section"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("""
            SELECT * FROM content WHERE section_id = ? ORDER BY created_at
        """, (section_id,))
        rows = await cursor.fetchall()
        return [dict(row) for row in rows] if rows else []

# MISSING FUNCTIONS ADDED FOR BOT FUNCTIONALITY

async def add_referral(referrer_id: int, referred_id: int) -> None:
    """Add a referral record"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            INSERT INTO referrals (referrer_id, referred_id)
            VALUES (?, ?)
        """, (referrer_id, referred_id))
        await db.commit()

async def get_user_referrals_count(user_id: int) -> int:
    """Get count of successful referrals for user"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(
            "SELECT COUNT(*) FROM referrals WHERE referrer_id = ?", (user_id,)
        )
        result = await cursor.fetchone()
        return result[0] if result else 0

async def get_user_by_referral_code(referral_code: str) -> Optional[Tuple[Any, ...]]:
    """Get user by referral code"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(
            "SELECT * FROM users WHERE referral_code = ?", (referral_code,)
        )
        return await cursor.fetchone()

async def update_referral_count(user_id: int) -> None:
    """Update referral count for user"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            UPDATE users 
            SET referral_count = referral_count + 1
            WHERE user_id = ?
        """, (user_id,))
        await db.commit()

async def reset_referral_count(user_id: int) -> None:
    """Reset referral count to 0"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            UPDATE users 
            SET referral_count = 0
            WHERE user_id = ?
        """, (user_id,))
        await db.commit()

async def revoke_premium(user_id: int) -> None:
    """Revoke premium access from user"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            UPDATE users 
            SET is_premium = FALSE, premium_expires_at = NULL
            WHERE user_id = ?
        """, (user_id,))
        await db.commit()

async def get_premium_users() -> List[Tuple[Any, ...]]:
    """Get all premium users"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("""
            SELECT user_id, first_name, username, premium_expires_at 
            FROM users 
            WHERE is_premium = TRUE
            ORDER BY premium_expires_at DESC
        """)
        return await cursor.fetchall()

async def get_all_users() -> List[Tuple[Any, ...]]:
    """Get all users"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("SELECT * FROM users ORDER BY created_at DESC")
        return await cursor.fetchall()

async def get_user_count() -> int:
    """Get total user count"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM users")
        result = await cursor.fetchone()
        return result[0] if result else 0

async def get_premium_user_count() -> int:
    """Get premium user count"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM users WHERE is_premium = TRUE")
        result = await cursor.fetchone()
        return result[0] if result else 0

async def get_section_count() -> int:
    """Get total section count"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM sections")
        result = await cursor.fetchone()
        return result[0] if result else 0

async def get_content_count() -> int:
    """Get total content count"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM content")
        result = await cursor.fetchone()
        return result[0] if result else 0

async def get_quiz_count() -> int:
    """Get total quiz count"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM quizzes")
        result = await cursor.fetchone()
        return result[0] if result else 0

async def update_user_rating(user_id: int, points: float) -> None:
    """Update user rating with points"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            UPDATE users 
            SET rating_score = rating_score + ?
            WHERE user_id = ?
        """, (points, user_id))
        await db.commit()

async def get_user_stats(user_id: int) -> Optional[Tuple[Any, ...]]:
    """Get user statistics"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("""
            SELECT user_id, first_name, total_sessions, words_learned, 
                   rating_score, referral_count, is_premium, premium_expires_at
            FROM users WHERE user_id = ?
        """, (user_id,))
        return await cursor.fetchone()

async def get_user_rating_details(user_id: int) -> dict:
    """Get detailed user rating information"""
    user_stats = await get_user_stats(user_id)
    if user_stats:
        return {
            'rating': user_stats[4] or 0.0,
            'sessions': user_stats[2] or 0,
            'words_learned': user_stats[3] or 0,
            'referrals': user_stats[5] or 0
        }
    return {'rating': 0.0, 'sessions': 0, 'words_learned': 0, 'referrals': 0}

async def get_subsections_by_section(section_id: int) -> List[Tuple[Any, ...]]:
    """Get all subsections for a section"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("""
            SELECT * FROM subsections WHERE section_id = ? ORDER BY created_at
        """, (section_id,))
        return await cursor.fetchall()

async def create_subsection(section_id: int, name: str, description: str, is_premium: bool = False) -> int:
    """Create a new subsection"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("""
            INSERT INTO subsections (section_id, name, description, is_premium)
            VALUES (?, ?, ?, ?)
        """, (section_id, name, description, is_premium))
        await db.commit()
        return cursor.lastrowid

async def delete_section(section_id: int) -> None:
    """Delete section and all related content"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        # Delete related content first
        await db.execute("DELETE FROM content WHERE section_id = ?", (section_id,))
        # Delete related subsections
        await db.execute("DELETE FROM subsections WHERE section_id = ?", (section_id,))
        # Delete section
        await db.execute("DELETE FROM sections WHERE id = ?", (section_id,))
        await db.commit()

async def get_section_by_id(section_id: int) -> Optional[Tuple[Any, ...]]:
    """Get section by ID"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("SELECT * FROM sections WHERE id = ?", (section_id,))
        return await cursor.fetchone()

async def create_quiz(title: str, description: str, language: str, category: str, is_premium: bool = False, created_by: Optional[int] = None) -> int:
    """Create a new quiz"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("""
            INSERT INTO quizzes (title, description, language, category, is_premium, created_by)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (title, description, language, category, is_premium, created_by))
        await db.commit()
        return cursor.lastrowid

async def add_question(quiz_id: int, question_text: str, option_a: str, option_b: str, 
                      option_c: str, option_d: str, correct_answer: str, explanation: str = "") -> int:
    """Add question to quiz"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("""
            INSERT INTO questions (quiz_id, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (quiz_id, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation))
        await db.commit()
        return cursor.lastrowid

async def get_quizzes(language: Optional[str] = None, category: Optional[str] = None) -> List[Tuple[Any, ...]]:
    """Get quizzes with optional filters"""
    query = "SELECT * FROM quizzes WHERE 1=1"
    params = []
    
    if language:
        query += " AND language = ?"
        params.append(language)
    
    if category:
        query += " AND category = ?"
        params.append(category)
    
    query += " ORDER BY created_at DESC"
    
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(query, params)
        return await cursor.fetchall()

async def get_questions_by_quiz(quiz_id: int) -> List[Tuple[Any, ...]]:
    """Get all questions for a quiz"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("""
            SELECT * FROM questions WHERE quiz_id = ? ORDER BY id
        """, (quiz_id,))
        return await cursor.fetchall()

async def record_quiz_attempt(user_id: int, quiz_id: int, score: int, total_questions: int) -> None:
    """Record a quiz attempt"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            INSERT INTO quiz_attempts (user_id, quiz_id, score, total_questions)
            VALUES (?, ?, ?, ?)
        """, (user_id, quiz_id, score, total_questions))
        
        # Update user stats
        await db.execute("""
            UPDATE users 
            SET quiz_score_total = quiz_score_total + ?, 
                quiz_attempts = quiz_attempts + 1
            WHERE user_id = ?
        """, (score, user_id))
        
        await db.commit()

async def get_leaderboard(limit: int = 10) -> List[Tuple[Any, ...]]:
    """Get top users by rating"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("""
            SELECT user_id, first_name, username, rating_score, words_learned, quiz_score_total
            FROM users 
            WHERE rating_score > 0
            ORDER BY rating_score DESC, words_learned DESC, quiz_score_total DESC
            LIMIT ?
        """, (limit,))
        return await cursor.fetchall()

# ALIAS FUNCTIONS FOR COMPATIBILITY
async def get_quiz_questions(quiz_id: int) -> List[Tuple[Any, ...]]:
    """Alias for get_questions_by_quiz for compatibility"""
    return await get_questions_by_quiz(quiz_id)

async def get_quiz_by_id(quiz_id: int) -> Optional[Tuple[Any, ...]]:
    """Get quiz by ID"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("SELECT * FROM quizzes WHERE id = ?", (quiz_id,))
        return await cursor.fetchone()

async def delete_quiz(quiz_id: int) -> None:
    """Delete quiz and all related questions"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        # Delete related questions first
        await db.execute("DELETE FROM questions WHERE quiz_id = ?", (quiz_id,))
        # Delete quiz
        await db.execute("DELETE FROM quizzes WHERE id = ?", (quiz_id,))
        await db.commit()

async def get_user_quizzes(user_id: int) -> List[Tuple[Any, ...]]:
    """Get quizzes created by user"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("""
            SELECT * FROM quizzes WHERE created_by = ? ORDER BY created_at DESC
        """, (user_id,))
        return await cursor.fetchall()

async def update_words_learned(user_id: int, count: int = 1) -> None:
    """Update words learned count for user"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            UPDATE users 
            SET words_learned = words_learned + ?
            WHERE user_id = ?
        """, (count, user_id))
        await db.commit()

async def get_content_by_subsection(subsection_id: int) -> List[Any]:
    """Get all content for a subsection"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("""
            SELECT * FROM content WHERE subsection_id = ? ORDER BY created_at
        """, (subsection_id,))
        rows = await cursor.fetchall()
        return [dict(row) for row in rows] if rows else []

async def get_subsection_by_id(subsection_id: int) -> Optional[Tuple[Any, ...]]:
    """Get subsection by ID"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("SELECT * FROM subsections WHERE id = ?", (subsection_id,))
        return await cursor.fetchone()

async def get_content_by_id(content_id: int) -> Optional[Tuple[Any, ...]]:
    """Get content by ID"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("SELECT * FROM content WHERE id = ?", (content_id,))
        return await cursor.fetchone()

async def delete_content(content_id: int) -> None:
    """Delete content by ID"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("DELETE FROM content WHERE id = ?", (content_id,))
        await db.commit()

async def delete_subsection(subsection_id: int) -> None:
    """Delete subsection and all related content"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        # Delete related content first
        await db.execute("DELETE FROM content WHERE subsection_id = ?", (subsection_id,))
        # Delete subsection
        await db.execute("DELETE FROM subsections WHERE id = ?", (subsection_id,))
        await db.commit()

# PREMIUM CONTENT FUNCTIONS
async def add_premium_content(section_type: str, title: str, description: str, 
                             file_id: Optional[str] = None, file_type: Optional[str] = None,
                             content_text: Optional[str] = None) -> int:
    """Add premium content"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("""
            INSERT INTO premium_content (section_type, title, description, file_id, file_type, content_text)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (section_type, title, description, file_id, file_type, content_text))
        await db.commit()
        return cursor.lastrowid

async def get_premium_content(section_type: Optional[str] = None) -> List[Tuple[Any, ...]]:
    """Get premium content by section type"""
    if section_type:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            cursor = await db.execute("""
                SELECT * FROM premium_content WHERE section_type = ? ORDER BY order_index, created_at
            """, (section_type,))
            return await cursor.fetchall()
    else:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            cursor = await db.execute("""
                SELECT * FROM premium_content ORDER BY section_type, order_index, created_at
            """)
            return await cursor.fetchall()

async def delete_premium_content(content_id: int) -> None:
    """Delete premium content by ID"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("DELETE FROM premium_content WHERE id = ?", (content_id,))
        await db.commit()

# BROADCAST AND STATISTICS FUNCTIONS
async def get_all_user_ids() -> List[int]:
    """Get all user IDs for broadcasting"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("SELECT user_id FROM users")
        results = await cursor.fetchall()
        return [row[0] for row in results]

async def get_admin_statistics() -> dict:
    """Get comprehensive admin statistics"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        stats = {}
        
        # User stats
        cursor = await db.execute("SELECT COUNT(*) FROM users")
        stats['total_users'] = (await cursor.fetchone())[0]
        
        cursor = await db.execute("SELECT COUNT(*) FROM users WHERE is_premium = TRUE")
        stats['premium_users'] = (await cursor.fetchone())[0]
        
        # Content stats
        cursor = await db.execute("SELECT COUNT(*) FROM sections")
        stats['total_sections'] = (await cursor.fetchone())[0]
        
        cursor = await db.execute("SELECT COUNT(*) FROM content")
        stats['total_content'] = (await cursor.fetchone())[0]
        
        cursor = await db.execute("SELECT COUNT(*) FROM quizzes")
        stats['total_quizzes'] = (await cursor.fetchone())[0]
        
        cursor = await db.execute("SELECT COUNT(*) FROM questions")
        stats['total_questions'] = (await cursor.fetchone())[0]
        
        # Activity stats
        cursor = await db.execute("SELECT COUNT(*) FROM quiz_attempts")
        stats['total_quiz_attempts'] = (await cursor.fetchone())[0]
        
        cursor = await db.execute("SELECT SUM(total_sessions) FROM users")
        result = await cursor.fetchone()
        stats['total_sessions'] = result[0] if result[0] else 0
        
        cursor = await db.execute("SELECT SUM(words_learned) FROM users")
        result = await cursor.fetchone()
        stats['total_words_learned'] = result[0] if result[0] else 0
        
        return stats