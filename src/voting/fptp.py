from voting.vote_parser import VoteParser
import chess
from typing import Iterable
from collections import Counter

class FPTPVoteParser(VoteParser):
    def parse_single_vote(self, comment: str) -> chess.Move:
        """
        Parse a single comment into a chess move. In FPTP, each vote should be
        a single valid move in UCI format (e.g., "e2e4").
        
        Args:
            comment: A string containing a user's comment/vote
            
        Returns:
            chess.Move object representing the voted move
            
        Raises:
            ValueError: If the comment cannot be parsed into a valid move
        """
        # Strip whitespace and convert to lowercase
        clean_comment = comment.strip().lower()
        
        # If the comment contains spaces or multiple moves, it's invalid
        if ' ' in clean_comment or ',' in clean_comment:
            raise ValueError(f"FPTP vote must be a single move, got: {comment}")
            
        # Try to parse as UCI move
        try:
            move = chess.Move.from_uci(clean_comment)
            if move in self.board.legal_moves:
                return move
            else:
                raise ValueError(f"Illegal move: {clean_comment}")
        except ValueError:
            raise ValueError(f"Could not parse move: {clean_comment}")

    def resolve_votes(self, votes: Iterable[chess.Move]) -> chess.Move:
        """
        Determine the winning move by counting votes and selecting the move
        with the most votes. Ties are broken by selecting the first move
        that achieved the winning vote count.
        
        Args:
            votes: Iterable of chess.Move objects
            
        Returns:
            The chess.Move that received the most votes
            
        Raises:
            ValueError: If there are no valid votes
        """
        if not votes:
            raise ValueError("No valid votes to count")
            
        # Count votes for each move
        vote_counts = Counter(votes)
        
        if not vote_counts:
            raise ValueError("No valid votes to count")
            
        # Find move(s) with the most votes
        max_votes = max(vote_counts.values())
        winning_moves = [move for move, count in vote_counts.items() 
                        if count == max_votes]
                        
        # In case of a tie, take the first move that reached the winning count
        # We can do this because Counter maintains insertion order
        return winning_moves[0]

    def get_vote_counts(self, votes: Iterable[chess.Move]) -> dict[chess.Move, int]:
        """
        Get a dictionary of vote counts for each move. Useful for displaying
        voting results.
        
        Args:
            votes: Iterable of chess.Move objects
            
        Returns:
            Dictionary mapping moves to their vote counts
        """
        return dict(Counter(votes))

    def format_results(self, votes: Iterable[chess.Move]) -> str:
        """
        Create a human-readable string showing the voting results.
        
        Args:
            votes: Iterable of chess.Move objects
            
        Returns:
            A formatted string showing vote counts for each move
        """
        vote_counts = self.get_vote_counts(votes)
        if not vote_counts:
            return "No valid votes cast"
            
        # Sort moves by vote count (descending) and then alphabetically
        sorted_moves = sorted(vote_counts.items(),
                            key=lambda x: (-x[1], x[0].uci()),
                            reverse=False)
        
        # Format each line
        lines = [f"{move.uci()}: {count} vote{'s' if count != 1 else ''}"
                for move, count in sorted_moves]
        
        return "\n".join(lines)