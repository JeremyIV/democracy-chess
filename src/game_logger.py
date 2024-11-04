import os
import json
from datetime import datetime
from typing import List, Tuple, Literal
import chess

VotingMethod = Literal['fptp', 'approval', 'runoff']

class GameLogger:
    def __init__(self, log_dir: str, game_number: int, voting_method: VotingMethod, difficulty: int):
        """
        Initialize the game logger.
        
        Args:
            log_dir: Directory to store log files
            game_number: Sequential number of this game
            voting_method: The voting method being used
            difficulty: Stockfish difficulty level (1-15)
        """
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        
        # Generate unique filename using timestamp and game number
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = os.path.join(log_dir, f"game_{timestamp}_{game_number}.json")
        
        # Initialize game data
        self.game_data = {
            "game_number": game_number,
            "voting_method": voting_method,
            "stockfish_difficulty": difficulty,
            "moves": [],
            "turns": [],
            "start_time": datetime.now().isoformat(),
            "outcome": None
        }

    def log_turn(self, turn_number: int, chat_messages: List[Tuple[str, str]], 
                 twitch_move: str, stockfish_move: str):
        """
        Log a complete turn including chat messages and moves.
        
        Args:
            turn_number: The sequential number of this turn
            chat_messages: List of (username, message) tuples from chat
            twitch_move: The move chosen by Twitch chat (UCI format)
            stockfish_move: The move played by Stockfish (UCI format)
        """
        turn_data = {
            "turn_number": turn_number,
            "timestamp": datetime.now().isoformat(),
            "chat_messages": [
                {"username": username, "message": message} 
                for username, message in chat_messages
            ],
            "twitch_move": twitch_move,
            "stockfish_move": stockfish_move
        }
        self.game_data["turns"].append(turn_data)
        self.game_data["moves"].extend([twitch_move, stockfish_move])
        
        # Save after each turn in case of crash
        self._save_log()

    def log_outcome(self, outcome: chess.Outcome):
        """
        Log the game outcome.
        
        Args:
            outcome: A chess.Outcome object containing the game result
        """
        self.game_data["outcome"] = {
            "winner": "Twitch" if outcome.winner else "Stockfish" if outcome.winner is False else "Draw",
            "termination": outcome.termination.name,
            "end_time": datetime.now().isoformat()
        }
        self._save_log()

    def _save_log(self):
        """Save the current game data to file"""
        with open(self.log_file, 'w') as f:
            json.dump(self.game_data, f, indent=2)