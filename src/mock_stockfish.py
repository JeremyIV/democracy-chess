import pandas as pd
from typing import Optional
import chess

class MockStockfish:
    def __init__(self, csv_path: str = 'mock/stockfish.csv'):
        """Initialize with path to CSV file containing predetermined moves"""
        # Read the CSV file
        self.moves = pd.read_csv(csv_path)['move'].tolist()
        # Keep track of which move we're on
        self.current_move_index = 0
    
    def set_difficulty(self, difficulty: int):
        pass
    
    def play(self, board: chess.Board, limit: Optional[object] = None) -> 'MockResult':
        """
        Mock the stockfish play() method. Returns a MockResult object
        containing the next move from our CSV.
        
        Args:
            board: A chess.Board object (maintained for interface compatibility)
            limit: Ignored, maintained for interface compatibility
        """
        if self.current_move_index >= len(self.moves):
            raise RuntimeError("No more moves in mock Stockfish CSV!")
            
        # Get the next move from our list
        move_str = self.moves[self.current_move_index]
        # Convert string to chess.Move object
        move = chess.Move.from_uci(move_str)
        # Increment our position
        self.current_move_index += 1
        
        return MockResult(move)
    
    def reset(self):
        """Reset to start giving moves from the beginning again"""
        self.current_move_index = 0
        
    def quit(self):
        """Mock the quit method (does nothing but included for compatibility)"""
        pass

class MockResult:
    """Mock of the result object returned by stockfish's play() method"""
    def __init__(self, move: chess.Move):
        self.move = move