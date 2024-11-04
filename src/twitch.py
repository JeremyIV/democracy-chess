import time
from typing import List, Tuple
from twitchio.ext import commands
import asyncio
from queue import Queue
from threading import Thread

class TwitchChat:
    def __init__(self, channel_name: str, oauth_token: str):
        """
        Initialize real Twitch chat connection.
        
        Args:
            channel_name: Name of the Twitch channel to connect to (without the #)
            oauth_token: OAuth token for authentication (starts with 'oauth:')
        """
        self.channel_name = channel_name
        self.oauth_token = oauth_token
        self.message_queue = Queue()
        self.last_check = time.time()
        
        # Create and start the bot in a separate thread
        self.bot = TwitchBot(
            token=oauth_token,
            prefix='!',
            initial_channels=[f"#{channel_name}"],
            message_queue=self.message_queue
        )
        
        # Start bot in a separate thread
        self.bot_thread = Thread(target=self._run_bot)
        self.bot_thread.daemon = True  # Thread will close when main program exits
        self.bot_thread.start()

    def _run_bot(self):
        """Run the bot in a separate thread"""
        asyncio.run(self.bot.run())

    def get_chat(self) -> List[Tuple[str, str]]:
        """
        Get all chat messages that have happened since the last check.
        Returns a list of (username, comment) tuples.
        """
        current_time = time.time()
        messages = []
        
        # Get all messages from the queue
        while not self.message_queue.empty():
            messages.append(self.message_queue.get())
        
        self.last_check = current_time
        return messages

    def reset(self):
        """Reset the chat to start over"""
        # Clear the message queue
        while not self.message_queue.empty():
            self.message_queue.get()
        self.last_check = time.time()


class TwitchBot(commands.Bot):
    def __init__(self, message_queue: Queue, **kwargs):
        """Initialize the bot with a queue for storing messages"""
        super().__init__(**kwargs)
        self.message_queue = message_queue

    async def event_ready(self):
        """Called once when the bot goes online"""
        print(f"Bot is ready! Connected to {self.nick}")

    async def event_message(self, message):
        """Called whenever a message is received"""
        # Don't process messages from the bot itself
        if message.echo:
            return

        # Add message to queue as (username, content) tuple
        self.message_queue.put((message.author.name, message.content))


def create_twitch_chat(channel_name: str = None, oauth_token: str = None) -> TwitchChat:
    """
    Helper function to create a TwitchChat instance with credentials.
    If credentials aren't provided, attempts to read them from environment variables.
    """
    import os
    
    if channel_name is None:
        channel_name = os.getenv('TWITCH_CHANNEL')
        if not channel_name:
            raise ValueError("No channel name provided and TWITCH_CHANNEL environment variable not set")
    
    if oauth_token is None:
        oauth_token = os.getenv('TWITCH_OAUTH_TOKEN')
        if not oauth_token:
            raise ValueError("No OAuth token provided and TWITCH_OAUTH_TOKEN environment variable not set")
            
        # Add 'oauth:' prefix if not present
        if not oauth_token.startswith('oauth:'):
            oauth_token = f'oauth:{oauth_token}'
    
    return TwitchChat(channel_name, oauth_token)


# Example usage:
if __name__ == "__main__":
    import os
    
    # Example of testing the Twitch chat integration
    try:
        chat = create_twitch_chat()
        
        print("Starting chat monitoring... (Press Ctrl+C to stop)")
        
        while True:
            messages = chat.get_chat()
            if messages:
                print("\nNew messages:")
                for username, comment in messages:
                    print(f"{username}: {comment}")
            time.sleep(5)  # Check every 5 seconds
            
    except KeyboardInterrupt:
        print("\nStopping chat monitor...")