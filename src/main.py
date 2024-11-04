import argparse
import chess
import chess.engine
import chess.svg
import pygame
import cairosvg
import io
from PIL import Image
import time
import sys
from typing import Union, Optional, Literal, Tuple
import random
import traceback  

# Import our modules
from twitch import create_twitch_chat
from voting.fptp import FPTPVoteParser
from voting.approval import ApprovalVoteParser
from voting.runoff import InstantRunoffVoteParser
from mock_twitch import MockTwitchChat
from mock_stockfish import MockStockfish
from game_logger import GameLogger, get_last_game_info
from stockfish_wrapper import create_engine, DIFFICULTY_LEVELS

# Define valid voting methods
VOTING_METHODS = {
    'fptp': FPTPVoteParser,
    'approval': ApprovalVoteParser,
    'runoff': InstantRunoffVoteParser
}

VotingMethod = Literal['fptp', 'approval', 'runoff']

def determine_next_game_params(log_dir: str) -> Tuple[VotingMethod, int]:
    """
    Determine the voting method and difficulty for the next game based on history.
    
    Args:
        log_dir: Directory containing game logs
        
    Returns:
        Tuple of (voting_method, difficulty_level)
    """
    # Randomly choose next voting method
    voting_method = random.choice(list(VOTING_METHODS.keys()))
    
    # Get info about the last game with this voting method
    last_game_info = get_last_game_info(log_dir, voting_method)
    
    if last_game_info is None:
        # No previous games with this method, start at default difficulty
        return voting_method, 2
    
    last_difficulty, chat_won = last_game_info
    
    # Adjust difficulty based on outcome
    if chat_won:
        # Increase difficulty, but don't exceed maximum
        new_difficulty = min(last_difficulty + 1, len(DIFFICULTY_LEVELS))
    else:
        # Decrease difficulty, but don't go below 1
        new_difficulty = max(last_difficulty - 1, 1)
        
    return voting_method, new_difficulty
def render_game_state(
    screen: pygame.Surface,
    board: chess.Board,
    time_remaining: float,
    vote_time: int,
    voting_method: str
) -> None:
    """
    Render the current game state including chess board and timer.
    
    Args:
        screen: Pygame surface to render on
        board: Current chess board state
        time_remaining: Seconds remaining in current vote
        vote_time: Total voting time per turn
        voting_method: Current voting method being used
    """
    # Clear screen
    screen.fill((255, 255, 255))
    
    # Render chess board
    svg_data = chess.svg.board(board=board).encode('UTF-8')
    png_data = cairosvg.svg2png(bytestring=svg_data)
    image = Image.open(io.BytesIO(png_data))
    py_image = pygame.image.fromstring(image.tobytes(), image.size, image.mode)
    py_image = pygame.transform.scale(py_image, (800, 800))
    screen.blit(py_image, (0, 0))
    
    # Render timer and info panel
    font = pygame.font.Font(None, 48)
    
    # Timer
    time_text = font.render(f"Next Move: {int(time_remaining)}", True, (0, 0, 0))
    screen.blit(time_text, (820, 50))
    
    # Progress bar
    progress_height = 20
    progress_width = 200
    progress_x = 820
    progress_y = 100
    
    # Draw progress bar background
    pygame.draw.rect(screen, (200, 200, 200), (progress_x, progress_y, progress_width, progress_height))
    
    # Draw progress bar fill
    fill_width = int((time_remaining / vote_time) * progress_width)
    pygame.draw.rect(screen, (0, 255, 0), (progress_x, progress_y, fill_width, progress_height))
    
    # Voting method info
    method_label = font.render("Voting:", True, (0, 0, 0))
    method_text = font.render(voting_method.upper(), True, (0, 0, 0))
    screen.blit(method_label, (820, 150))
    screen.blit(method_text, (820, 200))
    
    pygame.display.flip()

