from voting.vote_parser import VoteParser
import chess
from typing import Iterable, List, Tuple
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
                # Strip whitespace and standardize format
        clean_comment = comment.strip()
        
        # If the comment contains spaces or multiple moves, it's invalid
        if ' ' in clean_comment or ',' in clean_comment:
            raise ValueError(f"FPTP vote must be a single move, got: {comment}")
        
        # Try to parse the move
        return self.parse_move(clean_comment)


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

    def get_colored_moves(self, votes: Iterable[chess.Move]) -> List[Tuple[chess.Move, str]]:
        """
        Generate a list of moves and their associated colors for visualization.
        For FPTP, we use red arrows with opacity proportional to vote share.
        
        Args:
            votes: Iterable of chess.Move objects
            
        Returns:
            List of tuples containing moves and their color codes. Colors are red
            with opacity proportional to the fraction of votes received.
        """
        vote_counts = Counter(votes)
        if not vote_counts:
            return []
            
        # Get the total number of votes
        total_votes = sum(vote_counts.values())
        
        # The default chess.svg red arrow color is #88202080
        # We'll keep the same red color but vary the opacity based on vote share
        base_color = "#882020"
        
        # Create a move-color tuple for each voted move
        colored_moves = []
        for move, count in vote_counts.items():
            # Calculate opacity (00-FF) based on vote proportion
            # Scale directly from 0% to 100% opacity
            vote_fraction = count / total_votes
            opacity = int(255 * vote_fraction)
            hex_opacity = f"{opacity:02x}"
            
            # Combine base color with calculated opacity
            color = f"{base_color}{hex_opacity}"
            
            colored_moves.append((move, color))
            
        return colored_moves

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