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

    def is_valid_move(self, move_str: str) -> bool:
        """
        Check if a move string represents a valid move in the current position.
        
        Args:
            move_str: String representation of a move (e.g., "e2e4")
            
        Returns:
            True if the move is valid, False otherwise
        """
        try:
            move = chess.Move.from_uci(move_str)
            return move in self.board.legal_moves
        except ValueError:
            return False