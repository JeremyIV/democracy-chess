from typing import Dict, Iterable, Tuple, List
import chess
import re
from math import sqrt
from voting.vote_parser import VoteParser

class QuadraticVoteParser(VoteParser):
    def parse_single_vote(self, comment: str) -> Dict[chess.Move, float]:
        """
        Parse a comment containing moves with optional weights.
        
        Args:
            comment: A string containing moves and weights
                    (e.g., "e4 5 d4 3 Nf3 -1" or "e4 Nf3")
            
        Returns:
            Dictionary mapping chess.Move objects to their weights
            
        Raises:
            ValueError: If no valid moves could be parsed from the comment
        """
        # Split the comment into tokens
        tokens = comment.strip().split()
        
        # Dictionary to store moves and their weights
        weighted_moves: Dict[chess.Move, float] = {}
        
        i = 0
        while i < len(tokens):
            move_str = tokens[i]
            
            try:
                move = self.parse_move(move_str)
                
                # Look ahead for a weight if there are more tokens
                weight = 1.0  # Default weight
                if i + 1 < len(tokens):
                    try:
                        # Try to parse next token as a number
                        weight = float(tokens[i + 1])
                        i += 1  # Skip the weight token in next iteration
                    except ValueError:
                        # Next token isn't a number, use default weight
                        pass
                
                weighted_moves[move] = weight
                
            except ValueError:
                # Skip invalid moves
                pass
            
            i += 1
        
        # If no valid moves were found, raise ValueError
        if not weighted_moves:
            raise ValueError(f"No valid moves found in comment: {comment}")
        
        # Normalize the weights using quadratic normalization
        return self._normalize_weights(weighted_moves)
    
    def _normalize_weights(self, weighted_moves: Dict[chess.Move, float]) -> Dict[chess.Move, float]:
        """
        Normalize weights so their squared sum equals 1.
        
        Args:
            weighted_moves: Dictionary mapping moves to their weights
            
        Returns:
            Dictionary with normalized weights
        """
        # Calculate the magnitude (square root of sum of squares)
        squared_sum = sum(weight * weight for weight in weighted_moves.values())
        magnitude = sqrt(squared_sum)
        
        # Guard against division by zero
        if magnitude == 0:
            raise ValueError("Cannot normalize zero weights")
            
        # Normalize each weight by dividing by the magnitude
        return {move: weight / magnitude 
                for move, weight in weighted_moves.items()}

    def resolve_votes(self, votes: Iterable[Dict[chess.Move, float]]) -> chess.Move:
        """
        Sum the weighted votes for each move and return the move with the highest total.
        
        Args:
            votes: Iterable of dictionaries mapping chess.Move objects to normalized weights
            
        Returns:
            The chess.Move with the highest total weight
            
        Raises:
            ValueError: If no valid moves were found in any of the votes
        """
        # Aggregate weights for each move
        total_weights: Dict[chess.Move, float] = {}
        
        for vote in votes:
            for move, weight in vote.items():
                if move in total_weights:
                    total_weights[move] += weight
                else:
                    total_weights[move] = weight
        
        if not total_weights:
            raise ValueError("No valid votes to count")
            
        # Find the move(s) with the highest total weight
        max_weight = max(total_weights.values())
        winning_moves = [move for move, weight in total_weights.items() 
                        if weight == max_weight]
        
        # If there's a tie, use the first move in UCI notation order
        # This ensures deterministic behavior
        return min(winning_moves, key=lambda m: m.uci())
    
    def get_colored_moves(self, votes: Iterable[Dict[chess.Move, float]]) -> List[Tuple[chess.Move, str]]:
        """
        Generate colored arrows where opacity scales with the total normalized weight
        each move received. Moves with negative total weights are excluded.
        
        Args:
            votes: Iterable of dictionaries mapping chess.Move objects to normalized weights
            
        Returns:
            List of tuples containing moves and their color codes. Colors are red
            with opacity proportional to the total normalized weight received.
            Moves with negative total weights are excluded.
        """
        # Aggregate weights for each move
        total_weights: Dict[chess.Move, float] = {}
        
        for vote in votes:
            for move, weight in vote.items():
                if move in total_weights:
                    total_weights[move] += weight
                else:
                    total_weights[move] = weight
                    
        if not total_weights:
            return []
            
        # Filter out moves with negative weights
        positive_weights = {move: weight for move, weight in total_weights.items() if weight > 0}
        
        if not positive_weights:
            return []
            
        # Find the maximum weight to normalize opacity
        max_weight = max(positive_weights.values())
        
        # The default chess.svg red arrow color is #882020
        base_color = "#882020"
        
        # Create a move-color tuple for each positively voted move
        colored_moves = []
        for move, weight in positive_weights.items():
            # Calculate opacity (00-FF) based on proportion of max weight
            opacity = int(255 * (weight / max_weight))
            hex_opacity = f"{opacity:02x}"
            
            # Combine base color with calculated opacity
            color = f"{base_color}{hex_opacity}"
            
            colored_moves.append((move, color))
            
        return colored_moves