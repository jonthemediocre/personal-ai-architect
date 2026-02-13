#!/usr/bin/env python3
"""
Channel Adapters for Personal AI Architect
WebChat, Discord, and Telegram interfaces
"""

import asyncio
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum

class Channel(Enum):
    WEBCHAT = "webchat"
    DISCORD = "discord"
    TELEGRAM = "telegram"

@dataclass
class Message:
    id: str
    channel: Channel
    content: str
    sender: str
    timestamp: datetime
    metadata: Dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class ChannelAdapter(ABC):
    """Base class for channel adapters"""
    
    @abstractmethod
    async def send(self, message: str, target: str = None) -> bool:
        """Send a message to the channel"""
        pass
    
    @abstractmethod
    async def receive(self) -> List[Message]:
        """Receive messages from the channel"""
        pass
    
    @abstractmethod
    async def start_listening(self):
        """Start listening for incoming messages"""
        pass

class WebChatAdapter(ChannelAdapter):
    """WebChat adapter - current primary channel"""
    
    def __init__(self):
        self.message_queue: List[Message] = []
        self.listeners: List[callable] = []
        
    async def send(self, message: str, target: str = None) -> bool:
        """WebChat uses OpenClaw's message system"""
        # Messages are sent through the main session
        # This is a no-op for the adapter - OpenClaw handles it
        print(f"[WebChat] Would send: {message[:100]}...")
        return True
    
    async def receive(self) -> List[Message]:
        """Receive from local queue"""
        msgs = self.message_queue.copy()
        self.message_queue.clear()
        return msgs
    
    async def start_listening(self):
        """WebChat doesn't need separate listening"""
        pass
    
    def enqueue(self, message: Message):
        """Add message to queue for processing"""
        self.message_queue.append(message)

class DiscordAdapter(ChannelAdapter):
    """Discord bot adapter"""
    
    def __init__(self, token: str, guild_id: str = None):
        self.token = token
        self.guild_id = guild_id
        self.message_queue: List[Message] = []
        self.running = False
        
    async def send(self, message: str, channel_id: str = None) -> bool:
        """Send message to Discord channel"""
        # Would use discord.py library
        # For now, print the message
        print(f"[Discord] Sending to {channel_id or 'default'}: {message[:100]}...")
        return True
    
    async def receive(self) -> List[Message]:
        """Receive pending messages"""
        # Would poll Discord API
        return self.message_queue.copy()
    
    async def start_listening(self):
        """Start Discord bot"""
        self.running = True
        print("[Discord] Bot started (placeholder)")

class TelegramAdapter(ChannelAdapter):
    """Telegram bot adapter"""
    
    def __init__(self, bot_token: str):
        self.token = bot_token
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        self.message_queue: List[Message] = []
        
    async def send(self, message: str, chat_id: str = None) -> bool:
        """Send message to Telegram"""
        import requests
        
        if not chat_id:
            print("[Telegram] No chat_id specified")
            return False
            
        try:
            r = requests.post(
                f"{self.base_url}/sendMessage",
                json={"chat_id": chat_id, "text": message}
            )
            return r.status_code == 200
        except Exception as e:
            print(f"[Telegram] Send failed: {e}")
            return False
    
    async def receive(self) -> List[Message]:
        """Get updates from Telegram"""
        import:
            r = requests
        
        try requests.get(f"{self.base_url}/getUpdates")
            data = r.json()
            
            if data.get("ok"):
                updates = data.get("result", [])
                messages = []
                for update in updates:
                    msg = update.get("message", {})
                    messages.append(Message(
                        id=str(update.get("update_id")),
                        channel=Channel.TELEGRAM,
                        content=msg.get("text", ""),
                        sender=str(msg.get("from", {}).get("id", "unknown")),
                        timestamp=datetime.fromtimestamp(msg.get("date", 0))
                    ))
                return messages
        except Exception as e:
            print(f"[Telegram] Receive failed: {e}")
        return []
    
    async def start_listening(self):
        """Set webhook for Telegram"""
        print("[Telegram] Webhook mode (placeholder)")

class ChannelRouter:
    """Route messages between channels"""
    
    def __init__(self):
        self.channels: Dict[Channel, ChannelAdapter] = {}
        self.primary_channel = Channel.WEBCHAT
        
    def register(self, channel: Channel, adapter: ChannelAdapter):
        """Register a channel adapter"""
        self.channels[channel] = adapter
        
    async def send_all(self, message: str):
        """Send to all configured channels"""
        for channel, adapter in self.channels.items():
            if channel != self.primary_channel:
                await adapter.send(message)
                
    async def receive_all(self) -> List[Message]:
        """Receive from all channels"""
        all_messages = []
        for adapter in self.channels.values():
            msgs = await adapter.receive()
            all_messages.extend(msgs)
        return all_messages

class NotificationManager:
    """Manage notifications with priority and batching"""
    
    def __init__(self, router: ChannelRouter):
        self.router = router
        self.pending: List[Message] = []
        self.batch_size = 3
        self.batch_timeout = 5.0  # seconds
        
    async def notify(self, message: str, priority: str = "normal"):
        """Queue a notification"""
        self.pending.append(Message(
            id=f"notif_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
            channel=self.router.primary_channel,
            content=message,
            sender="system",
            timestamp=datetime.now(),
            metadata={"priority": priority}
        ))
        
        # Flush if batch full or timeout
        if len(self.pending) >= self.batch_size:
            await self.flush()
            
    async def flush(self):
        """Send all pending notifications"""
        if not self.pending:
            return
            
        message = f"📬 Notifications ({len(self.pending)}):\n"
        for msg in self.pending:
            message += f"- {msg.content}\n"
            
        await self.router.send_all(message)
        self.pending.clear()

if __name__ == "__main__":
    # Test adapters
    webchat = WebChatAdapter()
    discord = DiscordAdapter("PLACEHOLDER_TOKEN")
    telegram = TelegramAdapter("PLACEHOLDER_TOKEN")
    
    router = ChannelRouter()
    router.register(Channel.WEBCHAT, webchat)
    router.register(Channel.DISCORD, discord)
    router.register(Channel.TELEGRAM, telegram)
    
    print("Channels initialized:")
    print(f"  - WebChat: {type(webchat).__name__}")
    print(f"  - Discord: {type(discord).__name__}")
    print(f"  - Telegram: {type(telegram).__name__}")