def play_game(
    screen: pygame.Surface,
    mock: bool,
    mock_chat_path: str,
    mock_stockfish_path: str,
    vote_time: int,
    log_dir: str,
    difficulty: int,
    game_number: int,
    voting_method: VotingMethod,
    twitch_chat=None
) -> None:
    """
    Play a single game of Democracy Chess.
    
    Args:
        [Previous args documentation remains the same...]
    """
    logger = GameLogger(log_dir, game_number, voting_method, difficulty)
    board = chess.Board()
    engine = create_engine(mock, mock_stockfish_path, difficulty)
    VoteParserClass = VOTING_METHODS[voting_method]
    vote_parser = VoteParserClass(board)

    try:
        turn_number = 1
        print(f"\nStarting game {game_number} with {voting_method.upper()} voting")
        
        while not board.is_game_over():
            print(f"\nGame {game_number}, Turn {turn_number} - Waiting {vote_time} seconds for votes...")
            print(f"Voting method: {voting_method.upper()}")
            
            vote_start_time = time.time()
            collected_messages = []
            
            # Voting period loop
            while True:
                current_time = time.time()
                elapsed_time = current_time - vote_start_time
                
                if elapsed_time >= vote_time:
                    break
                    
                time_remaining = vote_time - elapsed_time
                
                # Handle events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        raise KeyboardInterrupt
                
                # Collect any new messages
                new_messages = twitch_chat.get_chat()
                if new_messages:
                    collected_messages.extend(new_messages)
                
                # Render current state
                render_game_state(
                    screen=screen,
                    board=board,
                    time_remaining=time_remaining,
                    vote_time=vote_time,
                    voting_method=voting_method
                )
                
                # Small sleep to prevent excessive CPU usage
                time.sleep(0.1)
            
            if not collected_messages:
                print("No votes received in this period, continuing...")
                continue

            try:
                winning_move = vote_parser.get_winning_move(collected_messages)
                print(f"\nVotes received from {len(collected_messages)} users")
                print(f"Winning move: {winning_move.uci()}")

                # Make Twitch's move
                board.push(winning_move)
                render_game_state(screen, board, 0, vote_time, voting_method)

                # Get and make Stockfish's move
                result = engine.play(board)
                board.push(result)
                print(f"Stockfish played: {result.uci()}")
                render_game_state(screen, board, vote_time, vote_time, voting_method)

                # Log the complete turn
                logger.log_turn(
                    turn_number=turn_number,
                    chat_messages=collected_messages,
                    twitch_move=winning_move.uci(),
                    stockfish_move=result.uci()
                )
                turn_number += 1

            except ValueError as e:
                print(f"Error processing votes: {e}")
                continue

        # Game is over
        render_game_state(screen, board, 0, vote_time, voting_method)
        outcome = board.outcome()
        logger.log_outcome(outcome)
        
        print("\nGame Over!")
        winner = "Twitch" if outcome.winner else "Stockfish" if outcome.winner is False else "Draw"
        print(f"Winner: {winner}")
        print(f"Termination: {outcome.termination.name}")
        print(f"Game log saved to: {logger.log_file}")

    finally:
        engine.quit()

def main():
    parser = argparse.ArgumentParser(description='Democracy Chess - Chess played by Twitch chat')
    parser.add_argument('--mock', action='store_true', help='Use mock implementations instead of real APIs')
    parser.add_argument('--mock-chat-path', default='mock/chat.csv', help='Path to mock chat CSV file')
    parser.add_argument('--mock-stockfish-path', default='mock/stockfish.csv', help='Path to mock Stockfish CSV file')
    parser.add_argument('--vote-time', type=int, default=30, help='Seconds to wait for votes')
    parser.add_argument('--log-dir', default='logs', help='Directory to store game logs')
    args = parser.parse_args()

    if args.mock:
        twitch_chat = MockTwitchChat(mock_chat_path)
    else:
        twitch_chat = create_twitch_chat()

    pygame.init()
    # Increased window width to accommodate timer and info panel
    screen = pygame.display.set_mode((1100, 800))

    try:
        game_number = 1
        while True:
            try:
                voting_method, difficulty = determine_next_game_params(args.log_dir)
                pygame.display.set_caption(f"Democracy Chess - {voting_method.upper()} Voting (Difficulty {difficulty})")
                
                print(f"\nStarting game {game_number}")
                print(f"Voting method: {voting_method.upper()}")
                print(f"Difficulty level: {difficulty}")
                
                play_game(
                    screen=screen,
                    mock=args.mock,
                    mock_chat_path=args.mock_chat_path,
                    mock_stockfish_path=args.mock_stockfish_path,
                    vote_time=args.vote_time,
                    log_dir=args.log_dir,
                    difficulty=difficulty,
                    game_number=game_number,
                    voting_method=voting_method,
                    twitch_chat=twitch_chat
                )
                
                game_number += 1
                print("\nPreparing next game...")
                time.sleep(5)
                
            except KeyboardInterrupt:
                raise
            except Exception as e:
                print(f"Error during game {game_number}: {e}")
                traceback.print_exc()
                print("Starting new game...")
                time.sleep(5)
                continue

    except KeyboardInterrupt:
        print("\nProgram terminated by user")
    finally:
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()
