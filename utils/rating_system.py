import aiosqlite
from datetime import datetime, timedelta
from config import DATABASE_PATH

# Rating points for different activities
RATING_POINTS = {
    'session_start': 1.0,
    'content_access': 2.0,
    'content_view': 3.0,
    'content_complete': 5.0,
    'quiz_start': 3.0,
    'quiz_complete': 5.0,
    'quiz_good': 8.0,      # 60-80% score
    'quiz_excellent': 12.0, # 80%+ score
    'daily_login': 2.0,
    'weekly_active': 10.0,
    'referral_success': 15.0,
    'premium_subscribe': 20.0,
    'conversation_ai': 1.5,  # AI suhbat
    'grammar_ai': 2.0        # Grammar AI
}

async def update_user_rating(user_id: int, activity_type: str, bonus_points: float = 0):
    """Update user's rating based on activity"""
    base_points = RATING_POINTS.get(activity_type, 0)
    total_points = base_points + bonus_points
    
    if total_points <= 0:
        return
    
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            # Update rating score
            await db.execute("""
                UPDATE users 
                SET rating_score = rating_score + ?,
                    last_activity = CURRENT_TIMESTAMP
                WHERE user_id = ?
            """, (total_points, user_id))
            
            # Update words learned for content activities
            if activity_type in ['content_complete', 'quiz_excellent']:
                words_bonus = 1 if activity_type == 'content_complete' else 2
                await db.execute("""
                    UPDATE users 
                    SET words_learned = words_learned + ?
                    WHERE user_id = ?
                """, (words_bonus, user_id))
            
            await db.commit()
    except Exception as e:
        print(f"Rating update error: {e}")

async def get_user_rating_details(user_id: int):
    """Get detailed user rating information"""
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            # Get user data with all columns by position
            cursor = await db.execute("""
                SELECT * FROM users WHERE user_id = ?
            """, (user_id,))
            user = await cursor.fetchone()
            
            if not user:
                return None
            
            # Extract data based on correct database positions
            first_name = user[2] if len(user) > 2 else 'Anonim'  # [2] first_name
            rating_score = user[14] if len(user) > 14 and user[14] is not None else 0.0  # [14] rating_score
            words_learned = user[11] if len(user) > 11 and user[11] is not None else 0  # [11] words_learned 
            quiz_score_total = user[12] if len(user) > 12 and user[12] is not None else 0  # [12] quiz_score_total
            quiz_attempts = user[13] if len(user) > 13 and user[13] is not None else 0  # [13] quiz_attempts
            total_sessions = user[10] if len(user) > 10 and user[10] is not None else 0  # [10] total_sessions
            created_at = user[8] if len(user) > 8 else None  # [8] created_at
            
            # Calculate level (every 50 points = 1 level)
            level = min(100, max(1, int(rating_score / 50) + 1))
            
            # Get ranking
            cursor = await db.execute("""
                SELECT COUNT(*) + 1 as ranking
                FROM users 
                WHERE rating_score > ? AND rating_score > 0
            """, (rating_score,))
            ranking_result = await cursor.fetchone()
            ranking = ranking_result[0] if ranking_result else 1
            
            return {
                'first_name': first_name or 'Anonim',
                'rating_score': rating_score,
                'words_learned': words_learned,
                'quiz_score_total': quiz_score_total,
                'quiz_attempts': quiz_attempts,
                'total_sessions': total_sessions,
                'level': level,
                'ranking': ranking,
                'created_at': created_at
            }
    except Exception as e:
        print(f"Get user rating details error: {e}")
        return None

async def calculate_weekly_bonus():
    """Calculate and award weekly activity bonuses"""
    one_week_ago = datetime.now() - timedelta(days=7)
    
    async with aiosqlite.connect(DATABASE_PATH) as db:
        # Get users who were active this week
        cursor = await db.execute("""
            SELECT user_id, COUNT(*) as activity_count
            FROM (
                SELECT user_id FROM user_progress 
                WHERE completed_at > ?
                UNION ALL
                SELECT user_id FROM quiz_attempts 
                WHERE completed_at > ?
            ) as activities
            GROUP BY user_id
            HAVING activity_count >= 5  -- At least 5 activities this week
        """, (one_week_ago.isoformat(), one_week_ago.isoformat()))
        
        active_users = await cursor.fetchall()
        
        # Award weekly bonus
        for user_id, activity_count in active_users:
            await update_user_rating(user_id, 'weekly_active', 0)

async def get_user_rating_details(user_id: int):
    """Get detailed rating information for user"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("""
            SELECT rating_score, words_learned, quiz_score_total, 
                   quiz_attempts, total_sessions, last_activity
            FROM users 
            WHERE user_id = ?
        """, (user_id,))
        user_data = await cursor.fetchone()
        
        if not user_data:
            return None
        
        # Get user's ranking
        cursor = await db.execute("""
            SELECT COUNT(*) + 1 as ranking
            FROM users 
            WHERE rating_score > ? AND rating_score > 0
        """, (user_data[0],))
        ranking = (await cursor.fetchone())[0]
        
        # Calculate level based on rating
        rating_score = user_data[0]
        level = min(100, max(1, int(rating_score // 50) + 1))
        
        return {
            'rating_score': rating_score,
            'words_learned': user_data[1],
            'quiz_score_total': user_data[2],
            'quiz_attempts': user_data[3],
            'total_sessions': user_data[4],
            'last_activity': user_data[5],
            'ranking': ranking,
            'level': level
        }

async def get_rating_leaderboard(limit: int = 10, language: str = None):
    """Get top users by rating, optionally filtered by language preference"""
    query = """
        SELECT u.user_id, u.first_name, u.username, u.rating_score, 
               u.words_learned, u.quiz_score_total, u.last_activity
        FROM users u
        WHERE u.rating_score > 0
    """
    params = []
    
    if language:
        # This would require tracking user's preferred language
        # For now, we'll just get all users
        pass
    
    query += " ORDER BY u.rating_score DESC LIMIT ?"
    params.append(limit)
    
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(query, params)
        return await cursor.fetchall()