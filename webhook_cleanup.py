#!/usr/bin/env python3
"""
Webhook cleanup script for Telegram bot
Run this to remove any existing webhooks before deploying with polling
"""

import asyncio
import aiohttp
import os

BOT_TOKEN = os.getenv('BOT_TOKEN')

async def cleanup_webhook():
    """Remove webhook to enable polling"""
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN not found in environment")
        return
        
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook"
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url) as response:
                data = await response.json()
                if data.get('ok'):
                    print("✅ Webhook deleted successfully")
                    print("✅ Bot can now use polling without conflicts")
                else:
                    print(f"❌ Failed to delete webhook: {data}")
        except Exception as e:
            print(f"❌ Error: {e}")

    # Also check webhook info
    info_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getWebhookInfo"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(info_url) as response:
                data = await response.json()
                if data.get('ok'):
                    webhook_info = data.get('result', {})
                    webhook_url = webhook_info.get('url', '')
                    
                    if webhook_url:
                        print(f"⚠️  Webhook still active: {webhook_url}")
                    else:
                        print("✅ No webhook set - polling ready")
                        
                    print(f"📊 Pending updates: {webhook_info.get('pending_update_count', 0)}")
                else:
                    print(f"❌ Failed to get webhook info: {data}")
        except Exception as e:
            print(f"❌ Error getting webhook info: {e}")

if __name__ == "__main__":
    asyncio.run(cleanup_webhook())