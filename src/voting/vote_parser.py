from abc import ABC, abstractmethod
from typing import List, Dict, Tuple, TypeVar, Iterable
import chess

# Generic type for whatever data structure the subclass uses to represent a vote
V = TypeVar('V')

class VoteParser(ABC):
    def __init__(self, board: chess.Board):
        """
        Initialize the vote parser with a chess board.
        
        Args:
            board: The current chess board state, used to validate moves
        """
        self.board = board

    @abstractmethod
    def parse_single_vote(self, comment: str) -> V:
        """
        Parse a single comment into a vote.
        
        Args:
            comment: A string containing a user's comment/vote
            
        Returns:
            The parsed vote in whatever format the specific voting system uses.
            For example, FPTP might return a single move, while approval voting
            might return a set of moves.
            
        Raises:
            ValueError: If the comment cannot be parsed into a valid vote
        """
        pass

    def parse_all_votes(self, comments: List[Tuple[str, str]]) -> Dict[str, V]:
        """
        Parse all comments into a dictionary of votes, keeping only the latest
        vote from each user.
        
        Args:
            comments: List of (username, comment) tuples
            
        Returns:
            Dictionary mapping usernames to their final parsed votes
        """
        votes: Dict[str, V] = {}
        
        # Process comments in order, so later votes override earlier ones
        for username, comment in comments:
            try:
                vote = self.parse_single_vote(comment)
                votes[username] = vote
            except ValueError:
                # If we can't parse the vote, skip it
                continue
                
        return votes

    @abstractmethod
    def resolve_votes(self, votes: Iterable[V]) -> chess.Move:
        """
        Take all valid votes and determine the winning move.
        
        Args:
            votes: Iterable of parsed votes
            
        Returns:
            The winning chess.Move
            
        Raises:
            ValueError: If no valid winning move can be determined
        """
        pass

    def get_winning_move(self, comments: List[Tuple[str, str]]) -> chess.Move:
        """
        Convenience method that combines parsing and resolution.
        
        Args:
            comments: List of (username, comment) tuples
            
        Returns:
            The winning chess.Move
            
        Raises:
            ValueError: If no valid winning move can be determined
        """
        votes = self.parse_all_votes(comments)
        return self.resolve_votes(votes.values())

    def parse_move(self, move_str: str) -> chess.Move:
        """
        Try to parse a move string in either UCI or algebraic notation.
        
        Args:
            move_str: String representation of a move (e.g., "e2e4" or "e4" or "Nf3")
            
        Returns:
            chess.Move object representing the move
            
        Raises:
            ValueError: If the string cannot be parsed into a valid move
        """
        # Strip whitespace and standardize format
        clean_move = move_str.strip()
        
        # Try parsing as UCI notation first
        try:
            move = chess.Move.from_uci(clean_move)
            if move in self.board.legal_moves:
                return move
        except ValueError:
            pass
        
        # If UCI parsing fails, try algebraic notation
        try:
            move = self.board.parse_san(clean_move)
            if move in self.board.legal_moves:
                return move
        except ValueError:
            pass
            
        # If we get here, neither parsing attempt worked
        raise ValueError(f"Could not parse move: {move_str}")

    def is_valid_move(self, move_str: str) -> bool:
        """
        Check if a move string represents a valid move in the current position.
        Accepts both UCI and algebraic notation.
        
        Args:
            move_str: String representation of a move (e.g., "e2e4" or "e4" or "Nf3")
            
        Returns:
            True if the move is valid, False otherwise
        """
        try:
            self.parse_move(move_str)
            return True
        except ValueError:
            return False