# stockfish_wrapper.py
from dataclasses import dataclass
from typing import Dict, Union
import chess
import chess.engine

@dataclass
class DifficultyLevel:
    name: str
    elo: int
    skill_level: int
    depth: int
    time: float

# Define difficulty levels with corresponding Stockfish parameters
DIFFICULTY_LEVELS: Dict[int, DifficultyLevel] = {
    1:  DifficultyLevel("Beginner",      200,  0,  1, 0.1),
    2:  DifficultyLevel("Novice",        400,  2,  1, 0.1),
    3:  DifficultyLevel("Casual",        600,  4,  2, 0.2),
    4:  DifficultyLevel("Amateur",       800,  6,  2, 0.2),
    5:  DifficultyLevel("Club Player",   1000, 8,  3, 0.3),
    6:  DifficultyLevel("Strong Club",   1200, 10, 3, 0.3),
    7:  DifficultyLevel("Expert",        1400, 12, 4, 0.4),
    8:  DifficultyLevel("Candidate Master", 1600, 14, 4, 0.4),
    9:  DifficultyLevel("FIDE Master",   1800, 16, 5, 0.5),
    10: DifficultyLevel("International Master", 2000, 18, 5, 0.5),
    11: DifficultyLevel("Grandmaster",   2200, 20, 6, 0.6),
    12: DifficultyLevel("Super GM",      2400, 20, 7, 0.7),
    13: DifficultyLevel("World Class",   2600, 20, 8, 0.8),
    14: DifficultyLevel("Superhuman",    2800, 20, 9, 0.9),
    15: DifficultyLevel("Maximum",       3000, 20, 10, 1.0),
}

class StockfishWrapper:
    """Wrapper for both real Stockfish and mock Stockfish that handles difficulty levels"""
    def __init__(self, engine: Union[chess.engine.SimpleEngine, 'MockStockfish'], difficulty: int):
        self.engine = engine
        self.set_difficulty(difficulty)

    def set_difficulty(self, difficulty: int):
        """Set the difficulty level of the engine"""
        if difficulty not in DIFFICULTY_LEVELS:
            raise ValueError(f"Invalid difficulty level. Must be between 1 and {len(DIFFICULTY_LEVELS)}")
        
        self.difficulty = DIFFICULTY_LEVELS[difficulty]
        
        # Only configure if it's a real Stockfish engine (not mock)
        if isinstance(self.engine, chess.engine.SimpleEngine):
            self.engine.configure({
                "Skill Level": self.difficulty.skill_level,
                "UCI_LimitStrength": True,
                "UCI_Elo": self.difficulty.elo
            })

    def play(self, board: chess.Board) -> chess.Move:
        """Play a move at the current difficulty level"""
        # For real Stockfish, use the difficulty-based time control
        if isinstance(self.engine, chess.engine.SimpleEngine):
            result = self.engine.play(
                board,
                chess.engine.Limit(
                    time=self.difficulty.time,
                    depth=self.difficulty.depth
                )
            )
        else:
            # For mock Stockfish, just pass through
            result = self.engine.play(board, None)
            
        return result.move

    def quit(self):
        """Clean up the engine"""
        self.engine.quit()

def create_engine(mock: bool = False, mock_path: str = None, difficulty: int = 5) -> StockfishWrapper:
    """Factory function to create a properly configured engine"""
    if mock:
        from mock_stockfish import MockStockfish
        raw_engine = MockStockfish(mock_path)
    else:
        raw_engine = chess.engine.SimpleEngine.popen_uci("/usr/games/stockfish")
    
    engine = StockfishWrapper(raw_engine, difficulty)
    print(f"Playing against Stockfish at {DIFFICULTY_LEVELS[difficulty].name} "
          f"level (ELO: {DIFFICULTY_LEVELS[difficulty].elo})")
    
    return engine