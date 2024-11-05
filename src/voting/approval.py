from typing import Set, Iterable, List, Tuple
import chess
from collections import Counter
from voting.vote_parser import VoteParser

class ApprovalVoteParser(VoteParser):
    def parse_single_vote(self, comment: str) -> Set[chess.Move]:
        """
        Parse a comment containing a list of moves separated by spaces or commas.
        
        Args:
            comment: A string containing space/comma separated moves
                    (e.g., "e4, Nf3, d4" or "e2e4 g1f3")
            
        Returns:
            Set of chess.Move objects representing all valid moves in the vote
            
        Raises:
            ValueError: If no valid moves could be parsed from the comment
        """
        # Split on both commas and spaces
        move_strings = [m.strip() for m in comment.replace(',', ' ').split()]
        
        # Try to parse each move string
        valid_moves = set()
        for move_str in move_strings:
            try:
                move = self.parse_move(move_str)
                valid_moves.add(move)
            except ValueError:
                # Skip invalid moves
                continue
        
        # If no valid moves were found, raise ValueError
        if not valid_moves:
            raise ValueError(f"No valid moves found in comment: {comment}")
            
        return valid_moves

    def resolve_votes(self, votes: Set[chess.Move]) -> chess.Move:
        """
        Count the total approvals for each move and return the most approved move.
        
        Args:
            votes: Iterable of sets of chess.Move objects
            
        Returns:
            The chess.Move with the most approvals
            
        Raises:
            ValueError: If no valid moves were found in any of the votes
        """
        # Flatten the sets of votes into a single list
        all_votes = [move for vote_set in votes for move in vote_set]
        
        if not all_votes:
            raise ValueError("No valid votes to count")
            
        # Count occurrences of each move
        vote_counts = Counter(all_votes)
        
        # Find the move(s) with the most votes
        max_votes = max(vote_counts.values())
        winning_moves = [move for move, count in vote_counts.items() 
                        if count == max_votes]
        
        # If there's a tie, use the first move in UCI notation order
        # This ensures deterministic behavior
        return min(winning_moves, key=lambda m: m.uci())
    
    def get_colored_moves(self, votes: Iterable[Set[chess.Move]]) -> List[Tuple[chess.Move, str]]:
        """
        Generate a list of moves and their associated colors for visualization.
        For approval voting, we use red arrows with opacity proportional to 
        approval count.
        
        Args:
            votes: Iterable of sets of approved chess.Move objects
            
        Returns:
            List of tuples containing moves and their color codes. Colors are red
            with opacity proportional to the approval count.
        """
        # Flatten the sets of votes into a single list
        all_votes = [move for vote_set in votes for move in vote_set]
        
        if not all_votes:
            return []
            
        # Count approvals for each move
        approval_counts = Counter(all_votes)
        
        # Find the maximum approval count for scaling
        max_approvals = sum(approval_counts.values())
        
        # The default chess.svg red arrow color is #882020
        base_color = "#882020"
        
        # Create a move-color tuple for each voted move
        colored_moves = []
        for move, count in approval_counts.items():
            # Calculate opacity (00-FF) based on proportion of max approvals
            approval_proportion = count / max_approvals
            opacity = int(255 * approval_proportion)
            hex_opacity = f"{opacity:02x}"
            
            # Combine base color with calculated opacity
            color = f"{base_color}{hex_opacity}"
            
            colored_moves.append((move, color))
            
        return colored_moves