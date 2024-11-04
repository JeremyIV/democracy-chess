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
    
    # Add new fields for low-rated configurations
    hash_size: int = 64
    move_overhead: int = 30
    slow_mover: int = 100  # Default is 100
    use_elo_limit: bool = True

# Define difficulty levels with corresponding Stockfish parameters
DIFFICULTY_LEVELS: Dict[int, DifficultyLevel] = {
    # Very weak levels (don't use UCI_Elo)
    1: DifficultyLevel(
        "Beginner", 200, 0, 1, 0.1,
        hash_size=1, move_overhead=1000, slow_mover=10,
        use_elo_limit=False
    ),
    2: DifficultyLevel(
        "Novice", 400, 2, 1, 0.1,
        hash_size=1, move_overhead=800, slow_mover=20,
        use_elo_limit=False
    ),
    3: DifficultyLevel(
        "Casual", 600, 3, 2, 0.2,
        hash_size=2, move_overhead=600, slow_mover=30,
        use_elo_limit=False
    ),
    4: DifficultyLevel(
        "Amateur", 800, 4, 2, 0.2,
        hash_size=4, move_overhead=400, slow_mover=50,
        use_elo_limit=False
    ),
    5: DifficultyLevel(
        "Club Player", 1000, 5, 3, 0.3,
        hash_size=8, move_overhead=200, slow_mover=70,
        use_elo_limit=False
    ),
    6: DifficultyLevel(
        "Strong Club", 1200, 6, 3, 0.3,
        hash_size=16, move_overhead=100, slow_mover=85,
        use_elo_limit=False
    ),
    # Standard levels (use UCI_Elo)
    7:  DifficultyLevel("Expert", 1400, 12, 4, 0.4),
    8:  DifficultyLevel("Candidate Master", 1600, 14, 4, 0.4),
    9:  DifficultyLevel("FIDE Master", 1800, 16, 5, 0.5),
    10: DifficultyLevel("International Master", 2000, 18, 5, 0.5),
    11: DifficultyLevel("Grandmaster", 2200, 20, 6, 0.6),
    12: DifficultyLevel("Super GM", 2400, 20, 7, 0.7),
    13: DifficultyLevel("World Class", 2600, 20, 8, 0.8),
    14: DifficultyLevel("Superhuman", 2800, 20, 9, 0.9),
    15: DifficultyLevel("Maximum", 3000, 20, 10, 1.0),
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
            config = {
                "Skill Level": self.difficulty.skill_level,
                "Threads": 1,  # Single thread for consistency
                "Hash": self.difficulty.hash_size,
                "Move Overhead": self.difficulty.move_overhead,
                "Slow Mover": self.difficulty.slow_mover,
            }
            
            if self.difficulty.use_elo_limit:
                # Higher-rated configurations use UCI_Elo
                config.update({
                    "UCI_LimitStrength": True,
                    "UCI_Elo": self.difficulty.elo
                })
            else:
                # Lower-rated configurations don't use UCI_Elo
                config["UCI_LimitStrength"] = False
            
            self.engine.configure(config)

    def play(self, board: chess.Board) -> chess.Move:
        """Play a move at the current difficulty level"""
        # For real Stockfish, use the difficulty-based time control
        if isinstance(self.engine, chess.engine.SimpleEngine):
            limit_args = {
                "time": self.difficulty.time,
                "depth": self.difficulty.depth
            }
            
            # For very low difficulties, add some randomness by using nodes limit
            if not self.difficulty.use_elo_limit:
                # Limit nodes for lower difficulties to prevent deep calculation
                max_nodes = 1000 * (self.difficulty.skill_level + 1)
                limit_args["nodes"] = max_nodes
            
            result = self.engine.play(board, chess.engine.Limit(**limit_args))
        else:
            # For mock Stockfish, just pass through
            result = self.engine.play(board, None)
            
        return result.move

    def quit(self):
        """Clean up the engine"""
        if hasattr(self.engine, 'quit'):
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