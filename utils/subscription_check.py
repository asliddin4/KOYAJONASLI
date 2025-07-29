from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from config import CHANNELS, INSTAGRAM_URL

async def check_subscriptions(user_id: int, bot: Bot) -> dict:
    """
    Check if user is subscribed to all required channels and Instagram
    Returns dict with subscription status
    """
    subscription_status = {
        'all_subscribed': True,
        'missing_channels': [],
        'instagram_followed': True  # We can't check Instagram automatically
    }
    
    # Check Telegram channel subscriptions
    for channel_username, channel_name in CHANNELS.items():
        try:
            member = await bot.get_chat_member(chat_id=channel_username, user_id=user_id)
            
            # Check if user is member, admin, or creator
            if member.status in ['left', 'kicked']:
                subscription_status['all_subscribed'] = False
                subscription_status['missing_channels'].append({
                    'username': channel_username,
                    'name': channel_name
                })
                
        except TelegramBadRequest:
            # Channel might not exist or bot is not admin
            subscription_status['all_subscribed'] = False
            subscription_status['missing_channels'].append({
                'username': channel_username,
                'name': channel_name
            })
        except Exception:
            # Other errors - assume not subscribed
            subscription_status['all_subscribed'] = False
            subscription_status['missing_channels'].append({
                'username': channel_username,
                'name': channel_name
            })
    
    return subscription_status

async def check_single_channel(user_id: int, bot: Bot, channel_username: str) -> bool:
    """Check if user is subscribed to a single channel"""
    try:
        member = await bot.get_chat_member(chat_id=channel_username, user_id=user_id)
        return member.status not in ['left', 'kicked']
    except:
        return False

def get_subscription_links():
    """Get list of subscription links for display"""
    links = []
    
    # Add Telegram channels
    for channel_username, channel_name in CHANNELS.items():
        links.append({
            'type': 'telegram',
            'url': f"https://t.me/{channel_username[1:]}",  # Remove @ symbol
            'name': channel_name,
            'username': channel_username
        })
    
    # Add Instagram
    links.append({
        'type': 'instagram',
        'url': INSTAGRAM_URL,
        'name': 'Instagram sahifamiz',
        'username': '@kores_tili_online'
    })
    
    return links
