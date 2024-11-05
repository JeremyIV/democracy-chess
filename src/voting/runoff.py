from typing import List, Tuple
import chess
from collections import Counter, defaultdict
from .vote_parser import VoteParser

class InstantRunoffVoteParser(VoteParser):
    def parse_single_vote(self, comment: str) -> List[chess.Move]:
        """
        Parse a comment containing an ordered list of moves separated by spaces or commas.
        Order represents preference (first move is most preferred).
        
        Args:
            comment: A string containing ordered moves
                    (e.g., "e4, Nf3, d4" means e4 is first choice, Nf3 second, d4 third)
            
        Returns:
            List of chess.Move objects in order of preference
            
        Raises:
            ValueError: If no valid moves could be parsed from the comment
        """
        # Split on both commas and spaces
        move_strings = [m.strip() for m in comment.replace(',', ' ').split()]
        
        # Try to parse each move string, maintaining order
        valid_moves = []
        seen_moves = set()  # To prevent duplicate votes
        
        for move_str in move_strings:
            try:
                move = self.parse_move(move_str)
                # Only add if we haven't seen this move before
                if move not in seen_moves:
                    valid_moves.append(move)
                    seen_moves.add(move)
            except ValueError:
                # Skip invalid moves
                continue
        
        # If no valid moves were found, raise ValueError
        if not valid_moves:
            raise ValueError(f"No valid moves found in comment: {comment}")
            
        return valid_moves

    def resolve_votes(self, votes: List[List[chess.Move]]) -> chess.Move:
        """
        Implement Instant Runoff Voting to determine the winning move.
        
        Args:
            votes: Iterable of ordered lists of chess.Move objects
            
        Returns:
            The chess.Move that wins the IRV process
            
        Raises:
            ValueError: If no valid moves were found in any of the votes
        """
        if not votes:
            raise ValueError("No valid votes to count")
        
        # Convert votes to list for multiple iterations
        remaining_votes = list(votes)
        
        while True:
            # Count first preferences
            first_choices = [vote[0] for vote in remaining_votes if vote]
            if not first_choices:
                raise ValueError("No valid moves remaining")
                
            vote_counts = Counter(first_choices)
            
            # Calculate total votes for majority check
            total_votes = len(first_choices)
            
            # If any move has a majority (>50%), it wins
            for move, count in vote_counts.items():
                if count > total_votes / 2:
                    return move
            
            # No majority - eliminate move(s) with fewest votes
            min_votes = min(vote_counts.values())
            moves_to_eliminate = {move for move, count in vote_counts.items() 
                                if count == min_votes}
            
            # If all remaining moves have the same number of votes,
            # return the lexicographically first move
            if len(moves_to_eliminate) == len(vote_counts):
                return min(vote_counts.keys(), key=lambda m: m.uci())
            
            # Remove eliminated moves from all vote lists
            new_votes = []
            for vote in remaining_votes:
                # Remove eliminated moves and keep order
                updated_vote = [move for move in vote 
                              if move not in moves_to_eliminate]
                if updated_vote:  # Only keep non-empty votes
                    new_votes.append(updated_vote)
            
            remaining_votes = new_votes

    def get_round_results(self, votes: List[List[chess.Move]]) -> List[dict]:
        """
        Get detailed results of each round of IRV.
        Useful for debugging and displaying the voting process.
        
        Returns:
            List of dictionaries containing round-by-round results
        """
        results = []
        remaining_votes = list(votes)
        
        round_num = 1
        while True:
            if not remaining_votes or not any(remaining_votes):
                break
                
            # Count first preferences
            first_choices = [vote[0] for vote in remaining_votes if vote]
            vote_counts = Counter(first_choices)
            total_votes = len(first_choices)
            
            # Record this round's results
            round_result = {
                'round': round_num,
                'total_votes': total_votes,
                'counts': dict(vote_counts),
                'eliminated': set()
            }
            
            # Check for winner
            for move, count in vote_counts.items():
                if count > total_votes / 2:
                    round_result['winner'] = move
                    results.append(round_result)
                    return results
            
            # Find moves to eliminate
            min_votes = min(vote_counts.values())
            moves_to_eliminate = {move for move, count in vote_counts.items() 
                                if count == min_votes}
            
            # If all moves have same count, we're done
            if len(moves_to_eliminate) == len(vote_counts):
                round_result['winner'] = min(vote_counts.keys(), 
                                           key=lambda m: m.uci())
                results.append(round_result)
                return results
            
            round_result['eliminated'] = moves_to_eliminate
            results.append(round_result)
            
            # Update votes for next round
            new_votes = []
            for vote in remaining_votes:
                updated_vote = [move for move in vote 
                              if move not in moves_to_eliminate]
                if updated_vote:
                    new_votes.append(updated_vote)
            
            remaining_votes = new_votes
            round_num += 1
        
        return results
    
    def get_colored_moves(self, votes: List[List[chess.Move]]) -> List[Tuple[chess.Move, str]]:
        """
        Generate colored arrows based only on first-choice votes.
        Opacity scales with the proportion of voters who ranked each move first.
        
        Args:
            votes: List of ordered lists of chess.Move objects representing rankings
            
        Returns:
            List of tuples containing moves and their color codes. Colors are red
            with opacity proportional to first-choice votes received.
        """
        if not votes:
            return []
        
        # Count first choices only
        first_choices = [vote[0] for vote in votes if vote]  # Skip empty votes
        if not first_choices:
            return []
            
        vote_counts = Counter(first_choices)
        total_votes = len(first_choices)
        
        # Base color for arrows
        base_color = "#882020"
        
        # Create move-color pairs
        colored_moves = []
        for move, count in vote_counts.items():
            # Calculate opacity based on proportion of first-choice votes
            opacity = int(255 * (count / total_votes))
            hex_opacity = f"{opacity:02x}"
            
            color = f"{base_color}{hex_opacity}"
            colored_moves.append((move, color))
        
        return colored_moves