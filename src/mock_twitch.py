import pandas as pd
import time
from typing import List, Tuple

class MockTwitchChat:
    def __init__(self, csv_path: str):
        """Initialize with path to CSV file containing mock chat data"""
        # Read the CSV file
        self.chat_data = pd.read_csv(csv_path)
        # Sort by time to ensure chronological order
        self.chat_data = self.chat_data.sort_values('time')
        # When the game/mock chat starts
        self.start_time = time.time()
        # When we last checked for messages
        self.last_check = self.start_time

    def get_chat(self) -> List[Tuple[str, str]]:
        """
        Get all chat messages that have happened since the last check.
        Returns a list of (username, comment) tuples.
        """
        current_time = time.time()
        # How many seconds into the game are we?
        seconds_since_start = current_time - self.start_time
        # What was the last time we checked?
        seconds_at_last_check = self.last_check - self.start_time
        
        # Get messages that occurred between last check and now
        # based on the timestamps in the CSV
        new_messages = self.chat_data[
            (self.chat_data['time'] > seconds_at_last_check) & 
            (self.chat_data['time'] <= seconds_since_start)
        ]
        
        # Update last check time
        self.last_check = current_time
        
        # Return list of (username, comment) tuples
        return list(zip(new_messages['username'], new_messages['comment']))

    def reset(self):
        """Reset the chat to start over"""
        self.start_time = time.time()
        self.last_check = self.start_time


# Example usage:
if __name__ == "__main__":
    # Test the implementation
    chat = MockTwitchChat('twitch_chat.csv')
    
    print("Starting chat simulation...")
    
    # Simulate checking chat every 10 seconds
    for _ in range(6):  # Will cover first minute
        messages = chat.get_chat()
        if messages:
            print("\nNew messages:")
            for username, comment in messages:
                print(f"{username}: {comment}")
        else:
            print("\nNo new messages")
        time.sleep(10)  # Wait 10 seconds before next check